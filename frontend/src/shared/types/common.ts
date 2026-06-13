export interface ApiError {
  status: number;
  message: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export type AsyncStatus = 'idle' | 'loading' | 'success' | 'error';
