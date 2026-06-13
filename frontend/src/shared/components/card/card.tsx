import React from 'react';

interface CardProps {
  readonly children: React.ReactNode;
  readonly title?: string;
  readonly style?: React.CSSProperties;
}

const cardStyle: React.CSSProperties = {
  background: 'var(--color-bg)',
  border: '1px solid var(--color-border)',
  borderRadius: 'var(--radius-md)',
  padding: 'var(--spacing-lg)',
  boxShadow: 'var(--shadow-sm)',
};

const titleStyle: React.CSSProperties = {
  fontSize: '16px',
  fontWeight: 600,
  marginBottom: 'var(--spacing-md)',
};

/**
 *
 * @param root0
 * @param root0.children
 * @param root0.title
 * @param root0.style
 */
export function Card({ children, title, style }: CardProps) {
  return (
    <div style={{ ...cardStyle, ...style }}>
      {title && <div style={titleStyle}>{title}</div>}
      {children}
    </div>
  );
}
