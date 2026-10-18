/**
 * JS wrapper around window.pywebview.api.
 * All methods unwrap {ok, data} and throw on error.
 */

async function call(method, ...args) {
  if (!globalThis.pywebview?.api) {
    throw new Error(`pywebview.api not ready (calling ${method})`);
  }
  const result = await globalThis.pywebview.api[method](...args);
  if (!result.ok) throw new Error(result.error || 'Unknown error');
  return result.data;
}

export const api = {
  // Presets
  getPresets:   ()                   => call('get_presets'),
  loadPreset:   (path)               => call('load_preset', path),
  newPreset:    (name)               => call('new_preset', name),
  savePreset:   (name, steps)        => call('save_preset', name, steps),
  deletePreset: (path)               => call('delete_preset', path),
  exportPreset: (path)               => call('export_preset', path),

  // File
  openFileDialog:   ()               => call('open_file_dialog'),
  openFilesDialog:  ()               => call('open_files_dialog'),
  openFolderDialog: ()               => call('open_folder_dialog'),
  clearFile:        ()               => call('clear_file'),
  getSourceColumns: ()               => call('get_source_columns'),
  getDefaultOutputFolder: ()         => call('get_default_output_folder'),

  // Steps
  getStepPayload: (action)           => call('get_step_payload', action),
  setStepPayload: (action, payload)  => call('set_step_payload', action, payload),

  // Processing
  getScheduleCommand: (presetPath, filePaths, outputConfig, name = null, time = '08:00') =>
    call('get_schedule_command', presetPath, filePaths, outputConfig, name, time),
  createScheduledTask: (presetPath, filePaths, outputConfig, name, time, confirmed) =>
    call('create_scheduled_task', presetPath, filePaths, outputConfig, name, time, confirmed),
  createExecutionLauncher: (presetPath, filePaths, outputConfig, name) =>
    call('create_execution_launcher', presetPath, filePaths, outputConfig, name),
  previewPreset: (presetPath, filePath) => call('preview_preset', presetPath, filePath),
  runPreset: (presetPath, filePaths, outputConfig) =>
    call('run_preset', presetPath, filePaths, outputConfig),
  stopRun: () => call('stop_run'),

  // Settings & themes
  getAppConfig:   ()                 => call('get_app_config'),
  saveAppConfig:  (palette, mode, locale = 'en', csvSeparator = 'auto', csvDecimal = 'auto', presetSources = null) =>
                                     call('save_app_config', palette, mode, locale, csvSeparator, csvDecimal, presetSources),
  getThemes:      ()                 => call('get_themes'),

  // Version & auto-update
  getVersion:   ()                   => call('get_version'),
  checkUpdate:  ()                   => call('check_update'),
  applyUpdate:  ()                   => call('apply_update'),
};
