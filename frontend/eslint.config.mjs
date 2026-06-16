import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import unicornPlugin from 'eslint-plugin-unicorn';
import litPlugin from 'eslint-plugin-lit';
import simpleImportSortPlugin from 'eslint-plugin-simple-import-sort';
import jsdocPlugin from 'eslint-plugin-jsdoc';
import sonarjsPlugin from 'eslint-plugin-sonarjs';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  unicornPlugin.configs['flat/recommended'],
  litPlugin.configs['flat/recommended'],
  jsdocPlugin.configs['flat/recommended'],
  sonarjsPlugin.configs.recommended,
  {
    plugins: {
      'simple-import-sort': simpleImportSortPlugin,
    },
    rules: {
      'simple-import-sort/imports': 'error',
      'simple-import-sort/exports': 'error',
    },
  },
  {
    languageOptions: {
      parserOptions: {
        project: './tsconfig.eslint.json',
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      'max-lines': ['warn', { max: 500, skipBlankLines: true, skipComments: true }],
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-non-null-assertion': 'warn',
      'unicorn/filename-case': [
        'error',
        {
          cases: { kebabCase: true },
          ignore: ['^\\[[a-z]+\\]', '^\\.', '/generated/'],
        },
      ],
      'unicorn/prevent-abbreviations': 'off',
      'unicorn/no-null': 'off',
      'sonarjs/no-duplicate-string': ['warn', { threshold: 5 }],
    },
  },
  {
    files: ['**/*.test.ts', '**/*.test.tsx', '**/*.spec.ts', '**/*.spec.tsx'],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/unbound-method': 'off',
      'sonarjs/no-hardcoded-passwords': 'off',
      'max-lines': 'off',
    },
  },
  {
    files: ['**/*.stories.ts', '**/*.stories.tsx'],
    rules: {
      'sonarjs/no-duplicate-string': 'off',
      'unicorn/filename-case': 'off',
      'max-lines': 'off',
      '@typescript-eslint/no-unsafe-assignment': 'off',
    },
  },
  {
    // Generated files have different constraints — disable rules that clash with orval output.
    files: ['**/generated/**'],
    rules: {
      'unicorn/filename-case': 'off',
      '@typescript-eslint/no-redundant-type-constituents': 'off',
      '@typescript-eslint/no-unsafe-call': 'off',
      // orval's fetch client always merges options?.headers (typed HeadersInit, which
      // includes an array form) into the request headers object.
      '@typescript-eslint/no-misused-spread': 'off',
      // orval passes `customFetch<void>(...)` for 204 responses. The rule hard-disallows
      // void in call-expression generics (vs. type references) regardless of options.
      '@typescript-eslint/no-invalid-void-type': 'off',
    },
  },
);
