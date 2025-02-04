const baseConfig = require('./jest.config');

module.exports = {
  ...baseConfig,
  testRegex: '/__tests__/performance/.*\\.bench\\.(ts|tsx)$',
  testEnvironment: 'jest-bench/environment',
  reporters: ['default', 'jest-bench/reporter'],
  testRunner: 'jest-bench/runner',
  verbose: true,
  setupFilesAfterEnv: [
    ...baseConfig.setupFilesAfterEnv,
    'jest-bench/setup'
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  globals: {
    ...baseConfig.globals,
    'ts-jest': {
      ...baseConfig.globals['ts-jest'],
      isolatedModules: true,
    },
  },
  // Benchmark specific settings
  bench: {
    iterations: 10000, // Number of iterations
    warmupIterations: 100, // Warmup iterations
    threshold: 10, // Percentage threshold for performance regression
    failOnThreshold: true, // Fail if threshold is exceeded
    compareStats: ['mean', 'median', 'stddev'], // Stats to compare
    outputFormat: ['console', 'json'], // Output formats
    outputFile: 'benchmark-results.json', // Results file
  },
}; 