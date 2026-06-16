import { NavLink } from 'react-router-dom';

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
    <nav
      aria-label="Main navigation"
      className="flex flex-col"
      style={{
        width: 'var(--sidebar-width)',
        height: '100%',
        background: 'var(--color-bg-sidebar)',
        borderRight: '1px solid var(--color-border)',
        flexShrink: 0,
      }}
    >
      <h2 className="sr-only">Navigation</h2>

      {/* Logo zone — subtle data-grid texture is the signature design element */}
      <div
        style={{
          padding: 'var(--spacing-lg) var(--spacing-md)',
          backgroundImage:
            'repeating-linear-gradient(0deg, transparent 0, transparent 23px, var(--color-grid-line) 24px), repeating-linear-gradient(90deg, transparent 0, transparent 23px, var(--color-grid-line) 24px)',
        }}
      >
        <span
          className="text-accent tracking-wide uppercase font-semibold"
          style={{ fontSize: 'var(--text-xs)', letterSpacing: '0.14em' }}
        >
          text2sql
        </span>
      </div>

      <hr
        aria-hidden="true"
        style={{ border: 'none', borderTop: '1px solid var(--color-border-sidebar)' }}
      />

      <div className="flex flex-col gap-xs" style={{ padding: 'var(--spacing-sm)' }}>
        {links.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            aria-current={undefined}
            style={({ isActive }) => ({
              display: 'block',
              padding: 'var(--spacing-sm) var(--spacing-md)',
              borderRadius: 'var(--radius-sm)',
              fontSize: 'var(--text-sm)',
              textDecoration: 'none',
              color: isActive ? 'var(--color-text-sidebar-active)' : 'var(--color-text-sidebar)',
              background: isActive ? 'var(--color-bg-sidebar-active)' : 'transparent',
              fontWeight: isActive ? 500 : 400,
            })}
          >
            {({ isActive }) => (
              <>
                <span aria-current={isActive ? 'page' : undefined} aria-hidden="true" />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
