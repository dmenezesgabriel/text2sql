import { JSONUIProvider, Renderer } from '@json-render/react';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import type { Question } from '@/entities/question/types';
import { useDashboardStore } from '@/features/dashboard/model/store';
import { BiDashboardGridReact } from '@/features/dashboard/ui/dashboard-grid';
import { BiDashboardTileReact } from '@/features/dashboard/ui/dashboard-tile';
import { getQuestion } from '@/features/question/api/question-api';
import { buildVizSpec } from '@/features/question/lib/build-viz-spec';
import { registry } from '@/widgets/json-render/registry';

/**
 *
 */
export function DashboardDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedDashboard, activeFilters, isLoading, error, fetchDashboard } =
    useDashboardStore();

  const [tileQuestions, setTileQuestions] = useState<Partial<Record<string, Question>>>({});

  useEffect(() => {
    if (id) void fetchDashboard(id);
  }, [id, fetchDashboard]);

  useEffect(() => {
    if (!selectedDashboard?.tiles.length) return;
    void Promise.all(
      selectedDashboard.tiles.map((tile) =>
        getQuestion(tile.questionId).then((q) => [tile.questionId, q] as const),
      ),
    ).then((pairs) => {
      setTileQuestions(Object.fromEntries(pairs));
    });
  }, [selectedDashboard]);

  return (
    <div className="flex flex-col gap-lg">
      <bi-page-header heading={selectedDashboard?.title ?? 'Dashboard'}>
        <a href="/dashboards" slot="breadcrumb" className="text-secondary">
          ← Dashboards
        </a>
        <bi-button
          slot="actions"
          variant="secondary"
          onClick={() => {
            void navigate('/dashboards');
          }}
        >
          Back
        </bi-button>
      </bi-page-header>

      {isLoading && <bi-spinner />}

      {error && (
        <p role="alert" aria-live="assertive" className="text-error text-sm">
          {error}
        </p>
      )}

      {selectedDashboard && selectedDashboard.tiles.length === 0 && (
        <bi-empty-state
          heading="No tiles"
          description="Save questions from Chat and add them to this dashboard."
        />
      )}

      {selectedDashboard && selectedDashboard.tiles.length > 0 && (
        <BiDashboardGridReact heading={selectedDashboard.title}>
          {selectedDashboard.tiles.map((tile) => {
            const q = tileQuestions[tile.questionId];
            const isFiltered = tile.id in activeFilters;

            return (
              <BiDashboardTileReact
                key={tile.id}
                tileId={tile.id}
                heading={q?.title ?? ''}
                col={tile.position.col}
                width={tile.position.width}
                row={tile.position.row}
                height={tile.position.height}
                filtered={isFiltered}
              >
                {q && (
                  <JSONUIProvider registry={registry}>
                    <Renderer spec={buildVizSpec(q)} registry={registry} />
                  </JSONUIProvider>
                )}
              </BiDashboardTileReact>
            );
          })}
        </BiDashboardGridReact>
      )}
    </div>
  );
}
