export interface Dataset {
  id: string;
  name: string;
  kind: 'table' | 'file' | 'database';
  columns: ColumnDefinition[];
  createdAt: string;
  updatedAt: string;
}

export interface ColumnDefinition {
  name: string;
  dtype: string;
  nullable: boolean;
}

export type FileFormat = 'csv' | 'parquet' | 'json';
