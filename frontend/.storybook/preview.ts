// Load design tokens + utilities so stories render with the real design system.
import '../src/app/styles/global.css';

import type { Decorator, Preview } from '@storybook/web-components';
import { initialize, mswLoader } from 'msw-storybook-addon';

initialize();

const themeDecorator: Decorator = (
  story: () => unknown,
  context: { globals: Record<string, unknown> },
) => {
  const theme = context.globals['theme'] === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.theme = theme;
  document.body.style.background = 'var(--color-bg)';
  document.body.style.color = 'var(--color-text)';
  return story();
};

const preview: Preview = {
  globalTypes: {
    theme: {
      description: 'Color theme',
      defaultValue: 'light',
      toolbar: {
        title: 'Theme',
        icon: 'mirror',
        items: [
          { value: 'light', title: 'Light', icon: 'sun' },
          { value: 'dark', title: 'Dark', icon: 'moon' },
        ],
        dynamicTitle: true,
      },
    },
  },
  decorators: [themeDecorator],
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    a11y: {
      config: {
        rules: [{ id: 'color-contrast', enabled: true }],
      },
    },
  },
  loaders: [mswLoader],
};

export default preview;
