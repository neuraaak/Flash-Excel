// Shared registry of pipeline steps: canonical order + i18n keys.
// Used by ActionSteps.js (preset configuration) and Processing.js (console
// + preview) to show a translated name instead of the raw technical action
// (e.g. "rename_columns").

// drop_columns and fill_nulls sit at their RECOMMENDED_ACTION_ORDER positions
// (core/models.py); the relative order of the pre-existing steps is left as it
// was, since it decides the execution order of every preset saved from the UI.
export const STEP_ACTIONS = [
  'rename_columns', 'select_columns', 'drop_columns', 'cast_types',
  'replace_values', 'clean_text', 'fill_nulls', 'add_computed_column',
  'filter_rows', 'deduplicate_rows', 'sort_rows', 'reorder_columns',
];

const STEP_I18N_KEYS = {
  rename_columns: 'steps.rename',
  select_columns: 'steps.select',
  drop_columns: 'steps.drop',
  cast_types: 'steps.cast',
  replace_values: 'steps.replace',
  fill_nulls: 'steps.fill',
  clean_text: 'steps.clean',
  add_computed_column: 'steps.computed',
  filter_rows: 'steps.filter',
  deduplicate_rows: 'steps.dedupe',
  sort_rows: 'steps.sort',
  reorder_columns: 'steps.reorder',
};

/** Translated name of a step (falls back to the technical action). */
export function stepLabel(action, t) {
  const key = STEP_I18N_KEYS[action];
  return key ? t(key) : action;
}

/** Translated description of a step. */
export function stepDesc(action, t) {
  const key = STEP_I18N_KEYS[action];
  return key ? t(`${key}.desc`) : '';
}
