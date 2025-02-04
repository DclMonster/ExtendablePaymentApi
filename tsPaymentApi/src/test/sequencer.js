const Sequencer = require('@jest/test-sequencer').default;

class CustomSequencer extends Sequencer {
  sort(tests) {
    // Sort tests into groups: unit -> integration -> regression -> performance
    const testGroups = {
      unit: [],
      integration: [],
      regression: [],
      performance: [],
      other: [],
    };

    tests.forEach(test => {
      if (test.path.includes('/__tests__/unit/')) {
        testGroups.unit.push(test);
      } else if (test.path.includes('/__tests__/integration/')) {
        testGroups.integration.push(test);
      } else if (test.path.includes('/__tests__/regression/')) {
        testGroups.regression.push(test);
      } else if (test.path.includes('/__tests__/performance/')) {
        testGroups.performance.push(test);
      } else {
        testGroups.other.push(test);
      }
    });

    // Sort each group alphabetically
    Object.values(testGroups).forEach(group => {
      group.sort((a, b) => (a.path > b.path ? 1 : -1));
    });

    // Return all tests in the desired order
    return [
      ...testGroups.unit,
      ...testGroups.integration,
      ...testGroups.regression,
      ...testGroups.performance,
      ...testGroups.other,
    ];
  }
}

module.exports = CustomSequencer; 