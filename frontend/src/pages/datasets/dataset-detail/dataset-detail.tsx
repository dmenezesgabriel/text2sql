import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import type { Dataset } from '@/entities/dataset/types';
import { listDatasets, previewDataset } from '@/features/dataset/api/dataset-api';

interface Preview {
  columns: string[];
  rows: Record<string, unknown>[];
}

/**
 *
 * @param val
 */
function cellStr(val: unknown): string {
  if (val === null || val === undefined) return '';
  if (typeof val === 'string') return val;
  if (typeof val === 'number' || typeof val === 'boolean' || typeof val === 'bigint') {
    return String(val);
  }
  return JSON.stringify(val);
}

/**
 *
 */
export function DatasetDetail() {
  const { id } = useParams<{ id: string }>();
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    void Promise.all([
      listDatasets().then((list) => list.find((d) => d.id === id) ?? null),
      previewDataset(id),
    ])
      .then(([ds, prev]) => {
        setDataset(ds);
        setPreview(prev);
      })
      .catch((error_: unknown) => {
        setError(String(error_));
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [id]);

  return (
    <div className="flex flex-col gap-lg">
      <bi-page-header heading={dataset?.name ?? 'Dataset'}>
        <a href="/datasets" slot="breadcrumb" className="text-secondary">
          ← Datasets
        </a>
        {dataset && (
          <bi-badge slot="actions" variant="default">
            {dataset.kind}
          </bi-badge>
        )}
      </bi-page-header>

      {isLoading && <bi-spinner />}

      {error && (
        <p role="alert" aria-live="assertive" className="text-error text-sm">
          {error}
        </p>
      )}

      {dataset && (
        <bi-card heading={`Schema (${String(dataset.columns.length)} columns)`}>
          <div className="overflow-x-auto">
            <table role="table" aria-label="Dataset schema" className="w-full border-collapse">
              <thead>
                <tr>
                  <th scope="col" className="th-base">
                    Column
                  </th>
                  <th scope="col" className="th-base">
                    Type
                  </th>
                  <th scope="col" className="th-base">
                    Nullable
                  </th>
                </tr>
              </thead>
              <tbody>
                {dataset.columns.map((col) => (
                  <tr key={col.name}>
                    <td className="td-base font-mono text-sm">{col.name}</td>
                    <td className="td-base">
                      <bi-badge variant="mono">{col.dtype}</bi-badge>
                    </td>
                    <td className="td-base text-secondary text-sm">
                      {col.nullable ? 'Yes' : 'No'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </bi-card>
      )}

      {preview && (
        <bi-card heading={`Data Preview (${String(preview.rows.length)} rows)`}>
          <div className="overflow-x-auto">
            <table
              role="table"
              aria-label="Dataset preview"
              className="w-full border-collapse tabular-nums"
            >
              <thead>
                <tr>
                  {preview.columns.map((col) => (
                    <th key={col} scope="col" className="th-base font-mono text-xs">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((row, i) => (
                  <tr key={i}>
                    {preview.columns.map((col) => (
                      <td key={col} className="td-base text-sm font-mono">
                        {cellStr(row[col])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </bi-card>
      )}
    </div>
  );
}
