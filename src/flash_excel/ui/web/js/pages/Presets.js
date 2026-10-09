import { api } from '../api.js';
import FileLoader from '../components/FileLoader.js';
import ActionSteps from '../components/ActionSteps.js';
import { STEP_ACTIONS } from '../steps-registry.js';

// Single source of truth: this list used to be duplicated here, so a step added
// to the registry silently kept its old position (or went missing) on save.
const ACTION_ORDER = STEP_ACTIONS;

/**
 * Supprime des payloads toute référence aux colonnes disparues.
 * Retourne un nouvel objet payloads nettoyé.
 */
function purgePayloads(payloads, missingCols) {
  const missing = new Set(missingCols);
  const p = { ...payloads };

  if (p.rename_columns?.mapping) {
    const m = Object.fromEntries(Object.entries(p.rename_columns.mapping).filter(([k]) => !missing.has(k)));
    p.rename_columns = Object.keys(m).length ? { ...p.rename_columns, mapping: m } : {};
  }
  if (p.select_columns?.columns) {
    const cols = p.select_columns.columns.filter(c => !missing.has(c));
    p.select_columns = cols.length ? { ...p.select_columns, columns: cols } : {};
  }
  if (p.drop_columns?.columns) {
    const cols = p.drop_columns.columns.filter(c => !missing.has(c));
    p.drop_columns = cols.length ? { ...p.drop_columns, columns: cols } : {};
  }
  if (p.fill_nulls?.columns) {
    const cols = p.fill_nulls.columns.filter(c => !missing.has(c));
    p.fill_nulls = cols.length ? { ...p.fill_nulls, columns: cols } : {};
  }
  if (p.cast_types?.casts) {
    const casts = Object.fromEntries(Object.entries(p.cast_types.casts).filter(([k]) => !missing.has(k)));
    p.cast_types = Object.keys(casts).length ? { ...p.cast_types, casts } : {};
  }
  if (p.replace_values?.items) {
    const items = p.replace_values.items.filter(it => !missing.has(it.column));
    p.replace_values = items.length ? { ...p.replace_values, items } : {};
  }
  if (p.clean_text?.items) {
    const items = p.clean_text.items
      .map(it => ({ ...it, columns: it.columns.filter(c => !missing.has(c)) }))
      .filter(it => it.columns.length);
    p.clean_text = items.length ? { ...p.clean_text, items } : {};
  }
  if (p.filter_rows?.conditions) {
    const conditions = p.filter_rows.conditions.filter(c => !missing.has(c.column));
    p.filter_rows = conditions.length ? { ...p.filter_rows, conditions } : {};
  }
  if (p.deduplicate_rows?.subset) {
    const subset = p.deduplicate_rows.subset.filter(c => !missing.has(c));
    p.deduplicate_rows = subset.length ? { ...p.deduplicate_rows, subset } : {};
  }
  if (p.sort_rows?.by) {
    const by = p.sort_rows.by.filter(s => !missing.has(s.column));
    p.sort_rows = by.length ? { ...p.sort_rows, by } : {};
  }
  if (p.reorder_columns?.columns) {
    const columns = p.reorder_columns.columns.filter(c => !missing.has(c));
    p.reorder_columns = columns.length ? { ...p.reorder_columns, columns } : {};
  }
  return p;
}

const IDENT_RE = /^[A-Za-z_]\w*$/;
function escapeRegExp(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, String.raw`\$&`); }

/**
 * Remplace toute référence à `oldName` par `newName` dans une expression
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
 * Réécrit les références à `oldName` en `newName` dans tous les steps
 * situés après `fromAction` dans le pipeline (propagation d'un renommage
 * de colonne, qu'il vienne de rename_columns ou d'add_computed_column).
 */
