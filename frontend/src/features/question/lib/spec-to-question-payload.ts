import type { CreateQuestionPayload } from '@/features/question/api/question-api';

type VizFormat = CreateQuestionPayload['viz_format'];

/**
 * Builds a question-creation payload from a json-render spec emitted by the
 * agent, defaulting missing fields so a partial spec still saves a question.
 * @param spec - The message's json-render spec (`AgentMessage.spec`)
 * @example
 * specToQuestionPayload({ meta: { title: 'Revenue' }, root: 'main', elements: { main: { type: 'BarChart' } } })
 */
export function specToQuestionPayload(spec: Record<string, unknown>): CreateQuestionPayload {
  const meta = (spec['meta'] as Record<string, unknown> | undefined) ?? {};
  const rootKey = (spec['root'] as string | undefined) ?? 'main';
  const elements = (spec['elements'] as Record<string, unknown> | undefined) ?? {};
  const rootEl = (elements[rootKey] as Record<string, unknown> | undefined) ?? {};
  const vizFormat = (meta['format'] as string | undefined)?.toUpperCase() as VizFormat | undefined;

  return {
    title: (meta['title'] as string | undefined) ?? 'Untitled question',
    sql: (meta['sql'] as string | undefined) ?? '',
    dataset_id: (meta['dataset_id'] as string | undefined) ?? '',
    viz_component: (rootEl['type'] as string | undefined) ?? '',
    viz_format: vizFormat ?? 'CHART',
    viz_props: (rootEl['props'] as Record<string, unknown> | undefined) ?? {},
  };
}
