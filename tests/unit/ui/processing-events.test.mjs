import assert from 'node:assert/strict';
import test from 'node:test';
import Processing from '../../../src/flash_excel/ui/web/js/pages/Processing.js';

function page() {
  const instance = {
    ...Processing.data(),
    totalSteps: 4,
    autoScroll: false,
    runState: 'running',
    fileStates: [{ status: 'pending', progress: 0 }, { status: 'pending', progress: 0 }],
    i18n: { t: (key, params) => `${key} ${JSON.stringify(params ?? {})}` },
  };
  for (const [name, method] of Object.entries(Processing.methods)) instance[name] = method.bind(instance);
  return instance;
}

test('step progress belongs to the event file', () => {
  const instance = page();
  instance.onFlashEvent('step', { file_index: 1, step_index: 1, step_name: 'drop_columns', rows_in: 10, rows_out: 10 });
  assert.deepEqual(instance.fileStates, [{ status: 'pending', progress: 0 }, { status: 'running', progress: 50 }]);
  assert.equal(instance.logs[0].level, 'step');
});

test('a completed file adds its row count and finishes its progress', () => {
  const instance = page();
  instance.stats.rows_out = 7;
  instance.onFlashEvent('done', { file_index: 1, rows_out: 10, elapsed_s: 1, output_path: 'output.csv' });
  assert.equal(instance.stats.rows_out, 17);
  assert.deepEqual(instance.fileStates[1], { status: 'done', progress: 100 });
  assert.equal(instance.fileStates[0].status, 'pending');
});

test('batch completion skips unfinished files and preserves an explicit stop', () => {
  const instance = page();
  instance.fileStates[0] = { status: 'done', progress: 100 };
  instance.onFlashEvent('batch_done', { succeeded: 1, total: 2, elapsed_s: 3 });
  assert.equal(instance.runState, 'error');
  assert.equal(instance.fileStates[0].status, 'done');
  assert.equal(instance.fileStates[1].status, 'skipped');
  assert.equal(instance.stats.elapsed_s, 3);
  instance.runState = 'stopped';
  instance.onFlashEvent('batch_done', { succeeded: 2, total: 2, elapsed_s: 4 });
  assert.equal(instance.runState, 'stopped');
});

test('a successful batch finishes the run', () => {
  const instance = page();
  instance.onFlashEvent('batch_done', { succeeded: 2, total: 2, elapsed_s: 3 });
  assert.equal(instance.runState, 'done');
});

for (const [mode, fatal, expected] of [['skip', false, 'skipped'], ['ignore', false, 'skipped'], ['stop', false, 'error'], ['skip', true, 'error']]) {
  test(`file error: mode=${mode}, fatal=${fatal}`, () => {
    const instance = page();
    instance.outputConfig.error_mode = mode;
    instance.onFlashEvent('error', { file_index: 1, message: 'Invalid column', fatal });
    assert.equal(instance.stats.errors, 1);
    assert.equal(instance.fileStates[1].status, expected);
    assert.equal(instance.fileStates[0].status, 'pending');
    assert.equal(instance.logs[0].message, 'Invalid column');
  });
}

test('dropped files are ignored during a run and accepted when idle', () => {
  const instance = page();
  const files = [{ path: 'input.csv' }];
  instance.onFlashEvent('files_dropped', { files });
  assert.deepEqual(instance.files, []);
  instance.runState = 'idle';
  instance.onFlashEvent('files_dropped', { files });
  assert.deepEqual(instance.files, files);
  assert.deepEqual(instance.fileStates, [{ status: 'pending', progress: 0 }]);
});

test('log events count warnings and support translated or raw messages', () => {
  const instance = page();
  instance.onFlashEvent('log', { level: 'warn', message: 'Raw warning' });
  instance.onFlashEvent('log', { level: 'info', key: 'log.run_stopped', params: { count: 2 } });
  assert.equal(instance.stats.warnings, 1);
  assert.equal(instance.logs[0].message, 'Raw warning');
  assert.match(instance.logs[1].message, /log\.run_stopped.*2/);
});

test('events without a matching file still update batch statistics', () => {
  const instance = page();
  instance.onFlashEvent('error', { file_index: 99, message: 'Batch failure', fatal: true });
  assert.equal(instance.stats.errors, 1);
  assert.ok(instance.fileStates.every(file => file.status === 'pending'));
});
