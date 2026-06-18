import { useEffect } from 'react';
import { NavLink, useMatch, useNavigate } from 'react-router-dom';

import { useConversationsStore } from '@/features/chat/model/conversations-store';
import { useChatStore } from '@/features/chat/model/store';

const navLinks = [
  { to: '/questions', label: 'Questions' },
  { to: '/dashboards', label: 'Dashboards' },
  { to: '/datasets', label: 'Datasets' },
];

/**
 *
 * @param isoString
 */
function relativeTime(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${String(minutes)}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${String(hours)}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return 'yesterday';
  return `${String(days)}d ago`;
}

/**
 *
 */
export function Sidebar() {
  const navigate = useNavigate();
  const { clear } = useChatStore();
  const { conversations, loadConversations } = useConversationsStore();
  const chatMatch = useMatch('/chat/:conversationId');

  useEffect(() => {
    void loadConversations();
  }, []);

  /**
   *
   */
  function handleNewChat() {
    clear();
    void navigate('/chat');
  }

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

      {/* Brand zone — data-grid texture is the signature design element */}
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

      {/* New Chat button */}
      <div style={{ padding: 'var(--spacing-sm)' }}>
        <button
          type="button"
          onClick={handleNewChat}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-xs)',
            width: '100%',
            padding: 'var(--spacing-sm) var(--spacing-md)',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--text-sm)',
            fontWeight: 500,
            color: 'var(--color-text-sidebar-active)',
            background: 'var(--color-bg-sidebar-active)',
            border: 'none',
            cursor: 'pointer',
            textAlign: 'left',
          }}
        >
          <span aria-hidden="true" style={{ fontSize: '1rem', lineHeight: 1 }}>
            +
          </span>
          New Chat
        </button>
      </div>

      <hr
        aria-hidden="true"
        style={{ border: 'none', borderTop: '1px solid var(--color-border-sidebar)' }}
      />

      {/* Nav links */}
      <div className="flex flex-col gap-xs" style={{ padding: 'var(--spacing-sm)' }}>
        {navLinks.map(({ to, label }) => (
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

      {/* Recent conversations */}
      {conversations.length > 0 && (
        <>
          <hr
            aria-hidden="true"
            style={{ border: 'none', borderTop: '1px solid var(--color-border-sidebar)' }}
          />

          <div
            style={{
              padding: 'var(--spacing-sm) var(--spacing-md) var(--spacing-xs)',
            }}
          >
            <span
              style={{
                fontSize: 'var(--text-xs)',
                color: 'var(--color-text-muted, var(--color-text-sidebar))',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                opacity: 0.6,
              }}
            >
              Recent
            </span>
          </div>

          <div
            className="flex flex-col"
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '0 var(--spacing-sm) var(--spacing-sm)',
              gap: 'var(--spacing-xs)',
            }}
          >
            {conversations.map((conv) => {
              const isActive = chatMatch?.params.conversationId === conv.id;
              return (
                <NavLink
                  key={conv.id}
                  to={`/chat/${conv.id}`}
                  style={{
                    display: 'block',
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    borderRadius: 'var(--radius-sm)',
                    textDecoration: 'none',
                    background: isActive ? 'var(--color-bg-sidebar-active)' : 'transparent',
                  }}
                >
                  <div
                    style={{
                      fontSize: 'var(--text-sm)',
                      color: isActive
                        ? 'var(--color-text-sidebar-active)'
                        : 'var(--color-text-sidebar)',
                      fontWeight: isActive ? 500 : 400,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {conv.title}
                  </div>
                  <div
                    style={{
                      fontSize: 'var(--text-xs)',
                      color: 'var(--color-text-sidebar)',
                      opacity: 0.5,
                      marginTop: '2px',
                    }}
                  >
                    {relativeTime(conv.updated_at)}
                  </div>
                </NavLink>
              );
            })}
          </div>
        </>
      )}
    </nav>
  );
}
