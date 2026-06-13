import React, { useEffect } from 'react';

import type { Dataset } from '@/entities/dataset/types';
import { useDatasetStore } from '@/features/dataset/model/store';
import { RegisterDatasetForm } from '@/features/dataset/ui/register-dataset-form';
import { Card } from '@/shared/components/card';

const pageStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--spacing-lg)',
};

const tableStyle: React.CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: '0.9rem',
};

const thStyle: React.CSSProperties = {
  textAlign: 'left',
  padding: 'var(--spacing-sm)',
  borderBottom: '2px solid var(--color-border)',
  color: 'var(--color-text-secondary)',
  fontWeight: 600,
};

const tdStyle: React.CSSProperties = {
  padding: 'var(--spacing-sm)',
  borderBottom: '1px solid var(--color-border)',
};

/**
 *
 * @param datasets
 * @param isLoading
 * @param td
 * @param th
 * @param table
 */
function renderDatasetList(
  datasets: Dataset[],
  isLoading: boolean,
  td: React.CSSProperties,
  th: React.CSSProperties,
  table: React.CSSProperties,
) {
  if (isLoading && datasets.length === 0) {
    return <p style={{ color: 'var(--color-text-secondary)' }}>Loading...</p>;
  }
  if (datasets.length === 0) {
    return (
      <p style={{ color: 'var(--color-text-secondary)' }}>
        No datasets registered. Use the form above or run the seed script.
      </p>
    );
  }
  return (
    <table style={table}>
      <thead>
        <tr>
          <th style={th}>Name</th>
          <th style={th}>View</th>
          <th style={th}>Location</th>
          <th style={th}>Columns</th>
        </tr>
      </thead>
      <tbody>
        {datasets.map((ds) => (
          <tr key={ds.id}>
            <td style={td}>{ds.name}</td>
            <td style={{ ...td, fontFamily: 'monospace', fontSize: '0.8rem' }}>
              ds_{ds.id.replaceAll('-', '')}
            </td>
            <td style={{ ...td, fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
              {ds.location ?? '—'}
            </td>
            <td style={td}>{String(ds.columns.length)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/**
 *
 */
export function DatasetsPage() {
  const { datasets, isLoading, fetchDatasets } = useDatasetStore();

  useEffect(() => {
    void fetchDatasets();
  }, [fetchDatasets]);

  return (
    <div style={pageStyle}>
      <h2>Datasets</h2>
      <Card title="Register a Dataset">
        <RegisterDatasetForm />
      </Card>
      <Card title={`Registered Datasets (${String(datasets.length)})`}>
        {renderDatasetList(datasets, isLoading, tdStyle, thStyle, tableStyle)}
      </Card>
    </div>
  );
}
