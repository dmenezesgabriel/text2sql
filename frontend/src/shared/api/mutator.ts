/**
 * Custom fetch mutator used by orval-generated API clients.
 * Matches orval's `client: 'fetch'` calling convention: `customFetch<T>(url, options)`.
 * @param url
 * @param options
 */
export async function customFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);

  const text = [204, 205, 304].includes(res.status) ? null : await res.text();
  const data: unknown = text ? (JSON.parse(text) as unknown) : {};

  return data as T;
}
