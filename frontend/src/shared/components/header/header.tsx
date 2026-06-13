import React from 'react';

const headerStyle: React.CSSProperties = {
  height: 'var(--header-height)',
  borderBottom: '1px solid var(--color-border)',
  display: 'flex',
  alignItems: 'center',
  padding: '0 var(--spacing-lg)',
  background: 'var(--color-bg)',
};

const titleStyle: React.CSSProperties = {
  fontSize: '16px',
  fontWeight: 600,
  color: 'var(--color-text)',
};

/**
 *
 */
export function Header() {
  return (
    <header style={headerStyle}>
      <span style={titleStyle}>Generative Business Intelligence</span>
    </header>
  );
}
