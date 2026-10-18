import { api } from '../api.js';

export default {
  name: 'ExecutionModal',
  props: { execution: { type: Object, required: true } },
  emits: ['close'],
  inject: ['i18n', 'showToast'],

  data() {
    return {
      name: '',
      time: '08:00',
      output: { ...this.execution.outputConfig },
      runtime: null,
      busy: false,
      error: '',
      pendingTask: null,
      createdTask: '',
      launcherPath: '',
    };
  },

  computed: {
    filePaths() { return this.execution.files.map(file => file.path); },
    canCreate() { return !!this.name.trim() && !this.busy; },
    canSchedule() { return this.canCreate && /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(this.time); },
  },

  async mounted() {
    this.$refs.closeButton?.focus();
    try {
      this.runtime = await api.getScheduleCommand(this.execution.presetPath, this.filePaths, this.output);
      this.name = this.runtime.task_name;
    } catch (e) {
      this.error = e.message;
    }
  },

  methods: {
    close() { if (!this.busy) this.$emit('close'); },
    async browseFolder() {
      try {
        const result = await api.openFolderDialog();
        if (!result.cancelled) this.output.folder = result.folder;
      } catch (e) { this.error = e.message; }
    },
    requestTask() {
      if (!this.canSchedule) return;
      this.error = '';
      this.pendingTask = { name: this.name.trim(), time: this.time, output: { ...this.output } };
      this.$nextTick(() => this.$refs.confirmCancel?.focus());
    },
    cancelTask() {
      if (this.busy) return;
      this.pendingTask = null;
      this.$nextTick(() => this.$refs.closeButton?.focus());
    },
    async confirmTask() {
      if (this.busy || !this.pendingTask) return;
      this.busy = true;
      this.error = '';
      const task = this.pendingTask;
      try {
        const result = await api.createScheduledTask(
          this.execution.presetPath, this.filePaths, task.output, task.name, task.time, true,
        );
        this.createdTask = result.task_name;
        this.pendingTask = null;
        this.$nextTick(() => this.$refs.closeButton?.focus());
        this.showToast(this.i18n.t('execution.task_created', { name: result.task_name }), 'success');
      } catch (e) { this.error = e.message; }
      finally { this.busy = false; }
    },
    async createLauncher() {
      if (!this.canCreate) return;
      this.busy = true;
      this.error = '';
      try {
        const result = await api.createExecutionLauncher(
          this.execution.presetPath, this.filePaths, this.output, this.name.trim(),
        );
        if (!result.cancelled) {
          this.launcherPath = result.dest;
          this.showToast(this.i18n.t('execution.launcher_created'), 'success');
        }
      } catch (e) { this.error = e.message; }
      finally { this.busy = false; }
    },
    async copyCommand() {
      if (!this.canCreate) return;
      this.busy = true;
      this.error = '';
      try {
        const result = await api.getScheduleCommand(
          this.execution.presetPath, this.filePaths, this.output, this.name.trim(), this.time,
        );
        if (result.command_too_long) {
          this.error = this.i18n.t('execution.command_too_long');
          return;
        }
        await navigator.clipboard.writeText(result.command);
        this.showToast(this.i18n.t('execution.command_copied'), 'success');
      } catch (e) { this.error = e.message; }
      finally { this.busy = false; }
    },
  },

  template: `
  <teleport to="body">
    <div class="modal-overlay" @click.self="close" @keydown.esc.stop="close">
      <div class="modal execution-dialog" role="dialog" aria-modal="true" aria-labelledby="execution-title">
        <div class="modal-head">
          <h3 id="execution-title">{{ i18n.t('execution.title') }}</h3>
          <button class="icon-btn" ref="closeButton" @click="close" :disabled="busy" :aria-label="i18n.t('execution.close')">×</button>
        </div>
        <div class="execution-body">
          <p class="schedule-hint">{{ i18n.t('execution.shared_hint') }}</p>
          <div class="execution-grid">
            <label class="execution-field"><span>{{ i18n.t('execution.name') }}</span>
              <input class="input" v-model="name" :disabled="busy" maxlength="200" />
            </label>
            <label class="execution-field"><span>{{ i18n.t('execution.time') }}</span>
              <input class="input" type="time" v-model="time" :disabled="busy" required />
            </label>
          </div>
          <div class="execution-summary">
            <span class="field-label">{{ i18n.t('proc.preset') }}</span>
            <p>{{ execution.presetPath }}</p>
            <span class="field-label">{{ i18n.t('execution.files', { count: execution.files.length }) }}</span>
            <ul><li v-for="file in execution.files" :key="file.path">{{ file.path }}</li></ul>
          </div>
          <label class="execution-field"><span>{{ i18n.t('proc.dest_folder') }}</span>
            <input class="input" v-model="output.folder" :disabled="busy" />
          </label>
          <button class="btn execution-browse" @click="browseFolder" :disabled="busy">{{ i18n.t('execution.browse') }}</button>
          <div class="execution-grid">
            <label class="execution-field"><span>{{ i18n.t('proc.format') }}</span>
              <select class="input" v-model="output.format" :disabled="busy">
                <option value="keep">{{ i18n.t('proc.fmt_keep') }}</option>
                <option value="xlsx">.xlsx</option><option value="csv">.csv</option><option value="parquet">.parquet</option>
              </select>
            </label>
            <label class="execution-field"><span>{{ i18n.t('proc.naming_pattern') }}</span>
              <input class="input" v-model="output.pattern" :disabled="busy" />
            </label>
          </div>
          <p class="schedule-hint">{{ i18n.t('execution.session_hint') }}</p>
          <p v-if="runtime" class="schedule-hint">{{ i18n.t(runtime.development ? 'execution.development' : 'execution.installed', { executable: runtime.executable }) }}</p>
          <p v-if="createdTask" class="execution-success" role="status">{{ i18n.t('execution.task_created', { name: createdTask }) }}</p>
          <p v-if="launcherPath" class="execution-success" role="status">{{ i18n.t('execution.launcher_saved', { path: launcherPath }) }}</p>
          <div class="execution-removal">
            <h4>{{ i18n.t('execution.remove_title') }}</h4>
            <ol>
              <li>{{ i18n.t('execution.remove_open') }}</li>
              <li>{{ i18n.t('execution.remove_select', { name: createdTask || name }) }}</li>
              <li>{{ i18n.t('execution.remove_action') }}</li>
            </ol>
            <p>{{ i18n.t('execution.remove_hint') }}</p>
          </div>
          <p v-if="error && !pendingTask" class="preview-error" role="alert">{{ error }}</p>
          <button class="link-btn" @click="copyCommand" :disabled="!canCreate">{{ i18n.t('execution.copy') }}</button>
        </div>
        <div class="modal-foot execution-actions">
          <button class="btn" @click="createLauncher" :disabled="!canCreate">{{ i18n.t('execution.launcher') }}</button>
          <button class="btn primary" @click="requestTask" :disabled="!canSchedule">{{ i18n.t('execution.schedule') }}</button>
        </div>
      </div>
    </div>
    <div v-if="pendingTask" class="modal-overlay" @click.self="cancelTask" @keydown.esc.stop="cancelTask">
      <div class="modal execution-confirm" role="alertdialog" aria-modal="true" aria-labelledby="execution-confirm-title">
        <div class="modal-head"><h3 id="execution-confirm-title">{{ i18n.t('execution.confirm_title') }}</h3></div>
        <div class="modal-body">
          <p>{{ i18n.t('execution.confirm_summary', { name: pendingTask.name, time: pendingTask.time }) }}</p>
          <p class="execution-warning">{{ i18n.t('execution.risk') }}</p>
          <p>{{ i18n.t('execution.confirm_removal') }}</p>
          <p v-if="error" class="preview-error" role="alert">{{ error }}</p>
        </div>
        <div class="modal-foot">
          <button class="btn" ref="confirmCancel" @click="cancelTask" :disabled="busy">{{ i18n.t('modal.cancel') }}</button>
          <button class="btn primary" @click="confirmTask" :disabled="busy">{{ i18n.t('execution.confirm') }}</button>
        </div>
      </div>
    </div>
  </teleport>`,
};
