import React from 'react';

import { Header } from '../header';
import { Sidebar } from '../sidebar';

interface LayoutProps {
  readonly children: React.ReactNode;
}

const layoutStyle: React.CSSProperties = {
  display: 'flex',
  height: '100vh',
};

const mainStyle: React.CSSProperties = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
};

const contentStyle: React.CSSProperties = {
  flex: 1,
  overflow: 'auto',
  padding: 'var(--spacing-lg)',
};

/**
 *
 * @param root0
 * @param root0.children
 */
export function Layout({ children }: LayoutProps) {
  return (
    <div style={layoutStyle}>
      <Sidebar />
      <div style={mainStyle}>
        <Header />
        <main style={contentStyle}>{children}</main>
      </div>
    </div>
  );
}
