import { toRaw } from '../../vendor/vue.esm-browser.prod.js';

const ALL_OPS = ['trim', 'collapse', 'accents', 'special'];
const ALL_CASES = ['none', 'lower', 'upper', 'title'];

// Polars dtypes and JS cast types treated as text
const STRING_TYPES = new Set([
  'Utf8', 'String', 'LargeUtf8', 'Categorical', 'Enum',
  'string',
]);

export default {
  name: 'CleanTable',
  props: {
    columns: { type: Array, default: () => [] },
    schema: { type: Object, default: () => ({}) },
    payload: { type: Object, default: () => ({}) },
  },
  emits: ['update:payload'],
  inject: ['i18n'],
  data() {
    return {
      items: [],
      showModal: false,
      editIdx: null,
      draft: { columns: [], ops: [], case: 'none' },
    };
  },
  computed: {
    t() { return this.i18n.t; },
    effectiveColumns() {
      const base = this.columns.length ? this.columns : this.items.flatMap(it => it.columns);
      const stringOnly = Object.keys(this.schema).length
        ? base.filter(c => !this.schema[c] || STRING_TYPES.has(this.schema[c]))
        : base;
      // Exclude columns already covered by another rule (except when editing)
      const usedElsewhere = new Set(
        this.items
          .filter((_, i) => i !== this.editIdx)
          .flatMap(it => it.columns)
      );
      return stringOnly.filter(c => !usedElsewhere.has(c));
    },
    canSave() { return this.draft.columns.length > 0; },
  },
  watch: {
    payload: {
      immediate: true, handler(v) {
        if (this._emitting) return;
        this.items = v.items ? structuredClone(toRaw(v.items)) : [];
      }
    },
  },
  methods: {
    _dbg(msg) {
      console.log('[CleanTable]', msg);
      if (globalThis.pywebview?.api?.debug_log) globalThis.pywebview.api.debug_log(msg);
    },

    emit() {
      this._emitting = true;
      // Clone items so the Vue proxy is not handed to the parent by reference.
      const snapshot = structuredClone(toRaw(this.items));
      this._dbg(`emit: ${snapshot.length} item(s) → ${JSON.stringify(snapshot)}`);
      this.$emit('update:payload', snapshot.length
        ? { action: 'clean_text', items: snapshot }
        : {});
      this.$nextTick(() => { this._emitting = false; });
    },

    openAdd() {
      this.editIdx = null;
      this.draft = { columns: [], ops: [], case: 'none' };
      this.showModal = true;
      this._dbg('openAdd: modal opened');
    },
    openEdit(i) {
      this.editIdx = i;
      this.draft = structuredClone(toRaw(this.items[i]));
      this.showModal = true;
      this._dbg(`openEdit: editing index ${i}`);
    },
    closeModal() {
      this._dbg('closeModal called');
      this.showModal = false;
    },

    deleteItem(i) { this.items.splice(i, 1); this.emit(); },

    toggleCol(col) {
      const set = new Set(this.draft.columns);
      set.has(col) ? set.delete(col) : set.add(col);
      this.draft.columns = this.effectiveColumns.filter(c => set.has(c));
      this._dbg(`toggleCol: ${col} → draft.columns=${JSON.stringify(this.draft.columns)}`);
    },
    isColOn(col) { return this.draft.columns.includes(col); },

    toggleOp(op) {
      const set = new Set(this.draft.ops);
      set.has(op) ? set.delete(op) : set.add(op);
      this.draft.ops = ALL_OPS.filter(o => set.has(o));
    },
    isOpOn(op) { return this.draft.ops.includes(op); },

    setCase(c) { this.draft.case = c; },

    saveModal() {
      this._dbg(`saveModal: canSave=${this.canSave} editIdx=${this.editIdx} draft=${JSON.stringify(this.draft)}`);
      if (!this.canSave) return;
      const rule = structuredClone(toRaw(this.draft));
      if (this.editIdx === null) this.items.push(rule);
      else this.items[this.editIdx] = rule;
      this._dbg(`saveModal: items after push = ${JSON.stringify(this.items)}`);
      this.closeModal();
      this.emit();
    },

    opLabel(op) { return this.t('clean.op_' + op); },
    caseLabel(c) { return this.t('clean.case_' + c); },
  },
  template: `
    <div>

      <!-- List of configured rules -->
      <div v-if="items.length" class="rule-list" style="margin-bottom:10px;">
        <div v-for="(it, i) in items" :key="i" class="clean-row">
          <div class="clean-cols">
            <span v-for="col in it.columns" :key="col" class="tag col">{{ col }}</span>
          </div>
          <div class="clean-ops">
            <span v-for="op in it.ops" :key="op" class="tag op">{{ opLabel(op) }}</span>
            <span v-if="it.case && it.case !== 'none'" class="tag op">{{ caseLabel(it.case) }}</span>
            <span v-if="!it.ops.length && (!it.case || it.case === 'none')" class="tag muted">{{ t('table.clean_no_transform') }}</span>
          </div>
          <div class="clean-actions">
            <button class="mini-btn" @click="openEdit(i)" :title="t('clean.edit')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button class="mini-btn danger" @click="deleteItem(i)" title="Remove">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="!items.length" class="empty-state" style="margin-bottom:10px;">
        <span class="es-title">{{ t('clean.configure') }}</span>
        <span class="es-sub">{{ t('table.clean_empty_sub') }}</span>
      </div>

      <!-- Add button (always visible) -->
      <button class="add-rule" @click="openAdd">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        {{ t('clean.configure') }}
      </button>

      <!-- Modal -->
      <teleport to="body">
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal">

            <div class="modal-head">
              <h3>{{ editIdx === null ? t('clean.new') : t('clean.edit') }}</h3>
              <p>{{ t('clean.modal_sub') }}</p>
            </div>

            <div class="modal-body">

              <!-- Columns -->
              <div class="panel-sub">{{ t('clean.cols') }}</div>
              <div class="toggle-list">
                <div v-for="col in effectiveColumns" :key="col"
                  class="toggle-row" :class="{ on: isColOn(col) }"
                  @click="toggleCol(col)">
                  <span class="tr-name">{{ col }}</span>
                  <label class="switch" @click.prevent>
                    <input type="checkbox" :checked="isColOn(col)">
                    <span class="track"></span>
                  </label>
                </div>
              </div>

              <!-- Operations -->
              <div class="panel-sub mt">{{ t('clean.ops') }}</div>
              <div class="toggle-list">
                <div v-for="op in ['trim','collapse','accents','special']" :key="op"
                  class="toggle-row" :class="{ on: isOpOn(op) }"
                  @click="toggleOp(op)">
                  <span class="tr-name">{{ opLabel(op) }}</span>
                  <label class="switch" @click.prevent>
                    <input type="checkbox" :checked="isOpOn(op)">
                    <span class="track"></span>
                  </label>
                </div>
              </div>

              <!-- Case -->
              <div class="field" style="margin-top:14px;">
                <span class="field-label">{{ t('clean.case') }}</span>
                <span class="seg">
                  <button v-for="c in ['none','lower','upper','title']" :key="c"
                    :class="{ active: draft.case === c }"
                    @click="setCase(c)">{{ caseLabel(c) }}</button>
                </span>
              </div>

            </div>

            <div class="modal-foot">
              <button class="btn btn-ghost" @click="closeModal">{{ t('modal.cancel') }}</button>
              <button class="btn btn-primary" @click="saveModal" :disabled="!canSave">
                {{ editIdx === null ? t('modal.add') : t('modal.save') }}
              </button>
            </div>

          </div>
        </div>
      </teleport>

    </div>
  `,
};
