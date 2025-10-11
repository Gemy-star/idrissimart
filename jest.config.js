/**
 * For a detailed explanation regarding each configuration property, visit:
 * https://jestjs.io/docs/configuration
 */

/** @type {import('jest').Config} */
const config = {
  // All imported modules in your tests should be mocked automatically
  // automock: false,

  // Stop running tests after `n` failures
  // bail: 0,

  // The directory where Jest should store its cached dependency information
  // cacheDirectory: "/tmp/jest_rs",

  // Automatically clear mock calls, instances, contexts and results before every test
  clearMocks: true,

  // Indicates whether the coverage information should be collected while executing the test
  collectCoverage: true,

  // An array of glob patterns indicating a set of files for which coverage information should be collected
  // collectCoverageFrom: undefined,
  collectCoverageFrom: ['orange_cyberrating/static/js/**/*.js'],

  // The directory where Jest should output its coverage files
  coverageDirectory: 'reports',

  // An array of regexp pattern strings used to skip coverage collection
  // coveragePathIgnorePatterns: [
  //   "/node_modules/"
  // ],

  // Indicates which provider should be used to instrument code for coverage
  coverageProvider: 'v8',

  // A list of reporter names that Jest uses when writing coverage reports
  coverageReporters: ['json', 'text', 'cobertura', 'lcov', 'lcovonly'],

  // An object that configures minimum threshold enforcement for coverage results
  // coverageThreshold: undefined,

  // A path to a custom dependency extractor
  // dependencyExtractor: undefined,

  // Make calling deprecated APIs throw helpful error messages
  // errorOnDeprecated: false,

  // The default configuration for fake timers
  // fakeTimers: {
  //   "enableGlobally": false
  // },

  // Force coverage collection from ignored files using an array of glob patterns
  // forceCoverageMatch: [],

  // A path to a module which exports an async function that is triggered once before all test suites
  // globalSetup: undefined,

  // A path to a module which exports an async function that is triggered once after all test suites
  // globalTeardown: undefined,

  // A set of global variables that need to be available in all test environments
  // globals: {},

  // The maximum amount of workers used to run your tests. Can be specified as % or a number. E.g. maxWorkers: 10% will use 10% of your CPU amount + 1 as the maximum worker number. maxWorkers: 2 will use a maximum of 2 workers.
  // maxWorkers: "50%",

  // An array of directory names to be searched recursively up from the requiring module's location
  moduleDirectories: ['node_modules', 'orange_cyberrating/static'],

  // An array of file extensions your modules use
  moduleFileExtensions: [
    'js',
    'mjs',
    // "cjs",
    // "jsx",
    // "ts",
    // "tsx",
    // "json",
    // "node"
  ],

  // A map from regular expressions to module names or to arrays of module names that allow to stub out resources with a single module
  moduleNameMapper: {
    'api-utils': '<rootDir>/orange_cyberrating/static/js/utils/modules/api-module-utils.js',
    'onep-utils': '<rootDir>/orange_cyberrating/static/js/utils/modules/onep-utils.js',
    'onep-home': '<rootDir>/orange_cyberrating/static/js/onep/home/home.js',
    'onep-rating-history': '<rootDir>/orange_cyberrating/static/js/onep/rating/rating-history.js',
    'buttons-html5': '<rootDir>/orange_cyberrating/static/DataTables-2.2.1/buttons.html5.min.mjs',
    'change-entity': '<rootDir>/orange_cyberrating/static/js/utils/modules/change-entity.js',
    'datatable-module': '<rootDir>/orange_cyberrating/static/js/utils/modules/datatable-module.js',
    'datatables.net': '<rootDir>/orange_cyberrating/static/DataTables-2.2.1/dataTables.min.mjs',
    'dom-element-creator': '<rootDir>/orange_cyberrating/static/js/utils/modules/dom-element-creator.js',
    'highcharts-utils': '<rootDir>/orange_cyberrating/static/js/charts/highcharts-utils.js',
    jquery: '<rootDir>/orange_cyberrating/static/DataTables-2.2.1/jquery.3.7.1.mjs',
    'set-entity-scope-title': '<rootDir>/orange_cyberrating/static/js/utils/modules/set-entity-scope-title.js',
    '@popperjs/core': '<rootDir>/orange_cyberrating/static/boosted/@popperjs/core/dist/esm/popper.js',
    boosted: '<rootDir>/orange_cyberrating/static/boosted/js/boosted.esm.min.js',
    highcharts: '<rootDir>/orange_cyberrating/static/Highcharts-12.1.2/es-modules/masters/highcharts.src.js',
    gettext: '<rootDir>/orange_cyberrating/static/static/jsi18n/en/django.js',
  },

  // An array of regexp pattern strings, matched against all module paths before considered 'visible' to the module loader
  // modulePathIgnorePatterns: [],

  // Activates notifications for test results
  // notify: false,

  // An enum that specifies notification mode. Requires { notify: true }
  // notifyMode: "failure-change",

  // A preset that is used as a base for Jest's configuration
  // preset: undefined,

  // Run tests from one or more projects
  // projects: undefined,

  // Use this configuration option to add custom reporters to Jest
  // reporters: undefined,
  reporters: [
    'default',
    // 'jest-junit' to enable GitLab unit test report integration
    [
      'jest-junit',
      {
        outputDirectory: 'reports',
        outputName: 'node-test.xunit.xml',
      },
    ],
    // [OPTIONAL] only if using SonarQube
    // 'jest-sonar' to enable SonarQube unit test report integration
    [
      'jest-sonar',
      {
        outputDirectory: 'reports',
        outputName: 'node-test.sonar.xml',
      },
    ],
  ],

  // Automatically reset mock state before every test
  // resetMocks: false,

  // Reset the module registry before running each individual test
  // resetModules: false,

  // A path to a custom resolver
  // resolver: undefined,

  // Automatically restore mock state and implementation before every test
  // restoreMocks: false,

  // The root directory that Jest should scan for tests and modules within
  // rootDir: undefined,

  // A list of paths to directories that Jest should use to search for files in
  roots: ['<rootDir>/tests_javascript'],

  // Allows you to use a custom runner instead of Jest's default test runner
  // runner: "jest-runner",

  // The paths to modules that run some code to configure or set up the testing environment before each test
  setupFiles: ['./tests_javascript/mock-translate.js'],

  // A list of paths to modules that run some code to configure or set up the testing framework before each test
  // setupFilesAfterEnv: [],

  // The number of seconds after which a test is considered as slow and reported as such in the results.
  // slowTestThreshold: 5,

  // A list of paths to snapshot serializer modules Jest should use for snapshot testing
  // snapshotSerializers: [],

  // The test environment that will be used for testing
  // testEnvironment: "jest-environment-node",
  testEnvironment: 'jsdom',

  // Options that will be passed to the testEnvironment
  // testEnvironmentOptions: {},

  // Adds a location field to test results
  // testLocationInResults: false,

  // The glob patterns Jest uses to detect test files
  // testMatch: [
  //   "**/__tests__/**/*.[jt]s?(x)",
  //   "**/?(*.)+(spec|test).[tj]s?(x)"
  // ],
  // testMatch: ['tests_onep/one_p/**/*.test.js', '!**/node_modules/**'],

  // An array of regexp pattern strings that are matched against all test paths, matched tests are skipped
  // testPathIgnorePatterns: [
  //   "/node_modules/"
  // ],

  // The regexp pattern or array of patterns that Jest uses to detect test files
  // testRegex: [],

  // This option allows the use of a custom results processor
  // testResultsProcessor: undefined,

  // This option allows use of a custom test runner
  // testRunner: "jest-circus/runner",

  // A map from regular expressions to paths to transformers
  // transform: undefined,

  // An array of regexp pattern strings that are matched against all source file paths, matched files will skip transformation
  // transformIgnorePatterns: [
  //   "/node_modules/",
  //   "\\.pnp\\.[^\\/]+$"
  // ],
  // preset: 'ts-jest',
  // transform: {
  //   '^.+\\.(ts|tsx)?$': 'ts-jest',
  //   '^.+\\.(js|jsx)$': 'babel-jest',
  // },
  transform: {},

  // An array of regexp pattern strings that are matched against all modules before the module loader will automatically return a mock for them
  // unmockedModulePathPatterns: undefined,

  // Indicates whether each individual test should be reported during the run
  // verbose: undefined,

  // An array of regexp patterns that are matched against all source file paths before re-running tests in watch mode
  // watchPathIgnorePatterns: [],

  // Whether to use watchman for file crawling
  // watchman: true,
}

export default config
