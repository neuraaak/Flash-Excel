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
      csvSeparator: 'auto',
      csvDecimal: 'auto',
      presetSources: [],
      showSourceDialog: false,
      sourceDialogIndex: null,
      sourceDraft: { label: '', path: '' },
      sourceError: '',
      sourceSaving: false,
      deleteSourceIndex: null,
      deleteError: '',
      SEPARATORS: ['auto', 'semicolon', 'comma', 'tab'],
      DECIMALS: ['auto', 'comma', 'dot'],
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
    this.csvSeparator = cfgRes?.csv?.separator ?? 'auto';
    this.csvDecimal = cfgRes?.csv?.decimal ?? 'auto';
    this.presetSources = cfgRes?.presets?.sources ?? [];
    if (themesRes) this.themes = themesRes;
  },

  methods: {
    async setPalette(key) {
      this.palette = key;
      this._applyTheme();
      await this.saveSettings();
    },
    async setMode(m) {
      this.mode = m;
      this._applyTheme();
      await this.saveSettings();
    },
    async setLanguage(code) {
      this.locale = code;
      i18n.setLocale(code);
      await this.saveSettings();
    },
    async setCsvSeparator(token) {
      this.csvSeparator = token;
      await this.saveSettings();
    },
    async setCsvDecimal(token) {
      this.csvDecimal = token;
      await this.saveSettings();
    },
    openSourceDialog(index = null) {
      this.sourceDialogIndex = index;
      this.sourceDraft = index === null
        ? { label: '', path: '' }
        : { ...this.presetSources[index] };
      this.sourceError = '';
      this.showSourceDialog = true;
    },
    closeSourceDialog() {
      if (!this.sourceSaving) this.showSourceDialog = false;
    },
    async browsePresetSource() {
      try {
        const result = await api.openFolderDialog();
        if (result?.folder) this.sourceDraft.path = result.folder;
      } catch (e) {
        this.sourceError = this.t('settings.preset_source_browse_error', { error: e.message });
      }
    },
    async confirmPresetSource() {
      const source = {
        label: this.sourceDraft.label.trim(),
        path: this.sourceDraft.path.trim(),
      };
      if (!source.label || !source.path) {
        this.sourceError = this.t('settings.preset_source_required');
        return;
      }
      const sources = [...this.presetSources];
      if (this.sourceDialogIndex === null) sources.push(source);
      else sources[this.sourceDialogIndex] = source;
      this.sourceSaving = true;
      this.sourceError = '';
      try {
        await this.persistSettings(sources);
        this.presetSources = sources;
        this.showSourceDialog = false;
      } catch (e) {
        this.sourceError = this.t('settings.preset_source_save_error', { error: e.message });
      } finally {
        this.sourceSaving = false;
      }
    },
    removePresetSource(index) {
      this.deleteSourceIndex = index;
      this.deleteError = '';
    },
    cancelDeletePresetSource() {
      this.deleteSourceIndex = null;
    },
    async confirmDeletePresetSource() {
      const sources = this.presetSources.filter((_, index) => index !== this.deleteSourceIndex);
      try {
        await this.persistSettings(sources);
        this.presetSources = sources;
        this.deleteSourceIndex = null;
      } catch (e) {
        this.deleteError = this.t('settings.preset_source_delete_error', { error: e.message });
      }
    },
    persistSettings(sources = this.presetSources) {
      return api.saveAppConfig(this.palette, this.mode, this.locale, this.csvSeparator, this.csvDecimal, sources);
    },
    saveSettings() {
      return this.persistSettings().catch(() => { });
    },
    closeOnOverlay(e) {
      if (e.target === e.currentTarget) this.$emit('close');
    },
    _applyTheme() {
      const tokens = this.themes[this.palette]?.[this.mode];
      if (!tokens) return;
      const root = document.documentElement;
      for (const key of THEME_TOKENS) {
        if (tokens[key]) root.style.setProperty(`--${key}`, tokens[key]);
      }
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

          <!-- CSV -->
          <div class="settings-section">
            <div class="settings-section-label">{{ t('settings.csv') }}</div>

            <div class="settings-field">
              <div class="settings-field-label">{{ t('settings.csv_separator') }}</div>
              <div class="seg settings-mode-seg">
                <button
                  v-for="opt in SEPARATORS"
                  :key="opt"
                  :class="{ active: csvSeparator === opt }"
                  @click="setCsvSeparator(opt)"
                >
                  {{ t('settings.csv_sep_' + opt) }}
                </button>
              </div>
            </div>

            <div class="settings-field">
              <div class="settings-field-label">{{ t('settings.csv_decimal') }}</div>
              <div class="seg settings-mode-seg">
                <button
                  v-for="opt in DECIMALS"
                  :key="opt"
                  :class="{ active: csvDecimal === opt }"
                  @click="setCsvDecimal(opt)"
                >
                  {{ t('settings.csv_dec_' + opt) }}
                </button>
              </div>
            </div>

            <div class="settings-hint">{{ t('settings.csv_hint') }}</div>
          </div>

          <div class="settings-section">
            <div class="settings-section-label">{{ t('settings.preset_sources') }}</div>
            <div class="settings-hint">{{ t('settings.preset_sources_hint') }}</div>
            <div v-if="!presetSources.length" class="preset-sources-empty">{{ t('settings.preset_sources_empty') }}</div>
            <div v-for="(source, index) in presetSources" :key="index" class="preset-source-card">
              <div class="preset-source-details">
                <div class="preset-source-name">{{ source.label }}</div>
                <div class="preset-source-path" :title="source.path">{{ source.path }}</div>
              </div>
              <div class="preset-source-actions">
                <button type="button" class="btn preset-source-edit" @click="openSourceDialog(index)"
                  :aria-label="t('settings.edit_preset_source') + ': ' + source.label">
                  {{ t('settings.edit_preset_source') }}
                </button>
                <button type="button" class="icon-btn preset-source-remove" @click="removePresetSource(index)"
                  :title="t('settings.remove_preset_source')" :aria-label="t('settings.remove_preset_source') + ': ' + source.label">
                  <LucideIcon name="trash" :size="15" />
                </button>
              </div>
            </div>
            <button type="button" class="btn preset-source-add" @click="openSourceDialog()">
              <LucideIcon name="plus" :size="15" />
              {{ t('settings.add_preset_source') }}
            </button>
          </div>

        </div>

      </div>
    </div>

    <teleport to="body">
      <div v-if="showSourceDialog" class="modal-overlay" @click.self="closeSourceDialog" @keydown.esc.stop="closeSourceDialog">
        <div class="modal source-dialog" role="dialog" aria-modal="true"
          :aria-label="t(sourceDialogIndex === null ? 'settings.add_preset_source' : 'settings.edit_preset_source')">
          <div class="modal-head">
            <h3>{{ t(sourceDialogIndex === null ? 'settings.add_preset_source' : 'settings.edit_preset_source') }}</h3>
            <button type="button" class="btn-icon" @click="closeSourceDialog" :aria-label="t('modal.cancel')">
              <LucideIcon name="x" :size="14" />
            </button>
          </div>
          <form class="source-dialog-form" @submit.prevent="confirmPresetSource">
            <div class="modal-body">
              <label class="source-form-field">
                <span>{{ t('settings.preset_source_label') }}</span>
                <input class="input" v-model="sourceDraft.label" required autofocus
                  :placeholder="t('settings.preset_source_label_example')" />
              </label>
              <label class="source-form-field">
                <span>{{ t('settings.preset_source_path') }}</span>
                <span class="source-form-path">
                  <input class="input" v-model="sourceDraft.path" required
                    :placeholder="t('settings.preset_source_path_example')" />
                  <button type="button" class="icon-btn" @click="browsePresetSource"
                    :title="t('settings.browse_preset_source')" :aria-label="t('settings.browse_preset_source')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
                  </button>
                </span>
              </label>
              <p class="settings-hint">{{ t('settings.preset_source_read_only_hint') }}</p>
              <p v-if="sourceError" class="source-dialog-error" role="alert">{{ sourceError }}</p>
            </div>
            <div class="modal-foot">
              <button type="button" class="btn" @click="closeSourceDialog" :disabled="sourceSaving">{{ t('modal.cancel') }}</button>
              <button type="submit" class="btn primary" :disabled="sourceSaving">{{ t('toolbar.save') }}</button>
            </div>
          </form>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="deleteSourceIndex !== null" class="modal-overlay" @click.self="cancelDeletePresetSource" @keydown.esc.stop="cancelDeletePresetSource">
        <div class="modal source-delete-dialog" role="alertdialog" aria-modal="true" :aria-label="t('settings.delete_preset_source_title')">
          <div class="modal-head"><h3>{{ t('settings.delete_preset_source_title') }}</h3></div>
          <div class="modal-body">
            <p>{{ t('settings.delete_preset_source_confirm', { label: presetSources[deleteSourceIndex]?.label }) }}</p>
            <p v-if="deleteError" class="source-dialog-error" role="alert">{{ deleteError }}</p>
          </div>
          <div class="modal-foot">
            <button type="button" class="btn" @click="cancelDeletePresetSource">{{ t('modal.cancel') }}</button>
            <button type="button" class="btn btn-danger" @click="confirmDeletePresetSource">{{ t('toolbar.delete') }}</button>
          </div>
        </div>
      </div>
    </teleport>
  `,
};
