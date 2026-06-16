import React from 'react';

interface HeaderProps {
  readonly children?: React.ReactNode;
}

/**
 *
 * @param root0
 * @param root0.children
 */
export function Header({ children }: HeaderProps) {
  return (
    <header
      role="banner"
      className="flex items-center justify-between px-md border-top surface"
      style={{ height: 'var(--header-height)', flexShrink: 0 }}
    >
      <span
        className="text-sm text-secondary tracking-wide uppercase"
        style={{ letterSpacing: '0.08em' }}
      >
        Generative BI
      </span>
      {children && <div className="flex items-center gap-sm">{children}</div>}
    </header>
  );
}
