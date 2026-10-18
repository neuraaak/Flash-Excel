const js = require('@eslint/js');
const globals = require('globals');

module.exports = [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        // Injected by pywebview into the page, not by the browser.
        pywebview: 'readonly',
      },
    },
    rules: {
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-var': 'error',
      'prefer-const': 'error',
      eqeqeq: ['error', 'always'],
      // `debug` is allowed: it is how the UI traces itself in the pywebview
      // devtools. Plain `console.log` stays a warning.
      'no-console': ['warn', { allow: ['warn', 'error', 'info', 'debug'] }],
      'prefer-arrow-callback': 'error',
      // Left off on purpose: the existing concatenations are readable, and
      // --fix rewrites them into templates with stray padding.
      'prefer-template': 'off',
      'object-shorthand': ['error', 'always'],
    },
  },
  {
    // Vendored third-party bundles (Vue, Tailwind, Lucide): not ours to lint.
    ignores: ['src/flash_excel/ui/web/js/vendor/', 'node_modules/'],
  },
];
