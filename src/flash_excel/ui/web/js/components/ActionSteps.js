import { STEP_ACTIONS, stepLabel, stepDesc } from '../steps-registry.js';
import RenameTable from './tables/RenameTable.js';
import SelectTable from './tables/SelectTable.js';
import DropTable from './tables/DropTable.js';
import CastTable from './tables/CastTable.js';
import ReplaceTable from './tables/ReplaceTable.js';
import FillTable from './tables/FillTable.js';
import CleanTable from './tables/CleanTable.js';
import ComputedTable from './tables/ComputedTable.js';
import FilterTable from './tables/FilterTable.js';
import DeduplicateTable from './tables/DeduplicateTable.js';
import SortTable from './tables/SortTable.js';
import ReorderTable from './tables/ReorderTable.js';

const EDITOR_MAP = {
  rename_columns: RenameTable,
  select_columns: SelectTable,
  drop_columns: DropTable,
  cast_types: CastTable,
  replace_values: ReplaceTable,
  fill_nulls: FillTable,
  clean_text: CleanTable,
  add_computed_column: ComputedTable,
  filter_rows: FilterTable,
  deduplicate_rows: DeduplicateTable,
  sort_rows: SortTable,
  reorder_columns: ReorderTable,
};

/**
 * Returns the columns coming out of a given step.
 */
function applyStepToColumns(action, payload, cols) {
  if (!payload || !cols.length) return cols;
  switch (action) {
    case 'rename_columns': {
      const mapping = payload.mapping || {};
      if (!Object.keys(mapping).length) return cols;
      return cols.map(c => mapping[c] ?? c);
    }
    case 'select_columns': {
      const kept = payload.columns || [];
      if (!kept.length) return cols;
      return kept.filter(c => cols.includes(c));
    }
    case 'drop_columns': {
      const removed = new Set(payload.columns || []);
      if (!removed.size) return cols;
      return cols.filter(c => !removed.has(c));
    }
    case 'add_computed_column': {
      const newCols = (payload.items || []).map(i => i.target).filter(Boolean);
      return [...cols, ...newCols];
    }
    case 'reorder_columns': {
      const order = payload.columns || [];
      if (!order.length) return cols;
      return order.filter(c => cols.includes(c));
    }
    default:
      return cols;
  }
}

/**
 * Returns the schema (col -> type) coming out of a given step.
 * Types are either Polars dtype names (e.g. "String", "Int64") or the JS
 * cast names ("string", "int", "float", "bool", "date", "datetime").
 */
function applyStepToSchema(action, payload, schema) {
  if (!payload) return schema;
  switch (action) {
    case 'rename_columns': {
      const mapping = payload.mapping || {};
      if (!Object.keys(mapping).length) return schema;
      const result = {};
      for (const [k, v] of Object.entries(schema)) result[mapping[k] ?? k] = v;
      return result;
    }
    case 'select_columns': {
      const kept = new Set(payload.columns || []);
      if (!kept.size) return schema;
      return Object.fromEntries(Object.entries(schema).filter(([k]) => kept.has(k)));
    }
    case 'drop_columns': {
      const removed = new Set(payload.columns || []);
      if (!removed.size) return schema;
      return Object.fromEntries(Object.entries(schema).filter(([k]) => !removed.has(k)));
    }
    case 'cast_types': {
      const casts = payload.casts || {};
      if (!Object.keys(casts).length) return schema;
      return { ...schema, ...casts };
    }
    case 'add_computed_column': {
      const newEntries = (payload.items || [])
        .filter(i => i.target)
        .map(i => [i.target, 'string']);
      return { ...schema, ...Object.fromEntries(newEntries) };
    }
    case 'reorder_columns': {
      const order = payload.columns || [];
      if (!order.length) return schema;
      return Object.fromEntries(order.filter(c => c in schema).map(c => [c, schema[c]]));
    }
    default:
      return schema;
  }
}

function countPayload(p) {
  if (!p) return 0;
  if (p.mapping) return Object.keys(p.mapping).length;
  if (p.columns) return p.columns.length;
  if (p.casts) return Object.keys(p.casts).length;
  if (p.rules_by_column) return Object.keys(p.rules_by_column).length;
  if (p.items) return p.items.length;
  if (p.conditions) return p.conditions.length;
  if (p.subset) return p.subset.length;
  if (p.by) return p.by.length;
  return 0;
}

export default {
  name: 'ActionSteps',
  components: { ...EDITOR_MAP },
  props: {
    columns: { type: Array, default: () => [] },
    schema: { type: Object, default: () => ({}) },
    payloads: { type: Object, default: () => ({}) },
  },
  emits: ['update:payloads'],
  inject: ['i18n'],
  data() { return { activeAction: null }; },
  computed: {
    t() { return this.i18n.t; },
    steps() {
      return STEP_ACTIONS.map(action => ({
        action,
        label: stepLabel(action, this.t),
        desc: stepDesc(action, this.t),
      }));
    },

    // Columns available as input to each step
    columnsByStep() {
      let cols = [...this.columns];
      const result = {};
      for (const step of this.steps) {
        result[step.action] = cols;
        cols = applyStepToColumns(step.action, this.payloads[step.action], cols);
      }
      return result;
    },

    // Schema (col -> type) available as input to each step
    schemaByStep() {
      let schema = { ...this.schema };
      const result = {};
      for (const step of this.steps) {
        result[step.action] = schema;
        schema = applyStepToSchema(step.action, this.payloads[step.action], schema);
      }
      return result;
    },

    activeEditor() { return this.activeAction ? EDITOR_MAP[this.activeAction] : null; },
    activePayload() { return this.activeAction ? (this.payloads[this.activeAction] || {}) : {}; },
    activeStep() { return this.steps.find(s => s.action === this.activeAction); },
    activeCount() { return countPayload(this.activePayload); },
    activeColumns() { return this.activeAction ? (this.columnsByStep[this.activeAction] || this.columns) : this.columns; },
    activeSchema() { return this.activeAction ? (this.schemaByStep[this.activeAction] || this.schema) : this.schema; },
  },
  methods: {
    countFor(action) { return countPayload(this.payloads[action]); },
    onPayload(payload) {
      this.$emit('update:payloads', { ...this.payloads, [this.activeAction]: payload });
    },
  },
  template: `
    <div class="config">

      <!-- Left: action list -->
      <div class="action-list">
        <div v-for="s in steps" :key="s.action"
          class="action-item"
          :class="{ active: activeAction === s.action, on: countFor(s.action) > 0 }"
          @click="activeAction = s.action">
          <span class="ai-status"><span class="ring"></span></span>
          <span class="ai-name">{{ s.label }}</span>
          <span v-if="countFor(s.action) > 0" class="ai-count">{{ countFor(s.action) }}</span>
          <span class="ai-info" :title="s.desc" @click.stop>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>
          </span>
        </div>
      </div>

      <!-- Right: config panel -->
      <div class="panel">
        <div v-if="!activeAction" class="panel-empty">
          {{ t('steps.empty') }}
        </div>
        <template v-else>
          <div class="panel-head">
            <div class="ph-text">
              <h3>{{ activeStep.label }}</h3>
              <p>{{ activeStep.desc }}</p>
            </div>
            <span class="ph-count">{{ activeCount }} {{ t('steps.configured') }}</span>
          </div>
          <div class="panel-body">
            <component :is="activeEditor"
              :columns="activeColumns"
              :schema="activeSchema"
              :payload="activePayload"
              @update:payload="onPayload" />
          </div>
        </template>
      </div>

    </div>
  `,
};
