import { api } from '../api.js';
import FileLoader from '../components/FileLoader.js';
import ActionSteps from '../components/ActionSteps.js';
import { STEP_ACTIONS, stepLabel } from '../steps-registry.js';

// Single source of truth: this list used to be duplicated here, so a step added
// to the registry silently kept its old position (or went missing) on save.
const ACTION_ORDER = STEP_ACTIONS;

// How each step payload references column names. One description drives both
// the purge below and the rename propagation: a new step only needs an entry
// here instead of a branch in each.
const COLUMN_REFS = {
  rename_columns: { map: 'mapping' },
  select_columns: { list: 'columns' },
  drop_columns: { list: 'columns' },
  cast_types: { map: 'casts' },
  replace_values: { list: 'items', key: 'column' },
  clean_text: { list: 'items', inner: 'columns' },
  fill_nulls: { list: 'columns' },
  add_computed_column: { expression: true },
  filter_rows: { list: 'conditions', key: 'column' },
  deduplicate_rows: { list: 'subset' },
  sort_rows: { list: 'by', key: 'column' },
  reorder_columns: { list: 'columns' },
};

/**
 * Applies `fn` to every column name a payload references: it returns the new
 * name, or null to drop that reference. Returns the new payload, the payload
 * untouched when it holds no such collection, or null once every reference
 * was dropped.
 */
function rewriteRefs(payload, spec, fn) {
  if (spec.map) {
    if (!payload[spec.map]) return payload;
    const out = {};
    for (const [k, v] of Object.entries(payload[spec.map])) {
      const name = fn(k);
      if (name !== null) out[name] = v;
    }
    return Object.keys(out).length ? { ...payload, [spec.map]: out } : null;
  }
  const items = payload[spec.list];
  if (!items) return payload;
  let out;
  if (spec.inner) {
    out = items
      .map(it => ({ ...it, [spec.inner]: it[spec.inner].map(fn).filter(c => c !== null) }))
      .filter(it => it[spec.inner].length);
  } else if (spec.key) {
    out = items.map(it => ({ ...it, [spec.key]: fn(it[spec.key]) })).filter(it => it[spec.key] !== null);
  } else {
    out = items.map(fn).filter(c => c !== null);
  }
  return out.length ? { ...payload, [spec.list]: out } : null;
}

/**
 * Strips every reference to vanished columns from the payloads.
 * Returns a new, cleaned payloads object.
 */
function purgePayloads(payloads, missingCols) {
  const missing = new Set(missingCols);
  const keep = c => (missing.has(c) ? null : c);
  const p = { ...payloads };
  for (const [action, spec] of Object.entries(COLUMN_REFS)) {
    // Computed expressions are text, not a column list: left untouched.
    if (spec.expression || !p[action]) continue;
    p[action] = rewriteRefs(p[action], spec, keep) ?? {};
  }
  return p;
}

const IDENT_RE = /^[A-Za-z_]\w*$/;
function escapeRegExp(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, String.raw`\$&`); }

/**
 * Replaces every reference to `oldName` with `newName` in an
 * add_computed_column (syntaxe `[Nom de colonne]` ou identifiant brut).
 */
function renameInExpression(expr, oldName, newName) {
  if (!expr) return expr;
  const newRef = IDENT_RE.test(newName) ? newName : `[${newName}]`;
  let result = expr.split(`[${oldName}]`).join(newRef);
  if (IDENT_RE.test(oldName)) {
    result = result.replace(new RegExp(String.raw`\b${escapeRegExp(oldName)}\b`, 'g'), newRef);
  }
  return result;
}

/**
 * Rewrites references to `oldName` as `newName` in every step located
 * after `fromAction` in the pipeline (propagating a column rename,
 * whether it comes from rename_columns or from add_computed_column).
 */
function renameColumnDownstream(payloads, fromAction, oldName, newName) {
  if (oldName === newName) return payloads;
  const fromIdx = ACTION_ORDER.indexOf(fromAction);
  const sub = c => (c === oldName ? newName : c);
  const p = { ...payloads };
  ACTION_ORDER.forEach((action, idx) => {
    const payload = p[action];
    if (idx <= fromIdx || !payload) return;
    const spec = COLUMN_REFS[action];
    if (!spec) return;
    if (spec.expression) {
      if (payload.items) {
        p[action] = { ...payload, items: payload.items.map(it => ({ ...it, expression: renameInExpression(it.expression, oldName, newName) })) };
      }
      return;
    }
    // A rename never drops a reference, so rewriteRefs cannot empty the step.
    p[action] = rewriteRefs(payload, spec, sub);
  });
  return p;
}

