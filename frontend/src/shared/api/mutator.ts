/**
 * Custom fetch mutator used by orval-generated API clients.
 * @param config
 * @param config.url
 * @param config.method
 * @param config.headers
 * @param config.data
 * @param config.params
 * @param options
 */
export async function customFetch<T>(
  config: {
    url: string;
    method: string;
    headers?: Record<string, string>;
    data?: unknown;
    params?: Record<string, string>;
  },
  options?: RequestInit,
): Promise<T> {
  const merged = new Headers(options?.headers);
  if (config.headers) {
    for (const [key, value] of Object.entries(config.headers)) {
      merged.set(key, value);
    }
  }

  const res = await fetch(config.url, {
    ...options,
    method: config.method,
    headers: merged,
    body: config.data === undefined ? undefined : JSON.stringify(config.data),
  });

  const text = [204, 205, 304].includes(res.status) ? null : await res.text();
  const body: unknown = text ? (JSON.parse(text) as unknown) : {};
  return body as T;
}
