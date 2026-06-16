import { create } from 'zustand';

type Theme = 'light' | 'dark';

const STORAGE_KEY = 'theme';

/** Read the theme the no-FOUC inline script (index.html) committed to the DOM. */
function readInitialTheme(): Theme {
  const attr = document.documentElement.dataset.theme;
  return attr === 'dark' ? 'dark' : 'light';
}

/**
 * Single source of truth for the active theme: the <html data-theme> attribute
 *  plus a localStorage mirror. Persisting here keeps it in sync with the
 *  pre-paint script in index.html that reads the same key.
 * @param theme
 */
function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // Private mode / storage disabled: the in-memory state still drives the UI.
  }
}

interface ThemeState {
  readonly theme: Theme;
  toggle: () => void;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: readInitialTheme(),
  setTheme: (theme) => {
    applyTheme(theme);
    set({ theme });
  },
  toggle: () => {
    get().setTheme(get().theme === 'dark' ? 'light' : 'dark');
  },
}));
