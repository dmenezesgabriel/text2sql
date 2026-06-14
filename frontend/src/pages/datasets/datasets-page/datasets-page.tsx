import { useEffect } from 'react';
import { Link } from 'react-router-dom';

import type { Dataset } from '@/entities/dataset/types';
import { useDatasetStore } from '@/features/dataset/model/store';
import { RegisterDatasetForm } from '@/features/dataset/ui/register-dataset-form';

/**
 *
 * @param datasets
 * @param isLoading
 */
function renderDatasetList(datasets: Dataset[], isLoading: boolean) {
  if (isLoading && datasets.length === 0) {
    return <bi-spinner />;
  }
  if (datasets.length === 0) {
    return (
      <bi-empty-state
        heading="No datasets yet"
        description="Register an S3 dataset to get started."
      />
    );
  }
  return (
    <div className="overflow-x-auto">
      <table role="table" aria-label="Registered datasets" className="w-full border-collapse">
        <thead>
          <tr>
            <th scope="col" className="th-base">
              Name
            </th>
            <th scope="col" className="th-base">
              Kind
            </th>
            <th scope="col" className="th-base">
              Location
            </th>
            <th scope="col" className="th-base">
              Columns
            </th>
            <th scope="col" className="th-base">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {datasets.map((ds) => (
            <tr key={ds.id}>
              <td className="td-base font-semibold">
                <Link to={`/datasets/${ds.id}`}>{ds.name}</Link>
              </td>
              <td className="td-base">
                <bi-badge variant="default">{ds.kind}</bi-badge>
              </td>
              <td className="td-base text-secondary text-sm font-mono">{ds.location ?? '—'}</td>
              <td className="td-base tabular-nums">{ds.columns.length}</td>
              <td className="td-base">
                <Link to={`/datasets/${ds.id}`} className="text-accent text-sm">
                  Preview →
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
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
    <div className="flex flex-col gap-lg">
      <bi-page-header
        heading="Datasets"
        description="Register and browse data sources for your queries"
      />

      <bi-card heading="Register a Dataset">
        <RegisterDatasetForm />
      </bi-card>

      <bi-card heading={`Registered Datasets (${String(datasets.length)})`}>
        {renderDatasetList(datasets, isLoading)}
      </bi-card>
    </div>
  );
}
