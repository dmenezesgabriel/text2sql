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

export interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
}

export interface VizDecision {
  format: string;
  component: string;
  props: Record<string, unknown>;
}
