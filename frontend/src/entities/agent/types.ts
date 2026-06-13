export type MessageRole = 'user' | 'assistant' | 'system' | 'tool';

export type ResponseKind = 'chart' | 'table' | 'text' | 'dashboard';

export interface AgentMessage {
  id: string;
  role: MessageRole;
  content: string;
  toolCall?: ToolCall;
  createdAt: string;
}

export interface ToolCall {
  name: string;
  parameters: Record<string, unknown>;
}

export interface AgentEvent {
  type: string;
  payload: string;
}

export interface ThinkingEvent extends AgentEvent {
  type: 'ThinkingEvent';
  payload: string;
}

export interface SpecFragmentEvent extends AgentEvent {
  type: 'SpecFragmentEvent';
  payload: Record<string, unknown>;
}

export interface ErrorEvent extends AgentEvent {
  type: 'ErrorEvent';
  payload: string;
}

export interface Conversation {
  id: string;
  messages: AgentMessage[];
  createdAt: string;
  updatedAt: string;
}
