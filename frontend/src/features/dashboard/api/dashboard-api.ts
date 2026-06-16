import type { Dashboard } from '@/entities/dashboard/types';

const BASE = '/api/v1/dashboards';

export interface CreateDashboardPayload {
  title: string;
}

export interface FilterPayload {
  source_tile: string;
  column: string;
  value: unknown;
}

/**
 *
 */
export async function listDashboards(): Promise<Dashboard[]> {
  const res = await fetch(BASE);
  if (!res.ok) throw new Error(`listDashboards failed: ${res.statusText}`);
  const body = (await res.json()) as { dashboards: Dashboard[] };
  return body.dashboards;
}

/**
 *
 * @param id
 */
export async function getDashboard(id: string): Promise<Dashboard> {
  const res = await fetch(`${BASE}/${id}`);
  if (!res.ok) throw new Error(`getDashboard ${id} failed: ${res.statusText}`);
  return res.json() as Promise<Dashboard>;
}

/**
 *
 * @param payload
 */
export async function createDashboard(payload: CreateDashboardPayload): Promise<Dashboard> {
  const res = await fetch(BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`createDashboard failed: ${res.statusText}`);
  return res.json() as Promise<Dashboard>;
}

/**
 *
 * @param id
 */
export async function deleteDashboard(id: string): Promise<void> {
  const res = await fetch(`${BASE}/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`deleteDashboard ${id} failed: ${res.statusText}`);
}

/**
 *
 * @param id
 * @param payload
 */
export async function filterDashboard(id: string, payload: FilterPayload): Promise<void> {
  const res = await fetch(`${BASE}/${id}/filter`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`filterDashboard ${id} failed: ${res.statusText}`);
}
