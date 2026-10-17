import { api }      from '../api.js';
import { i18n }     from '../i18n.js';
import LucideIcon   from './LucideIcon.js';

const THEME_TOKENS = [
  'surface_sunken', 'surface_base', 'surface_raised',
  'surface_overlay', 'surface_floating', 'border_subtle',
  'accent_brand', 'text_primary', 'text_secondary', 'text_on_accent',
  'overlay_scrim',
  'semantic_success', 'semantic_warning', 'semantic_error', 'semantic_info',
];

export default {
  name: 'SettingsModal',
  components: { LucideIcon },
  inject: ['i18n'],
  emits: ['close'],

  data() {
    return {
      palette: 'blue-gray',
      mode: 'dark',
      locale: 'en',
      themes: {},
    };
  },

  computed: {
    t() { return this.i18n.t; },
    // Derived from the catalogue, so a palette added to theme.config.yaml
    // shows up here with no JS change. Swatches read the live tokens of the
    // mode being previewed instead of a second, hand-copied set of hexes.
    paletteCards() {
      return Object.entries(this.themes).map(([key, palette]) => {
        const tokens = palette?.[this.mode] ?? palette?.dark ?? {};
        return {
          key,
          label: palette?.label ?? key,
          preview: {
            surface: tokens.surface_raised,
            accent: tokens.accent_brand,
            text: tokens.text_primary,
          },
        };
      });
    },
  },

  async mounted() {
    const [cfgRes, themesRes] = await Promise.all([
      api.getAppConfig().catch(() => null),
      api.getThemes().catch(() => null),
    ]);
    if (cfgRes?.appearance) {
      this.palette = cfgRes.appearance.palette;
      this.mode = cfgRes.appearance.mode;
    }
    this.locale = cfgRes?.locale ?? 'en';
    if (themesRes) this.themes = themesRes;
  },

  methods: {
    async setPalette(key) {
      this.palette = key;
      this._applyTheme();
      await api.saveAppConfig(this.palette, this.mode, this.locale).catch(() => { });
    },
    async setMode(m) {
      this.mode = m;
      this._applyTheme();
      await api.saveAppConfig(this.palette, this.mode, this.locale).catch(() => { });
    },
    async setLanguage(code) {
      this.locale = code;
      i18n.setLocale(code);
      await api.saveAppConfig(this.palette, this.mode, code).catch(() => { });
    },
    _applyTheme() {
      const tokens = this.themes[this.palette]?.[this.mode];
      if (!tokens) return;
      const root = document.documentElement;
      for (const key of THEME_TOKENS) {
        if (tokens[key]) root.style.setProperty(`--${key}`, tokens[key]);
      }
    },
    closeOnOverlay(e) {
      if (e.target === e.currentTarget) this.$emit('close');
    },
  },

  template: `
    <div class="settings-overlay" @click="closeOnOverlay" @keydown.esc="$emit('close')">
      <div class="settings-modal" role="dialog" aria-modal="true" :aria-label="t('settings.title')">

        <div class="settings-head">
          <span class="settings-head-title">
            <LucideIcon name="settings" :size="15" :stroke="1.8" />
            {{ t('settings.title') }}
          </span>
          <button class="btn-icon" @click="$emit('close')" aria-label="Close">
            <LucideIcon name="x" :size="14" :stroke="2" />
          </button>
        </div>

        <div class="settings-body">

          <!-- Apparence -->
          <div class="settings-section">
            <div class="settings-section-label">{{ t('settings.appearance') }}</div>

            <div class="settings-field">
              <div class="settings-field-label">{{ t('settings.palette') }}</div>
              <div class="palette-grid">
                <button
                  v-for="p in paletteCards"
                  :key="p.key"
                  class="palette-card"
                  :class="{ active: palette === p.key }"
                  @click="setPalette(p.key)"
                >
                  <div class="palette-card-swatches">
                    <span class="palette-card-swatch" :style="{ background: p.preview.surface }"></span>
                    <span class="palette-card-swatch" :style="{ background: p.preview.accent  }"></span>
                    <span class="palette-card-swatch" :style="{ background: p.preview.text    }"></span>
                  </div>
                  <div class="palette-card-name">{{ p.label }}</div>
                  <div v-if="palette === p.key" class="palette-card-check">
                    <LucideIcon name="check" :size="10" :stroke="2.5" />
                  </div>
                </button>
              </div>
            </div>

            <div class="settings-field">
              <div class="settings-field-label">{{ t('settings.mode') }}</div>
              <div class="seg settings-mode-seg">
                <button :class="{ active: mode === 'dark' }" @click="setMode('dark')">
                  <LucideIcon name="moon" :size="13" :stroke="1.8" />
                  {{ t('settings.mode_dark') }}
                </button>
                <button :class="{ active: mode === 'light' }" @click="setMode('light')">
                  <LucideIcon name="sun" :size="13" :stroke="1.8" />
                  {{ t('settings.mode_light') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Langue -->
          <div class="settings-section">
            <div class="settings-section-label">{{ t('settings.language') }}</div>
            <div class="settings-field">
              <div class="seg settings-mode-seg">
                <button :class="{ active: locale === 'en' }" @click="setLanguage('en')">
                  {{ t('settings.lang_en') }}
                </button>
                <button :class="{ active: locale === 'fr' }" @click="setLanguage('fr')">
                  {{ t('settings.lang_fr') }}
                </button>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  `,
};
