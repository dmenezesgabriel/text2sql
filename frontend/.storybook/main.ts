import type { StorybookConfig } from '@storybook/web-components-vite';

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-docs',
    '@storybook/addon-a11y',
    '@storybook/experimental-addon-test',
    'msw-storybook-addon',
    // Serves an MCP endpoint at http://localhost:6006/mcp so agents can query
    // the component catalog. Consumed via .mcp.json at the repo root.
    '@storybook/addon-mcp',
  ],
  framework: {
    name: '@storybook/web-components-vite',
    options: {},
  },
  core: {
    disableTelemetry: true,
  },
  docs: {
    autodocs: 'tag',
  },
};

export default config;
