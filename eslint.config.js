import globals from 'globals'
import pluginJs from '@eslint/js'
import pluginJest from 'eslint-plugin-jest'

/** @type {import('eslint').Linter.Config[]} */
export default [
  {
    ignores: [
      './static/asset/*',
      './static/boosted/*',
      './static/Datatables/*',
      './static/DataTables-2.2.1/*',
      './static/fontawesome/*',
      './static/fonts/*',
      './static/Highcharts-9.2.2/*',
      './static/Highcharts-Maps-9.2.2/*',
      './static/Highcharts-Stock-9.2.2/*',
      './static/js/daterangepicker/*',
      './static/js/bootstrap-multiselect/*',
      './static/js/select2/*',
      './static/js/ipaddr.min.js',
      './static/js/bootstrap-table.min.js',
      './static/js/jquery.min.js',
      './static/js/reporting/html2pdf.bundle.min.js',
    ],
    languageOptions: { globals: { ...globals.browser, ...globals.jquery } },
  },
  pluginJs.configs.recommended,
  {
    // update this to match your test files
    files: ['**/*.spec.js', '**/*.test.js'],
    plugins: { jest: pluginJest },
    languageOptions: {
      globals: pluginJest.environments.globals.globals,
    },
    rules: {
      'jest/no-disabled-tests': 'warn',
      'jest/no-focused-tests': 'error',
      'jest/no-identical-title': 'error',
      'jest/prefer-to-have-length': 'warn',
      'jest/valid-expect': 'error',
    },
  },
]
