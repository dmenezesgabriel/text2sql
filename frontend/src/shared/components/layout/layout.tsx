import React from 'react';

import { ThemeToggle } from '@/shared/theme/theme-toggle';

import { Sidebar } from '../sidebar';

interface LayoutProps {
  readonly children: React.ReactNode;
  readonly headerActions?: React.ReactNode;
}

/**
 *
 * @param root0
 * @param root0.children
 * @param root0.headerActions
 */
export function Layout({ children, headerActions }: LayoutProps) {
  return (
    <div className="flex h-full" style={{ height: '100vh' }}>
      <a href="#main-content" className="skip-nav">
        Skip to content
      </a>
      <Sidebar />
      <div className="flex flex-col grow" style={{ overflow: 'hidden' }}>
        <bi-header>
          <div slot="actions" className="flex items-center gap-sm">
            {headerActions}
            <ThemeToggle />
          </div>
        </bi-header>
        <main
          id="main-content"
          className="grow overflow-auto"
          style={{ padding: 'var(--spacing-lg)' }}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
