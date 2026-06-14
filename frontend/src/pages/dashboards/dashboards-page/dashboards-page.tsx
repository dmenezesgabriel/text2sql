import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { useDashboardStore } from '@/features/dashboard/model/store';

/**
 *
 * @param iso
 */
function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
}

/**
 *
 */
export function DashboardsPage() {
  const { dashboards, isLoading, error, fetchDashboards, createDashboard } = useDashboardStore();
  const navigate = useNavigate();

  useEffect(() => {
    void fetchDashboards();
  }, [fetchDashboards]);

  const handleCreate = () => {
    const title = globalThis.prompt('Dashboard name:');
    if (!title?.trim()) return;
    void createDashboard({ title: title.trim() }).then((db) => {
      void navigate(`/dashboards/${db.id}`);
    });
  };

  return (
    <div className="flex flex-col gap-lg">
      <bi-page-header
        heading="Dashboards"
        description="Compose questions into interactive dashboards with cross-filtering"
      >
        <bi-button slot="actions" variant="primary" onClick={handleCreate}>
          + New Dashboard
        </bi-button>
      </bi-page-header>

      {isLoading && dashboards.length === 0 && <bi-spinner />}

      {error && (
        <p role="alert" aria-live="assertive" className="text-error text-sm">
          {error}
        </p>
      )}

      {!isLoading && !error && dashboards.length === 0 && (
        <bi-empty-state
          heading="No dashboards yet"
          description="Create a dashboard and add questions as tiles."
        >
          <bi-button slot="action" variant="primary" onClick={handleCreate}>
            Create Dashboard
          </bi-button>
        </bi-empty-state>
      )}

      {dashboards.length > 0 && (
        <div className="grid-auto-fill-340">
          {dashboards.map((db) => (
            <bi-card key={db.id}>
              <div className="flex flex-col gap-sm">
                <Link
                  to={`/dashboards/${db.id}`}
                  className="text-md font-semibold"
                  style={{ color: 'var(--color-text)', textDecoration: 'none' }}
                >
                  {db.title}
                </Link>
                <span className="text-sm text-secondary">
                  {db.tiles.length} tile{db.tiles.length === 1 ? '' : 's'}
                </span>
                <time dateTime={db.createdAt} className="text-xs text-secondary tabular-nums">
                  {formatDate(db.createdAt)}
                </time>
              </div>
            </bi-card>
          ))}
        </div>
      )}
    </div>
  );
}
