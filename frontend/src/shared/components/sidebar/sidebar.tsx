import React from 'react';
import { NavLink } from 'react-router-dom';

const sidebarStyle: React.CSSProperties = {
  width: 'var(--sidebar-width)',
  height: '100%',
  borderRight: '1px solid var(--color-border)',
  padding: 'var(--spacing-md)',
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--spacing-sm)',
};

const linkStyle: React.CSSProperties = {
  padding: 'var(--spacing-sm) var(--spacing-md)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--color-text)',
  textDecoration: 'none',
  fontSize: '14px',
};

const activeLinkStyle: React.CSSProperties = {
  ...linkStyle,
  background: 'var(--color-primary)',
  color: '#ffffff',
};

const logoStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  padding: 'var(--spacing-md) 0',
  marginBottom: 'var(--spacing-md)',
};

const links = [
  { to: '/chat', label: 'Chat' },
  { to: '/questions', label: 'Questions' },
  { to: '/dashboards', label: 'Dashboards' },
  { to: '/datasets', label: 'Datasets' },
];

/**
 *
 */
export function Sidebar() {
  return (
    <nav style={sidebarStyle}>
      <div style={logoStyle}>text2sql</div>
      {links.map(({ to, label }) => (
        <NavLink
          key={to}
          to={to}
          style={({ isActive }) => (isActive ? activeLinkStyle : linkStyle)}
        >
          {label}
        </NavLink>
      ))}
    </nav>
  );
}
