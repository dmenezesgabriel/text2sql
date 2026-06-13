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
        fetch: {
          includeHttpResponseReturnType: false,
        },
      },
      mock: {
        generators: [{ type: 'msw', delay: false }],
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
});
