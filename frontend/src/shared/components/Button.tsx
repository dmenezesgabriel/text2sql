import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  disabled?: boolean;
  style?: React.CSSProperties;
}

const baseStyle: React.CSSProperties = {
  padding: 'var(--spacing-sm) var(--spacing-md)',
  borderRadius: 'var(--radius-sm)',
  border: '1px solid var(--color-border)',
  cursor: 'pointer',
  fontSize: '14px',
  fontWeight: 500,
  display: 'inline-flex',
  alignItems: 'center',
  gap: 'var(--spacing-xs)',
};

const variants: Record<string, React.CSSProperties> = {
  primary: {
    background: 'var(--color-primary)',
    color: '#ffffff',
    border: 'none',
  },
  secondary: {
    background: 'var(--color-bg)',
    color: 'var(--color-text)',
  },
  ghost: {
    background: 'transparent',
    border: 'none',
    color: 'var(--color-text-secondary)',
  },
};

/**
 *
 * @param root0
 * @param root0.children
 * @param root0.onClick
 * @param root0.variant
 * @param root0.disabled
 * @param root0.style
 */
export function Button({
  children,
  onClick,
  variant = 'secondary',
  disabled = false,
  style,
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        ...baseStyle,
        ...variants[variant],
        ...(disabled ? { opacity: 0.5, cursor: 'not-allowed' } : {}),
        ...style,
      }}
    >
      {children}
    </button>
  );
}
