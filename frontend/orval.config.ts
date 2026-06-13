import { defineConfig } from 'orval';

export default defineConfig({
  text2sql: {
    input: {
      target: 'http://localhost:8000/openapi.json',
      unsafeDisableValidation: true,
    },
    output: {
      target: './src/shared/api/generated/endpoints.ts',
      schemas: './src/shared/api/generated/schemas',
      client: 'fetch',
      mode: 'split',
      clean: true,
      override: {
        mutator: {
          path: './src/shared/api/mutator.ts',
          name: 'customFetch',
        },
      },
      mock: {
        generators: [{ type: 'msw', delay: false }],
      },
    },
    hooks: {
      afterAllFilesWrite:
        'prettier --write && eslint --fix src/shared/api/generated/ --no-warn-ignored',
    },
  },
});
