import type { Dataset } from '@/entities/dataset/types';

const BASE = '/api/v1/datasets';

/**
 *
 */
export async function listDatasets(): Promise<Dataset[]> {
  const res = await fetch(BASE);
  if (!res.ok) throw new Error(`listDatasets failed: ${res.statusText}`);
  const body = (await res.json()) as { datasets: Dataset[] };
  return body.datasets;
}

/**
 *
 * @param params
 * @param params.name
 * @param params.s3_uri
 */
export async function registerS3Dataset(params: {
  name: string;
  s3_uri: string;
}): Promise<Dataset> {
  const res = await fetch(`${BASE}/register-s3`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`registerS3Dataset failed: ${res.statusText}`);
  return res.json() as Promise<Dataset>;
}

/**
 *
 * @param id
 */
export async function previewDataset(
  id: string,
): Promise<{ columns: string[]; rows: Record<string, unknown>[] }> {
  const res = await fetch(`${BASE}/${id}/preview`);
  if (!res.ok) throw new Error(`previewDataset failed: ${res.statusText}`);
  return res.json() as Promise<{ columns: string[]; rows: Record<string, unknown>[] }>;
}

/**
 *
 * @param id
 */
export async function deleteDataset(id: string): Promise<void> {
  const res = await fetch(`${BASE}/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`deleteDataset ${id} failed: ${res.statusText}`);
}
