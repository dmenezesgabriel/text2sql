export interface Question {
  id: string;
  title: string;
  sql: string;
  datasetId: string;
  vizComponent: string;
  vizFormat: 'CHART' | 'TABLE' | 'TEXT' | 'DASHBOARD';
  vizProps: Record<string, unknown>;
  vizChildren?: unknown[];
  createdAt: string;
  updatedAt: string;
}
