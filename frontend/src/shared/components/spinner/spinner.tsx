import React from 'react';

const containerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 'var(--spacing-xl)',
};

const spinnerStyle: React.CSSProperties = {
  width: 24,
  height: 24,
  border: '2px solid var(--color-border)',
  borderTop: '2px solid var(--color-primary)',
  borderRadius: '50%',
  animation: 'spin 0.8s linear infinite',
};

/**
 *
 */
export function Spinner() {
  return (
    <div style={containerStyle}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={spinnerStyle} />
    </div>
  );
}