function renameColumnDownstream(payloads, fromAction, oldName, newName) {
  if (oldName === newName) return payloads;
  const fromIdx = ACTION_ORDER.indexOf(fromAction);
  const p = { ...payloads };
  ACTION_ORDER.forEach((action, idx) => {
    if (idx <= fromIdx) return;
    const payload = p[action];
    if (!payload) return;
    switch (action) {
      case 'select_columns':
        if (payload.columns) p.select_columns = { ...payload, columns: payload.columns.map(c => c === oldName ? newName : c) };
        break;
      case 'drop_columns':
        if (payload.columns) p.drop_columns = { ...payload, columns: payload.columns.map(c => c === oldName ? newName : c) };
        break;
      case 'fill_nulls':
        if (payload.columns) p.fill_nulls = { ...payload, columns: payload.columns.map(c => c === oldName ? newName : c) };
        break;
      case 'cast_types':
        if (payload.casts && oldName in payload.casts) {
          const casts = { ...payload.casts };
          casts[newName] = casts[oldName];
          delete casts[oldName];
          p.cast_types = { ...payload, casts };
        }
        break;
      case 'replace_values':
        if (payload.items) p.replace_values = { ...payload, items: payload.items.map(it => it.column === oldName ? { ...it, column: newName } : it) };
        break;
      case 'clean_text':
        if (payload.items) p.clean_text = { ...payload, items: payload.items.map(it => ({ ...it, columns: it.columns.map(c => c === oldName ? newName : c) })) };
        break;
      case 'add_computed_column':
        if (payload.items) p.add_computed_column = { ...payload, items: payload.items.map(it => ({ ...it, expression: renameInExpression(it.expression, oldName, newName) })) };
        break;
      case 'filter_rows':
        if (payload.conditions) p.filter_rows = { ...payload, conditions: payload.conditions.map(c => c.column === oldName ? { ...c, column: newName } : c) };
        break;
      case 'deduplicate_rows':
        if (payload.subset) p.deduplicate_rows = { ...payload, subset: payload.subset.map(c => c === oldName ? newName : c) };
        break;
      case 'sort_rows':
        if (payload.by) p.sort_rows = { ...payload, by: payload.by.map(s => s.column === oldName ? { ...s, column: newName } : s) };
        break;
      case 'reorder_columns':
        if (payload.columns) p.reorder_columns = { ...payload, columns: payload.columns.map(c => c === oldName ? newName : c) };
        break;
    }
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
      templateFile: '',     // nom du fichier modèle mémorisé dans le preset
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
  methods: {
    async loadList() {
      try { this.presets = await api.getPresets(); }
      catch (e) { this.showToast(`Failed to load presets: ${e.message}`, 'error'); }
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
        // Fallback : si le preset a des colonnes mais pas encore de source_file
        // (sauvé avant l'ajout du champ), on affiche quand même l'état template.
        this.templateFile = data.source_file || (this.presetColumns.length ? this.t('file.template_unknown') : '');
        this.payloads = {};
        for (const step of data.steps) {
          const { action, ...rest } = step;
          this.payloads[action] = { action, ...rest };
        }
      } catch (e) { this.showToast(`Load failed: ${e.message}`, 'error'); }
    },

    async newPreset() {
      const name = `Preset ${this.presets.length + 1}`;
      try {
        await api.newPreset(name);
        this.isNew = true; this.selectedPath = null;
        this.presetName = name; this.fileInfo = null;
        this.fileSchema = {}; this.presetColumns = []; this.templateFile = ''; this.payloads = {};
      } catch (e) { this.showToast(`Error: ${e.message}`, 'error'); }
    },

    async savePreset() {
      if (!this.presetName.trim()) { this.showToast('Preset name cannot be empty', 'error'); return; }
      try {
        const steps = ACTION_ORDER.map(a => this.payloads[a]).filter(p => p && Object.keys(p).length > 1);
        const res = await api.savePreset(this.presetName, steps);
        this.selectedPath = res.path; this.isNew = false;
        await this.loadList();
        this.showToast('Preset saved');
      } catch (e) { this.showToast(`Save failed: ${e.message}`, 'error'); }
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
        this.showToast('Preset deleted');
      } catch (e) { this.showToast(`Delete failed: ${e.message}`, 'error'); }
    },
    cancelDelete() { this.showDeleteConfirm = false; },

    async exportPreset() {
      if (!this.selectedPath) return;
      try {
        const res = await api.exportPreset(this.selectedPath);
        if (!res?.cancelled) this.showToast('Preset exported');
      } catch (e) { this.showToast(`Export failed: ${e.message}`, 'error'); }
    },

    async loadFile() {
      try {
        const res = await api.openFileDialog();
        if (res?.cancelled) return;
        // Comparer avec les colonnes enregistrées dans le preset
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
      } catch (e) { this.showToast(`File error: ${e.message}`, 'error'); }
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
      if (missing.length > 0) this.showToast(`${missing.length} obsolete reference(s) removed`);
    },

    mismatchCancel() {
      this.mismatch = null;
    },

    onPayloads(newPayloads) {
      let result = newPayloads;
      const old = this.payloads;

      // Renommage d'une colonne source (rename_columns) → propager aux steps suivantes
      const oldMapping = old.rename_columns?.mapping || {};
      const newMapping = newPayloads.rename_columns?.mapping || {};
      for (const src of Object.keys(newMapping)) {
        if (src in oldMapping && oldMapping[src] !== newMapping[src]) {
          result = renameColumnDownstream(result, 'rename_columns', oldMapping[src], newMapping[src]);
        }
      }

      // Renommage d'une colonne calculée (add_computed_column.target) → propager aux steps suivantes
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
            <button class="btn primary" @click="savePreset">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><path d="M17 21v-8H7v8M7 3v5h8"/></svg>
              {{ t('toolbar.save') }}
            </button>
            <span class="tb-spacer"></span>
            <button class="btn danger-hover" @click="deletePreset" :disabled="!selectedPath">
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
            class="preset-card" :class="{ active: selectedPath === p.path }"
            @click="selectPreset(p.path)">
            <span class="pc-name">{{ p.name }}</span>
            <span class="pc-meta">{{ p.step_count }}</span>
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
