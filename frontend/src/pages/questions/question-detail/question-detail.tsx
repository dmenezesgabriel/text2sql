import { JSONUIProvider, Renderer } from '@json-render/react';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { buildVizSpec } from '@/features/question/lib/build-viz-spec';
import { useQuestionStore } from '@/features/question/model/store';
import { BiInputReact } from '@/shared/components/input';
import { registry } from '@/widgets/json-render/registry';

/**
 *
 * @param iso
 */
function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
}

/**
 *
 */
export function QuestionDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedQuestion, isLoading, error, fetchQuestion, deleteQuestion, drillQuestion } =
    useQuestionStore();

  const [drillColumn, setDrillColumn] = useState('');
  const [drillValue, setDrillValue] = useState('');
  const [isDrilling, setIsDrilling] = useState(false);
  const [drillError, setDrillError] = useState('');

  useEffect(() => {
    if (id) void fetchQuestion(id);
  }, [id, fetchQuestion]);

  const handleDelete = () => {
    if (!id || !globalThis.confirm('Delete this question?')) return;
    void deleteQuestion(id).then(() => navigate('/questions'));
  };

  const handleDrill = async () => {
    if (!id || !drillColumn.trim() || !drillValue.trim()) return;
    setIsDrilling(true);
    setDrillError('');
    try {
      const result = await drillQuestion(id, {
        column: drillColumn.trim(),
        value: drillValue.trim(),
      });
      void navigate(`/questions/${result.id}`);
    } catch (error_) {
      setDrillError(String(error_));
    } finally {
      setIsDrilling(false);
    }
  };

  return (
    <div className="flex flex-col gap-lg">
      <bi-page-header heading={selectedQuestion?.title ?? 'Question'}>
        <a href="/questions" slot="breadcrumb" className="text-secondary">
          ← Questions
        </a>
        <bi-button slot="actions" variant="danger" onClick={handleDelete}>
          Delete
        </bi-button>
      </bi-page-header>

      {isLoading && <bi-spinner />}

      {error && (
        <p role="alert" aria-live="assertive" className="text-error text-sm">
          {error}
        </p>
      )}

      {selectedQuestion && (
        <>
          <bi-card heading="Visualization">
            <JSONUIProvider registry={registry}>
              <Renderer spec={buildVizSpec(selectedQuestion)} registry={registry} />
            </JSONUIProvider>
          </bi-card>

          <bi-card heading="SQL Query">
            <pre
              className="font-mono text-sm"
              style={{
                background: 'var(--color-bg-secondary)',
                padding: 'var(--spacing-md)',
                borderRadius: 'var(--radius-sm)',
                overflowX: 'auto',
                margin: 0,
              }}
            >
              <code>{selectedQuestion.sql}</code>
            </pre>
          </bi-card>

          <bi-card heading="Metadata">
            <dl className="flex flex-col gap-sm">
              {(
                [
                  ['Dataset', selectedQuestion.datasetId],
                  ['Format', selectedQuestion.vizFormat],
                  ['Created', formatDate(selectedQuestion.createdAt)],
                  ['Updated', formatDate(selectedQuestion.updatedAt)],
                ] as [string, string][]
              ).map(([term, detail]) => (
                <div key={term} className="flex gap-md">
                  <dt className="text-sm text-secondary" style={{ minWidth: '80px' }}>
                    {term}
                  </dt>
                  <dd className="text-sm font-medium">
                    {term === 'Format' ? <bi-badge variant="primary">{detail}</bi-badge> : detail}
                  </dd>
                </div>
              ))}
            </dl>
          </bi-card>

          <bi-card heading="Drill Down">
            <p className="text-sm text-secondary mb-md">
              Filter by a column value to create a derived question.
            </p>
            <div className="flex flex-col gap-sm">
              <BiInputReact
                label="Column name"
                value={drillColumn}
                onBiInputChange={(e: Event) => {
                  setDrillColumn((e as CustomEvent<string>).detail);
                }}
                placeholder="e.g. region"
              />
              <BiInputReact
                label="Filter value"
                value={drillValue}
                onBiInputChange={(e: Event) => {
                  setDrillValue((e as CustomEvent<string>).detail);
                }}
                placeholder="e.g. North America"
              />
              {drillError && <p className="text-error text-xs">{drillError}</p>}
              <bi-button
                variant="primary"
                disabled={isDrilling || !drillColumn.trim() || !drillValue.trim()}
                onClick={() => void handleDrill()}
              >
                {isDrilling ? 'Drilling…' : 'Drill Down'}
              </bi-button>
            </div>
          </bi-card>
        </>
      )}
    </div>
  );
}
