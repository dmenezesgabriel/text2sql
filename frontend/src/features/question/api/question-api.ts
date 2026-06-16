import type { Question } from '@/entities/question/types';

const BASE = '/api/v1/questions';

export interface CreateQuestionPayload {
  title: string;
  sql: string;
  dataset_id: string;
  viz_component: string;
  viz_format: 'CHART' | 'TABLE' | 'TEXT' | 'DASHBOARD';
  viz_props: Record<string, unknown>;
  viz_children?: unknown[];
}

export interface DrillPayload {
  column: string;
  value: unknown;
}

/**
 *
 */
export async function listQuestions(): Promise<Question[]> {
  const res = await fetch(BASE);
  if (!res.ok) throw new Error(`listQuestions failed: ${res.statusText}`);
  const body = (await res.json()) as { questions: Question[] };
  return body.questions;
}

/**
 *
 * @param id
 */
export async function getQuestion(id: string): Promise<Question> {
  const res = await fetch(`${BASE}/${id}`);
  if (!res.ok) throw new Error(`getQuestion ${id} failed: ${res.statusText}`);
  return res.json() as Promise<Question>;
}

/**
 *
 * @param payload
 */
export async function createQuestion(payload: CreateQuestionPayload): Promise<Question> {
  const res = await fetch(BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`createQuestion failed: ${res.statusText}`);
  return res.json() as Promise<Question>;
}

/**
 *
 * @param id
 */
export async function deleteQuestion(id: string): Promise<void> {
  const res = await fetch(`${BASE}/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`deleteQuestion ${id} failed: ${res.statusText}`);
}

/**
 *
 * @param id
 * @param payload
 */
export async function drillQuestion(id: string, payload: DrillPayload): Promise<Question> {
  const res = await fetch(`${BASE}/${id}/drill`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`drillQuestion ${id} failed: ${res.statusText}`);
  return res.json() as Promise<Question>;
}
