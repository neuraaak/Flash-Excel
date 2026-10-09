const STRATEGIES = ['value', 'forward', 'backward'];

export default {
  name: 'FillTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],
  data() { return { strategies: STRATEGIES, draftValue: '' }; },
  computed: {
    t() { return this.i18n.t; },
    effectiveColumns() {
      return this.columns.length ? this.columns : (this.payload.columns || []);
    },
    selected() {
      const s = this.payload.columns;
      return Array.isArray(s) ? s : [];
    },
    strategy() { return this.payload.strategy || 'value'; },
  },
  watch: {
    payload: {
      immediate: true,
      handler(v) { this.draftValue = v.value ?? ''; },
    },
  },
  methods: {
    isOn(col) { return this.selected.includes(col); },
    strategyLabel(s) { return this.t('fill.strategy_' + s); },
    // The model requires `value` when strategy is "value", and ignores it
    // otherwise: send null rather than an empty string for the other two.
    emit(columns, strategy, value) {
      this.$emit('update:payload', {
        action: 'fill_nulls',
        columns,
        strategy,
        value: strategy === 'value' ? value : null,
      });
    },
    toggle(col) {
      const set = new Set(this.selected);
      if (set.has(col)) set.delete(col); else set.add(col);
      this.emit(this.effectiveColumns.filter(c => set.has(c)), this.strategy, this.draftValue);
    },
    setStrategy(s) { this.emit(this.selected, s, this.draftValue); },
    onValue() { this.emit(this.selected, this.strategy, this.draftValue); },
  },
  template: `
    <div>
      <div class="row-between" style="margin-bottom:10px;">
        <span class="panel-sub" style="margin:0;">{{ t('table.fill_cols') }}</span>
        <span style="font-size:var(--fs-xs);color:var(--text_secondary);">{{ t('table.fill_selected', { n: selected.length, total: effectiveColumns.length }) }}</span>
      </div>
      <div class="toggle-list">
        <div v-for="col in effectiveColumns" :key="col" class="toggle-row" :class="{ on: isOn(col) }">
          <span class="tr-name">{{ col }}</span>
          <label class="switch">
            <input type="checkbox" :checked="isOn(col)" @change="toggle(col)">
            <span class="track"></span>
          </label>
        </div>
      </div>
      <div class="field" style="margin-top:16px;">
        <span class="field-label">{{ t('table.fill_strategy_label') }}</span>
        <span class="seg">
          <button v-for="s in strategies" :key="s" :class="{ active: strategy === s }" @click="setStrategy(s)">
            {{ strategyLabel(s) }}
          </button>
        </span>
      </div>
      <div v-if="strategy === 'value'" class="field">
        <span class="field-label">{{ t('table.fill_value_label') }}</span>
        <input class="input" v-model="draftValue" :placeholder="t('table.value')" @input="onValue" />
      </div>
      <div class="panel-hint">{{ t('table.fill_hint') }}</div>
    </div>
  `,
};
