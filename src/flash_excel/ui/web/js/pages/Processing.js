import { api } from '../api.js';
import { stepLabel } from '../steps-registry.js';
import ExecutionModal from '../components/ExecutionModal.js';

const LEVEL_LABEL = { info: 'INFO', ok: 'OK', step: 'STEP', warn: 'WARN', err: 'ERROR' };

export default {
  name: 'ProcessingPage',
  components: { ExecutionModal },
  inject: ['showToast', 'i18n'],

  data() {
    return {
      LEVEL_LABEL,
      presets: [],
      selectedPresetPath: '',
      selectedPreset: null,   // full preset dict from api.loadPreset
      files: [],        // [{ path, file_name, size_bytes, columns, ... }]
      // Per-file run state, parallel to files[] and indexed by the
      // file_index every backend event carries.
      fileStates: [],   // [{ status, progress }]
      outputConfig: {
        format: 'keep',
        folder: '',
        pattern: '{name}_clean',
        error_mode: 'skip',
      },
      runState: 'idle',    // 'idle' | 'running' | 'done' | 'error' | 'stopped'
      stats: { rows_out: 0, warnings: 0, errors: 0, elapsed_s: null },
      logs: [],
      consoleCollapsed: false,
      consoleFilter: 'all',
      autoScroll: true,
      previewOpen: false,
      previewLoading: false,
      previewData: null,
      previewError: '',
      previewFileName: '',
      executionDraft: null,
      fileTypeIcons: {},
    };
  },

  computed: {
    STATUS_LABEL() {
      const t = this.i18n.t.bind(this.i18n);
      return {
        pending: t('proc.status_pending'),
        running: t('proc.status_running'),
        done: t('proc.status_done'),
        error: t('proc.status_error'),
        skipped: t('proc.status_skipped'),
      };
    },
    ERROR_OPTS() {
      const t = this.i18n.t.bind(this.i18n);
      return [
        { value: 'skip', label: t('proc.err_skip'), sub: t('proc.err_skip_sub') },
        { value: 'stop', label: t('proc.err_stop'), sub: t('proc.err_stop_sub') },
        { value: 'ignore', label: t('proc.err_ignore'), sub: t('proc.err_ignore_sub') },
      ];
    },
    totalSteps() { return this.selectedPreset?.steps?.length ?? 0; },
    stepNames() { return this.selectedPreset?.steps?.map(s => s.action) ?? []; },
    canRun() { return this.files.length > 0 && !!this.selectedPresetPath && this.runState !== 'running' && !this.previewLoading; },
    // The footer bar covers the whole batch, not the file in flight.
    overallProgress() {
      if (!this.fileStates.length) return 0;
      const sum = this.fileStates.reduce((acc, f) => acc + f.progress, 0);
      return Math.round(sum / this.fileStates.length);
    },
    filteredLogs() {
      const f = this.consoleFilter;
      if (f === 'all') return this.logs;
      if (f === 'step') return this.logs.filter(l => l.level === 'step');
      if (f === 'err') return this.logs.filter(l => l.level === 'err');
      if (f === 'warn') return this.logs.filter(l => l.level === 'warn' || l.level === 'err');
      return this.logs.filter(l => ['info', 'ok'].includes(l.level));
    },
  },

  mounted() {
    window.flashEvent = (type, data) => this.onFlashEvent(type, data);
    this.loadPresets();
    this.loadDefaultOutputFolder();
    this.loadFileTypeIcons();
  },

  beforeUnmount() {
    delete window.flashEvent;
  },

  methods: {
    async loadFileTypeIcons() {
      const [csv, excel] = await Promise.all([
        api.getFileTypeIconUri('csv'),
        api.getFileTypeIconUri('excel'),
      ]);
      this.fileTypeIcons = { csv, excel };
    },

    fileIconUrl(file) {
      return this.fileTypeIcons[this.fileExt(file.file_name) === 'csv' ? 'csv' : 'excel'];
    },

    openExecutionSettings() {
      if (!this.canRun) return;
      this.executionDraft = {
        presetPath: this.selectedPresetPath,
        files: this.files.map(file => ({ path: file.path, file_name: file.file_name })),
        outputConfig: { ...this.outputConfig },
      };
    },

    async previewPreset() {
      if (!this.canRun) return;
      const file = this.files[0];
      this.previewFileName = file.file_name;
      this.previewData = null;
      this.previewError = '';
      this.previewOpen = true;
      this.previewLoading = true;
      this.$nextTick(() => this.$refs.previewClose?.focus());
      try {
        this.previewData = await api.previewPreset(this.selectedPresetPath, file.path);
      } catch (e) {
        this.previewError = e.message;
      } finally {
        this.previewLoading = false;
      }
    },

    async browseFolder() {
      try {
        const res = await api.openFolderDialog();
        if (!res.cancelled) this.outputConfig.folder = res.folder;
      } catch (e) {
        this.showToast(e.message, 'error');
      }
    },

    async loadDefaultOutputFolder() {
      // Shown rather than assumed: an empty or relative folder would be
      // written next to the executable, which auto-updates replace.
      try {
        const res = await api.getDefaultOutputFolder();
        if (!this.outputConfig.folder) this.outputConfig.folder = res.folder;
      } catch { /* the Python side resolves it anyway on run */ }
    },

    async loadPresets() {
      try {
        this.presets = await api.getPresets();
        const stillExists = this.presets.some(p => p.path === this.selectedPresetPath);
        if (!stillExists) {
          this.selectedPresetPath = '';
          this.selectedPreset = null;
        }
      } catch (e) {
        this.showToast(e.message, 'error');
      }
    },

    async onPresetChange() {
      if (!this.selectedPresetPath) { this.selectedPreset = null; return; }
      try {
        this.selectedPreset = await api.loadPreset(this.selectedPresetPath);
      } catch (e) {
        this.showToast(e.message, 'error');
      }
    },

    async openFile() {
      try {
        const data = await api.openFilesDialog();
        if (data?.cancelled) return;
        this.files = data.files;
        this.resetRun();
      } catch (e) {
        this.showToast(e.message, 'error');
      }
    },

    clearFiles() {
      this.files = [];
      this.resetRun();
    },

    async runPreset() {
      if (!this.canRun) return;
      this.resetRun();
      this.runState = 'running';
      this.fileStates[0].status = 'running';
      try {
        await api.runPreset(
          this.selectedPresetPath,
          this.files.map(f => f.path),
          this.outputConfig,
        );
      } catch (e) {
        this.runState = 'error';
        this.fileStates[0].status = 'error';
        this.pushLog('err', e.message);
      }
    },

    async stopRun() {
      try {
        await api.stopRun();
        this.runState = 'stopped';
      } catch (e) {
        this.showToast(e.message, 'error');
      }
    },

    onFlashEvent(type, data) {
      // Every backend event carries the file it belongs to, so a batch
      // updates its own queue row and never the one before it.
      const file = this.fileStates[data.file_index];
      if (file?.status === 'pending') file.status = 'running';

      switch (type) {
        case 'step': this.handleStepEvent(data, file); break;
        case 'done': this.handleDoneEvent(data, file); break;
        case 'batch_done': this.handleBatchDoneEvent(data); break;
        case 'error': this.handleErrorEvent(data, file); break;
        case 'files_dropped': this.handleDroppedFilesEvent(data); break;
        case 'log': this.handleLogEvent(data); break;
      }
    },

    handleStepEvent(data, file) {
      const idx = data.step_index + 1;
      if (file) file.progress = this.totalSteps > 0 ? Math.round(idx / this.totalSteps * 100) : 0;
      this.pushLog('step', `${stepLabel(data.step_name, this.i18n.t)} ✓ (${data.rows_in} → ${data.rows_out} rows)`);
    },

    handleDoneEvent(data, file) {
      if (file) { file.status = 'done'; file.progress = 100; }
      this.stats.rows_out += data.rows_out;
      this.pushLog('ok', this.i18n.t('log.done', { elapsed: data.elapsed_s, path: data.output_path }));
    },

    handleBatchDoneEvent(data) {
      this.stats.elapsed_s = data.elapsed_s;
      // Files left pending were never reached: the run stopped before them.
      for (const file of this.fileStates) {
        if (file.status === 'pending' || file.status === 'running') file.status = 'skipped';
      }
      if (this.runState === 'running') {
        this.runState = data.succeeded === data.total ? 'done' : 'error';
      }
    },

    handleErrorEvent(data, file) {
      const em = this.outputConfig.error_mode;
      this.stats.errors++;
      this.pushLog('err', data.message);
      // data.fatal: the worker gave up before the step loop, so no 'done'
      // will follow for this file whatever the error mode says.
      if (file) file.status = (data.fatal || em === 'stop') ? 'error' : 'skipped';
    },

    handleDroppedFilesEvent(data) {
      // Python resolved the real paths: the browser's File objects have none.
      if (this.runState !== 'running') {
        this.files = data.files;
        this.resetRun();
      }
    },

    handleLogEvent(data) {
      if (data.level === 'warn') this.stats.warnings++;
      this.pushLog(data.level, data.key ? this.i18n.t(data.key, data.params) : data.message);
    },

    pushLog(level, message) {
      const d = new Date();
      const time = [d.getHours(), d.getMinutes(), d.getSeconds()]
        .map(n => String(n).padStart(2, '0')).join(':');
      this.logs.push({ level, message, time });
      if (this.autoScroll) {
        this.$nextTick(() => {
          const el = this.$refs.conBody;
          if (el) el.scrollTop = el.scrollHeight;
        });
      }
    },

    resetRun() {
      this.runState = 'idle';
      this.fileStates = this.files.map(() => ({ status: 'pending', progress: 0 }));
      this.stats = { rows_out: 0, warnings: 0, errors: 0, elapsed_s: null };
      this.logs = [];
    },

    fileSizeLabel(bytes) {
      if (!bytes) return '';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },

    fileExt(name) { return name?.split('.').pop().toLowerCase() ?? ''; },

    stepDisplay(action) { return stepLabel(action, this.i18n.t); },
  },

  template: `
<div class="processing-page">

  <!-- Work column: files + console -->
  <section class="processing-work">

    <!-- Files area -->
    <div class="files-area">
      <div class="area-head">
        <h2>{{ i18n.t('proc.input_file') }}</h2>
        <span class="ah-meta">{{ files.length ? i18n.t('proc.n_files', { count: files.length }) : i18n.t('proc.no_files') }}</span>
        <span style="flex:1 1 auto"></span>
        <button v-if="files.length" class="link-btn" @click="openFile" :disabled="runState === 'running'">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
          {{ i18n.t('proc.load_file') }}
        </button>
        <button v-if="files.length" class="link-btn danger"
          @click="clearFiles" :disabled="runState === 'running'">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          {{ i18n.t('file.clear') }}
        </button>
      </div>

      <!-- Drop zone -->
      <div v-if="!files.length" class="dropzone" @click="openFile">
        <span class="dz-ico">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 16V8M9 11l3-3 3 3"/>
            <path d="M20 16.5A4.5 4.5 0 0 0 18 8h-1.26A7 7 0 1 0 4 14.9"/>
          </svg>
        </span>
        <span>{{ i18n.t('proc.dropzone') }}
          <span style="color:var(--text_secondary);font-weight:400">{{ i18n.t('proc.dropzone_or') }}</span>
        </span>
      </div>

      <!-- File row -->
      <div v-if="files.length" class="file-queue">
        <div v-for="(file, i) in files" :key="file.path" class="file-row"
          :class="{ running: fileStates[i]?.status === 'running', error: fileStates[i]?.status === 'error' }">
          <img v-if="fileIconUrl(file)" class="file-ico" :src="fileIconUrl(file)" alt="">
          <div class="file-main">
            <div class="file-top">
              <span class="file-name">{{ file.file_name }}</span>
              <span class="file-size">{{ fileSizeLabel(file.size_bytes) }}</span>
            </div>
            <div v-if="i === 0" class="file-sub">{{ file.columns?.length ?? 0 }} {{ i18n.t('proc.columns') }}</div>
            <div class="file-prog"><i :style="{ width: (fileStates[i]?.progress ?? 0) + '%' }"></i></div>
          </div>
          <div class="file-right">
            <span class="status-badge" :class="fileStates[i]?.status ?? 'pending'">
              <span class="dot"></span>{{ STATUS_LABEL[fileStates[i]?.status ?? 'pending'] }}
            </span>
          </div>
        </div>
      </div>

      <!-- Empty state (shown below drop zone when no file) -->
      <div v-if="!files.length" class="empty-state" style="margin-top:14px">
        <span class="es-title">{{ i18n.t('proc.no_file') }}</span>
        <span class="es-sub">{{ i18n.t('proc.no_file_sub') }}</span>
      </div>
    </div>

    <!-- Console -->
    <div class="p-console" :class="{ collapsed: consoleCollapsed }">
      <div class="con-head" @click.self="consoleCollapsed = !consoleCollapsed">
        <span class="con-caret" @click="consoleCollapsed = !consoleCollapsed">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
        </span>
        <span class="con-title">
          <span class="con-live" :class="{ on: runState === 'running' }"></span>
          {{ i18n.t('proc.console') }}
        </span>
        <div class="con-filters" @click.stop>
          <span v-for="f in ['all','info','step','warn','err']" :key="f"
            class="con-chip" :class="{ active: consoleFilter === f }"
            @click="consoleFilter = f">{{ f[0].toUpperCase() + f.slice(1) }}</span>
        </div>
        <span style="flex:1 1 auto"></span>
        <span class="con-tool" :class="{ active: autoScroll }" title="Auto-scroll"
          @click.stop="autoScroll = !autoScroll">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
        </span>
        <span class="con-tool" title="Clear console"
          @click.stop="logs = []; pushLog('info', i18n.t('log.console_cleared'))">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
        </span>
      </div>
      <div class="con-body" ref="conBody">
        <div v-for="(log, i) in filteredLogs" :key="i"
          class="log-line"
          :class="log.level === 'err' ? 'l-err' : log.level === 'warn' ? 'l-warn' : 'l-info'">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-lvl" :class="'lvl-' + log.level">
            {{ LEVEL_LABEL[log.level] ?? log.level.toUpperCase() }}
          </span>
          <span class="log-msg">{{ log.message }}</span>
        </div>
      </div>
    </div>

  </section>

  <!-- Run panel -->
  <aside class="run-panel">
    <div class="rp-scroll">

      <!-- Preset selector -->
      <div class="rp-block">
        <span class="rp-label">{{ i18n.t('proc.preset') }}</span>
        <div style="position:relative">
          <select
            style="appearance:none;-webkit-appearance:none;width:100%;height:34px;background:var(--surface_sunken);border:2px solid var(--border_subtle);border-radius:5px;color:var(--text_primary);font-family:inherit;font-size:13px;padding:0 30px 0 11px;cursor:pointer;outline:none;transition:border-color .12s"
            v-model="selectedPresetPath" @change="onPresetChange">
            <option value="" disabled>{{ i18n.t('proc.preset_ph') }}</option>
            <option v-for="p in presets" :key="p.path" :value="p.path">
              {{ p.name }} — {{ p.label }} — {{ p.step_count }} {{ i18n.t('proc.actions') }}
            </option>
          </select>
          <span style="position:absolute;right:11px;top:50%;width:7px;height:7px;border-right:2px solid var(--text_secondary);border-bottom:2px solid var(--text_secondary);transform:translateY(-70%) rotate(45deg);pointer-events:none"></span>
        </div>
        <div v-if="selectedPreset" class="preset-box">
          <div class="pb-top">
            <span class="pb-name">{{ selectedPreset.name }}</span>
            <span class="pb-count">{{ totalSteps }} {{ i18n.t('proc.actions') }}</span>
          </div>
          <div class="pb-ops">
            <span v-for="s in stepNames" :key="s" class="op-tag">{{ stepDisplay(s) }}</span>
          </div>
        </div>
      </div>

      <!-- Output config -->
      <div class="rp-block">
        <span class="rp-label">{{ i18n.t('proc.output') }}</span>
        <div class="field">
          <span class="field-label">{{ i18n.t('proc.format') }}</span>
          <div style="position:relative">
            <select
              style="appearance:none;-webkit-appearance:none;width:100%;height:34px;background:var(--surface_sunken);border:2px solid var(--border_subtle);border-radius:5px;color:var(--text_primary);font-family:inherit;font-size:13px;padding:0 30px 0 11px;cursor:pointer;outline:none;"
              v-model="outputConfig.format">
              <option value="keep">{{ i18n.t('proc.fmt_keep') }}</option>
              <option value="xlsx">.xlsx (Excel)</option>
              <option value="csv">.csv (UTF-8)</option>
              <option value="parquet">.parquet</option>
            </select>
            <span style="position:absolute;right:11px;top:50%;width:7px;height:7px;border-right:2px solid var(--text_secondary);border-bottom:2px solid var(--text_secondary);transform:translateY(-70%) rotate(45deg);pointer-events:none"></span>
          </div>
        </div>
        <div class="field">
          <span class="field-label">{{ i18n.t('proc.dest_folder') }}</span>
          <div style="display:flex;gap:8px">
            <input class="input" style="flex:1 1 auto" v-model="outputConfig.folder" />
            <button class="icon-btn" title="Browse folder" @click="browseFolder">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
            </button>
          </div>
        </div>
        <div class="field">
          <span class="field-label">{{ i18n.t('proc.naming_pattern') }}</span>
          <input class="input" v-model="outputConfig.pattern" />
        </div>
      </div>

      <!-- On error -->
      <div class="rp-block">
        <span class="rp-label">{{ i18n.t('proc.on_error') }}</span>
        <div class="radio-col">
          <div v-for="opt in ERROR_OPTS" :key="opt.value"
            class="radio-row" :class="{ on: outputConfig.error_mode === opt.value }"
            @click="outputConfig.error_mode = opt.value">
            <span class="radio-mark"></span>
            {{ opt.label }}
            <span class="rr-sub">{{ opt.sub }}</span>
          </div>
        </div>
      </div>

      <div class="rp-block schedule-block">
        <span class="rp-label">{{ i18n.t('execution.section') }}</span>
        <p class="schedule-hint">{{ i18n.t('execution.intro') }}</p>
        <button class="btn schedule-copy" @click="openExecutionSettings" :disabled="!canRun">
          {{ i18n.t('execution.open') }}
        </button>
      </div>

    </div>

    <!-- Footer: progress + stats + run/stop buttons -->
    <div class="rp-foot">
      <div class="ov-prog">
        <div class="ov-top">
          <span class="ov-label">{{ i18n.t('proc.progress') }}</span>
          <span class="ov-pct">{{ overallProgress }}%</span>
        </div>
        <div class="ov-bar"><i :style="{ width: overallProgress + '%' }"></i></div>
      </div>
      <div class="stat-grid">
        <div class="stat ok">
          <div class="sv">{{ stats.rows_out.toLocaleString('en-US') }}</div>
          <div class="sl">{{ i18n.t('proc.stat_rows') }}</div>
        </div>
        <div class="stat" :class="stats.errors > 0 ? 'err' : ''">
          <div class="sv">{{ stats.errors }}</div>
          <div class="sl">{{ i18n.t('proc.stat_errors') }}</div>
        </div>
        <div class="stat" :class="stats.warnings > 0 ? 'warn' : ''">
          <div class="sv">{{ stats.warnings }}</div>
          <div class="sl">{{ i18n.t('proc.stat_warnings') }}</div>
        </div>
        <div class="stat">
          <div class="sv">{{ stats.elapsed_s != null ? stats.elapsed_s + 's' : '—' }}</div>
          <div class="sl">{{ i18n.t('proc.stat_elapsed') }}</div>
        </div>
      </div>
      <div class="run-actions">
        <button class="btn preview-button run-main" @click="previewPreset" :disabled="!canRun">
          {{ i18n.t('proc.preview') }}
        </button>
        <button class="btn primary run-main" @click="runPreset" :disabled="!canRun">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          {{ i18n.t('proc.run') }}
        </button>
        <button class="btn danger-hover run-main" @click="stopRun"
          :disabled="runState !== 'running'" style="flex:0 0 auto">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
        </button>
      </div>
    </div>
  </aside>

<ExecutionModal v-if="executionDraft" :execution="executionDraft" @close="executionDraft = null" />

<teleport to="body">
  <div v-if="previewOpen" class="modal-overlay" @click.self="previewOpen = false" @keydown.esc.stop="previewOpen = false">
    <div class="modal preview-dialog" role="dialog" aria-modal="true" aria-labelledby="preview-title">
      <div class="modal-head">
        <h3 id="preview-title">{{ i18n.t('proc.preview_title') }}</h3>
        <button class="icon-btn" ref="previewClose" @click="previewOpen = false" :aria-label="i18n.t('proc.preview_close')">×</button>
      </div>
      <div class="preview-body" :aria-busy="previewLoading">
        <p class="preview-hint">{{ i18n.t('proc.preview_hint', { file: previewFileName }) }}</p>
        <p v-if="previewLoading" role="status">{{ i18n.t('proc.preview_loading') }}</p>
        <p v-else-if="previewError" class="preview-error" role="alert">{{ i18n.t('proc.preview_error', { error: previewError }) }}</p>
        <template v-else-if="previewData">
          <p v-if="!previewData.rows.length" class="preview-empty" role="status">{{ i18n.t('proc.preview_empty') }}</p>
          <template v-else>
            <p class="preview-hint">{{ i18n.t('proc.preview_count', { count: previewData.rows.length }) }}</p>
            <div class="preview-table-scroll" tabindex="0" :aria-label="i18n.t('proc.preview_title')">
              <table class="preview-table">
                <thead><tr><th v-for="column in previewData.columns" :key="column" scope="col">{{ column }}</th></tr></thead>
                <tbody>
                  <tr v-for="(row, index) in previewData.rows" :key="index">
                    <td v-for="column in previewData.columns" :key="column" :class="{ 'preview-null': row[column] === null }">
                      {{ row[column] === null ? i18n.t('proc.preview_null') : row[column] }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </template>
      </div>
    </div>
  </div>
</teleport>
</div>
  `,
};