export default {
  name: 'PresetsPage',
  components: { FileLoader, ActionSteps },
  inject: ['showToast', 'i18n'],
  data() {
    return {
      presets: [],
      selectedPath: null,
      isNew: false,
      presetName: '',
      fileInfo: null,
      fileSchema: {},
      presetColumns: [],
      templateFile: '',     // template file name recorded in the preset
      payloads: {},
      // Mismatch modal state
      mismatch: null,   // null | { pending, missing, added }
      // Delete confirmation modal
      showDeleteConfirm: false,
    };
  },
  computed: {
    t() { return this.i18n.t; },
    hasSelection() { return !!this.selectedPath || this.isNew; },
    sourceColumns() { return this.fileInfo?.columns || this.presetColumns; },
    sourceSchema() { return this.fileSchema; },
  },
  async created() { await this.loadList(); },

  mounted() {
    // The drop handler lives on the window body, so this page gets the event
    // too. Without a listener here the Python side would still have swapped
    // the loaded file, with nothing on screen saying so.
    window.flashEvent = (type, data) => {
      if (type === 'files_dropped' && data.files?.length) this.acceptFile(data.files[0]);
    };
  },

  beforeUnmount() { delete window.flashEvent; },

  methods: {
    async loadList() {
      try { this.presets = await api.getPresets(); }
      catch (e) { this.showToast(this.t('toast.presets_load_failed', { error: e.message }), 'error'); }
    },

    async selectPreset(path) {
      try {
        const data = await api.loadPreset(path);
        this.selectedPath = path;
        this.isNew = false;
        this.presetName = data.name;
        this.fileInfo = null;
        this.fileSchema = data.source_types || {};
        this.presetColumns = data.source_columns || [];
        // Fallback: when the preset has columns but no source_file yet
        // (saved before the field existed), still show the template state.
        this.templateFile = data.source_file || (this.presetColumns.length ? this.t('file.template_unknown') : '');
        this.payloads = {};
        for (const step of data.steps) {
          const { action, ...rest } = step;
          this.payloads[action] = { action, ...rest };
        }
      } catch (e) { this.showToast(this.t('toast.preset_load_failed', { error: e.message }), 'error'); }
    },

    async newPreset() {
      const name = `Preset ${this.presets.length + 1}`;
      try {
        await api.newPreset(name);
        this.isNew = true; this.selectedPath = null;
        this.presetName = name; this.fileInfo = null;
        this.fileSchema = {}; this.presetColumns = []; this.templateFile = ''; this.payloads = {};
      } catch (e) { this.showToast(this.t('toast.preset_create_failed', { error: e.message }), 'error'); }
    },

    async savePreset() {
      if (!this.presetName.trim()) { this.showToast(this.t('toast.preset_name_empty'), 'error'); return; }
      try {
        const steps = ACTION_ORDER.map(a => this.payloads[a]).filter(p => p && Object.keys(p).length > 1);
        const res = await api.savePreset(this.presetName, steps);
        this.selectedPath = res.path; this.isNew = false;
        await this.loadList();
        // Steps the model refused are absent from the saved file — say so
        // rather than let them vanish.
        if (res.rejected?.length) {
          const names = res.rejected.map(r => stepLabel(r.action, this.i18n.t)).join(', ');
          this.showToast(this.t('toast.preset_saved_with_rejected', { steps: names }), 'error');
        } else {
          this.showToast(this.t('toast.preset_saved'));
        }
      } catch (e) { this.showToast(this.t('toast.preset_save_failed', { error: e.message }), 'error'); }
    },

    deletePreset() {
      if (!this.selectedPath) return;
      this.showDeleteConfirm = true;
    },
    async confirmDelete() {
      this.showDeleteConfirm = false;
      try {
        await api.deletePreset(this.selectedPath);
        this.selectedPath = null; this.isNew = false;
        this.presetName = ''; this.fileInfo = null;
        this.fileSchema = {}; this.templateFile = ''; this.payloads = {};
        await this.loadList();
        this.showToast(this.t('toast.preset_deleted'));
      } catch (e) { this.showToast(this.t('toast.preset_delete_failed', { error: e.message }), 'error'); }
    },
    cancelDelete() { this.showDeleteConfirm = false; },

    async exportPreset() {
      if (!this.selectedPath) return;
      try {
        const res = await api.exportPreset(this.selectedPath);
        if (!res?.cancelled) this.showToast(this.t('toast.preset_exported'));
      } catch (e) { this.showToast(this.t('toast.preset_export_failed', { error: e.message }), 'error'); }
    },

    async loadFile() {
      try {
        const res = await api.openFileDialog();
        if (res?.cancelled) return;
        this.acceptFile(res);
      } catch (e) { this.showToast(this.t('toast.file_error', { error: e.message }), 'error'); }
    },

    // Shared by the picker and by a file dropped onto the window.
    acceptFile(res) {
      // Compare against the columns recorded in the preset
      const savedCols = this.presetColumns;
      if (savedCols.length > 0) {
        const missing = savedCols.filter(c => !res.columns.includes(c));
        const added = res.columns.filter(c => !savedCols.includes(c));
        if (missing.length > 0 || added.length > 0) {
          // Stocker en attente et afficher le modal
          this.mismatch = { pending: res, missing, added };
          return;
        }
      }
      this._applyFile(res);
    },

    async clearFile() {
      await api.clearFile();
      this.fileInfo = null;
      this.fileSchema = {};
    },

    _applyFile(res) {
      this.fileInfo = res;
      this.fileSchema = res.schema || {};
      this.templateFile = res.file_name || '';
    },

    mismatchIgnore() {
      this._applyFile(this.mismatch.pending);
      this.mismatch = null;
    },

    mismatchCleanup() {
      const { pending, missing } = this.mismatch;
      this._applyFile(pending);
      this.payloads = purgePayloads(this.payloads, missing);
      this.mismatch = null;
      if (missing.length > 0) this.showToast(this.t('toast.refs_removed', { n: missing.length }));
    },

    mismatchCancel() {
      this.mismatch = null;
    },

    onPayloads(newPayloads) {
      let result = newPayloads;
      const old = this.payloads;

      // Renaming a source column (rename_columns) -> propagate to later steps
      const oldMapping = old.rename_columns?.mapping || {};
      const newMapping = newPayloads.rename_columns?.mapping || {};
      for (const src of Object.keys(newMapping)) {
        if (src in oldMapping && oldMapping[src] !== newMapping[src]) {
          result = renameColumnDownstream(result, 'rename_columns', oldMapping[src], newMapping[src]);
        }
      }

      // Renaming a computed column (add_computed_column.target) -> propagate to later steps
      const oldItems = old.add_computed_column?.items || [];
      const newItems = newPayloads.add_computed_column?.items || [];
      newItems.forEach((item, i) => {
        const oldItem = oldItems[i];
        if (oldItem?.target && item.target && oldItem.target !== item.target) {
          result = renameColumnDownstream(result, 'add_computed_column', oldItem.target, item.target);
        }
      });

      this.payloads = result;
    },
  },

  template: `
    <div class="presets-page">

      <!-- Toolbar -->
      <div class="toolbar">
        <div class="tb-presets-cell">
          <span class="sec-label">{{ t('presets.title') }}</span>
          <button class="icon-btn" @click="newPreset" :title="t('presets.new')">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
          </button>
        </div>
        <div class="tb-actions-cell">
          <template v-if="hasSelection">
            <input class="input name-input" v-model="presetName" :placeholder="t('presets.name')" :aria-label="t('presets.name')" />
            <button class="btn primary" @click="savePreset" :disabled="presets.find(p => p.path === selectedPath)?.read_only">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><path d="M17 21v-8H7v8M7 3v5h8"/></svg>
              {{ t('toolbar.save') }}
            </button>
            <span class="tb-spacer"></span>
            <button class="btn danger-hover" @click="deletePreset" :disabled="!selectedPath || presets.find(p => p.path === selectedPath)?.read_only">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6"/></svg>
              {{ t('toolbar.delete') }}
            </button>
            <button class="btn" @click="exportPreset" :disabled="!selectedPath">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4M8 8l4-4 4 4"/><path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>
              {{ t('toolbar.export') }}
            </button>
          </template>
        </div>
      </div>

      <!-- Body -->
      <div class="presets-body">

        <!-- Left: preset list -->
        <aside class="presets-col">
          <div v-if="!presets.length" class="presets-empty" style="white-space:pre-line">
            {{ t('presets.empty') }}
          </div>
          <div v-for="p in presets" :key="p.path"
            class="preset-card" :class="{ active: selectedPath === p.path, broken: p.error }"
            @click="selectPreset(p.path)">
            <span class="pc-name">{{ p.name }}</span>
            <span class="pc-meta">{{ p.label }}</span>
            <span class="pc-meta" v-if="p.error" :title="p.error">{{ t('presets.unreadable') }}</span>
            <span class="pc-meta" v-else>{{ p.step_count }}</span>
          </div>
        </aside>

        <!-- Right: settings -->
        <section class="settings-col">
          <div v-if="!hasSelection" class="settings-placeholder">
            {{ t('presets.placeholder') }}
          </div>

          <template v-else>
            <h2 class="panel-title">{{ t('presets.name') }}</h2>

            <!-- Step 1 -->
            <div class="step">
              <div class="step-head">
                <span class="step-badge">1</span>
                <span class="step-title">{{ t('presets.step1.title') }}</span>
                <span class="step-hint">{{ t('presets.step1.hint') }} <code>.xlsx .xls .xlsm .csv</code></span>
              </div>
              <FileLoader :fileInfo="fileInfo" :templateFile="templateFile" @load="loadFile" @clear="clearFile" />
            </div>

            <div class="sep-line"></div>

            <!-- Step 2 -->
            <div class="step">
              <div class="step-head">
                <span class="step-badge">2</span>
                <span class="step-title">{{ t('presets.step2.title') }}</span>
                <span v-if="!sourceColumns.length" class="step-hint">{{ t('presets.step2.hint') }}</span>
              </div>
              <ActionSteps
                :columns="sourceColumns"
                :schema="sourceSchema"
                :payloads="payloads"
                @update:payloads="onPayloads" />
            </div>
          </template>
        </section>

      </div>

      <!-- Mismatch modal -->
      <teleport to="body">
        <div v-if="mismatch" class="modal-overlay" @click.self="mismatchCancel">
          <div class="modal">

            <div class="modal-head">
              <h3>{{ t('mismatch.title') }}</h3>
              <p>{{ t('mismatch.subtitle') }}</p>
            </div>

            <div class="modal-body">

              <template v-if="mismatch.missing.length">
                <div class="panel-sub">{{ t('mismatch.missing') }}</div>
                <div class="mismatch-list mismatch-list--warn">
                  <span v-for="c in mismatch.missing" :key="c" class="mismatch-chip mismatch-chip--warn">{{ c }}</span>
                </div>
              </template>

              <template v-if="mismatch.added.length">
                <div class="panel-sub" :class="{ mt: mismatch.missing.length }">{{ t('mismatch.added') }}</div>
                <div class="mismatch-list">
                  <span v-for="c in mismatch.added" :key="c" class="mismatch-chip">{{ c }}</span>
                </div>
              </template>

            </div>

            <div class="modal-foot">
              <button class="btn" @click="mismatchCancel">{{ t('modal.cancel') }}</button>
              <button class="btn" @click="mismatchIgnore">{{ t('mismatch.ignore') }}</button>
              <button v-if="mismatch.missing.length" class="btn primary" @click="mismatchCleanup">
                {{ t('mismatch.cleanup') }}
              </button>
              <button v-else class="btn primary" @click="mismatchIgnore">{{ t('mismatch.load') }}</button>
            </div>

          </div>
        </div>
      </teleport>

      <!-- Delete confirmation modal -->
      <teleport to="body">
        <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
          <div class="modal" style="width:380px;">
            <div class="modal-head">
              <h3>{{ t('preset.delete_title') }}</h3>
              <p>{{ t('preset.delete_subtitle') }}</p>
            </div>
            <div class="modal-body" style="padding:16px;">
              <p style="font-size:var(--fs-md);color:var(--text_secondary);">
                {{ t('preset.delete_confirm') }} <strong style="color:var(--text_primary);">{{ presetName }}</strong> ?
              </p>
            </div>
            <div class="modal-foot">
              <button class="btn btn-ghost" @click="cancelDelete">{{ t('modal.cancel') }}</button>
              <button class="btn btn-danger" @click="confirmDelete">{{ t('toolbar.delete') }}</button>
            </div>
          </div>
        </div>
      </teleport>

    </div>
  `,
};
