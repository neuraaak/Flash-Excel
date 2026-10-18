import { api } from '../api.js';

export default {
  name: 'FileLoader',
  props: {
    fileInfo:     { type: Object, default: null },
    templateFile: { type: String, default: '' },
  },
  emits: ['load', 'clear'],
  inject: ['i18n'],
  data() {
    return { fileIconUrl: '' };
  },
  watch: {
    fileInfo: {
      immediate: true,
      async handler(fileInfo) {
        this.fileIconUrl = '';
        if (fileInfo) this.fileIconUrl = await api.getFileTypeIconUri(fileInfo.file_type);
      },
    },
  },
  computed: {
    t() { return this.i18n.t; },
  },
  methods: {
    onClear(e) { e.stopPropagation(); this.$emit('clear'); },
    sizeLabel(b) {
      if (b < 1024) return `${b} B`;
      if (b < 1048576) return `${(b / 1024).toFixed(1)} KB`;
      return `${(b / 1048576).toFixed(1)} MB`;
    },
  },
  template: `
    <div v-if="fileInfo" class="file-loaded">
      <div class="file-loaded__icon">
        <img v-if="fileIconUrl" class="file-type-icon" :src="fileIconUrl" alt="">
      </div>
      <div class="file-loaded__meta">
        <div class="file-loaded__name">{{ fileInfo.file_name }}</div>
        <div class="file-loaded__size">{{ sizeLabel(fileInfo.size_bytes) }}</div>
      </div>
      <button class="icon-btn" @click="onClear" :title="t('file.clear')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M6 6l12 12M18 6L6 18"/>
        </svg>
      </button>
    </div>

    <div v-else-if="templateFile" class="file-template">
      <div class="file-template__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <path d="M14 2v6h6M12 18v-6M9 15h6"/>
        </svg>
      </div>
      <div class="file-template__meta">
        <div class="file-template__name">{{ templateFile }}</div>
        <div class="file-template__hint">{{ t('file.template_hint') }}</div>
      </div>
      <button class="btn btn-ghost" style="flex:0 0 auto;font-size:var(--fs-sm);" @click="$emit('load')">
        {{ t('file.load') }}
      </button>
    </div>

    <div v-else class="dropzone" @click="$emit('load')">
      <span class="dz-ico">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 16V8M9 11l3-3 3 3"/>
          <path d="M20 16.5A4.5 4.5 0 0 0 18 8h-1.26A7 7 0 1 0 4 14.9"/>
        </svg>
      </span>
      <span>{{ t('file.load') }}</span>
    </div>
  `,
};
