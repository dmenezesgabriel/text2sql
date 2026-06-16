type MessageRole = 'user' | 'assistant' | 'system' | 'tool';

export interface AgentMessage {
  id: string;
  role: MessageRole;
  content: string;
  spec?: Record<string, unknown>;
  toolCall?: ToolCall;
  createdAt: string;
  error?: boolean;
}

interface ToolCall {
  name: string;
  parameters: Record<string, unknown>;
}

export interface AgentEvent {
  type: string;
  payload: string | Record<string, unknown>;
}
