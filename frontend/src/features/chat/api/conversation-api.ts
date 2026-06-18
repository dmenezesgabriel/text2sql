import type { AgentMessage } from '@/entities/agent/types';

export interface ConversationSummary {
  id: string;
  title: string;
  updated_at: string;
}

/**
 *
 */
export async function listConversations(): Promise<ConversationSummary[]> {
  const res = await fetch('/api/v1/conversations');
  if (!res.ok) throw new Error(`Failed to list conversations: ${String(res.status)}`);
  const data = (await res.json()) as { conversations: ConversationSummary[] };
  return data.conversations;
}

/**
 *
 * @param id
 */
export async function getConversationMessages(id: string): Promise<AgentMessage[]> {
  const res = await fetch(`/api/v1/conversations/${id}/messages`);
  if (!res.ok) throw new Error(`Failed to load messages: ${String(res.status)}`);
  const data = (await res.json()) as {
    messages: { role: 'user' | 'assistant'; content: string; spec?: Record<string, unknown> }[];
  };
  return data.messages.map((m, i) => ({
    id: `${id}-${String(i)}`,
    role: m.role,
    content: m.content,
    spec: m.spec,
    createdAt: new Date().toISOString(),
  }));
}
