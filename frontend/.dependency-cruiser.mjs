/** @type {import('dependency-cruiser').IConfiguration} */
export default {
  forbidden: [
    {
      name: 'no-circular',
      severity: 'error',
      comment: 'Circular dependencies are not allowed.',
      from: {},
      to: { circular: true },
    },
    {
      name: 'no-orphans',
      severity: 'warn',
      comment: 'Modules that are not imported anywhere.',
      from: { orphan: true },
      to: {},
    },
    {
      name: 'no-deprecated-core',
      comment:
        'A module depends on a deprecated core (node) module.',
      severity: 'warn',
      from: {},
      to: {
        dependencyTypes: ['core'],
        path: '^(punycode|domain|constants|sys|_linklist|_stream_wrap)$',
      },
    },
    {
      name: 'shared-must-not-depend-on-features',
      comment:
        'Shared layer must not import from features, widgets, pages, or app.',
      severity: 'error',
      from: { path: '^src/shared/' },
      to: {
        path: '^src/(features|widgets|pages|app)/',
      },
    },
    {
      name: 'entities-must-not-depend-on-features',
      comment:
        'Entities must not depend on features, widgets, pages.',
      severity: 'error',
      from: { path: '^src/entities/' },
      to: {
        path: '^src/(features|widgets|pages)/',
      },
    },
    {
      name: 'features-must-not-depend-on-pages',
      comment:
        'Features should not depend on page-level modules.',
      severity: 'error',
      from: { path: '^src/features/' },
      to: { path: '^src/pages/' },
    },
    {
      name: 'not-to-test',
      comment:
        'Do not import test modules from non-test code.',
      severity: 'error',
      from: { pathNot: '\.(test|spec|stories)\.(ts|tsx)$' },
      to: { path: '\.(test|spec|stories)\.(ts|tsx)$' },
    },
    {
      name: 'not-to-dev-dep',
      severity: 'error',
      comment:
        'Production modules should not import dev dependencies.',
      from: { path: '^src/', pathNot: ['\\.(test|spec|stories)\\.(ts|tsx)$', '/test/', '/__tests__/'] },
      to: { dependencyTypes: ['npm-dev'] },
    },
  ],
  options: {
    doNotFollow: {
      path: 'node_modules',
    },
    tsPreCompilationDeps: true,
    tsConfig: {
      fileName: 'tsconfig.json',
    },
    enhancedResolveOptions: {
      exportsFields: ['exports'],
      conditionNames: ['import', 'require', 'default'],
    },
    reporterOptions: {
      dot: {
        collapsePattern: 'node_modules/[^/]+',
      },
      archi: {
        collapsePattern:
          '^(node_modules|src/shared|src/entities|src/features|src/widgets|src/pages|src/app)',
      },
    },
  },
};
