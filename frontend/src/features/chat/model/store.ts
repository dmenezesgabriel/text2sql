import { create } from 'zustand';

import type { AgentEvent, AgentMessage } from '@/entities/agent/types';

interface ChatState {
  messages: AgentMessage[];
  isStreaming: boolean;
  conversationId: string | null;

  addMessage: (message: AgentMessage) => void;
  appendToLastAssistant: (fragment: string) => void;
  setSpecOnLastAssistant: (spec: Record<string, unknown>) => void;
  setErrorOnLastAssistant: (message: string) => void;
  handleEvent: (event: AgentEvent) => void;
  setStreaming: (streaming: boolean) => void;
  setConversationId: (id: string) => void;
  loadMessages: (conversationId: string, messages: AgentMessage[]) => void;
  clear: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isStreaming: false,
  conversationId: null,

  addMessage: (message) => {
    set((state) => ({ messages: [...state.messages, message] }));
  },

  appendToLastAssistant: (fragment) => {
    set((state) => {
      const messages = [...state.messages];
      const last = messages.at(-1);
      if (last && last.role === 'assistant') {
        messages[messages.length - 1] = { ...last, content: last.content + fragment };
      }
      return { messages };
    });
  },

  setSpecOnLastAssistant: (spec) => {
    set((state) => {
      const messages = [...state.messages];
      const last = messages.at(-1);
      if (last?.role === 'assistant') {
        messages[messages.length - 1] = { ...last, spec };
      }
      return { messages };
    });
  },

  setErrorOnLastAssistant: (message) => {
    set((state) => {
      const messages = [...state.messages];
      const last = messages.at(-1);
      if (last?.role === 'assistant') {
        messages[messages.length - 1] = { ...last, content: message, error: true };
      }
      return { messages };
    });
  },

  handleEvent: (event) => {
    switch (event.type) {
      case 'ThinkingEvent': {
        get().appendToLastAssistant(event.payload as string);

        break;
      }
      case 'SpecFragmentEvent': {
        get().setSpecOnLastAssistant(event.payload as Record<string, unknown>);

        break;
      }
      case 'ErrorEvent': {
        get().setErrorOnLastAssistant(event.payload as string);

        break;
      }
      // No default
    }
  },

  setStreaming: (streaming) => {
    set({ isStreaming: streaming });
  },

  setConversationId: (id) => {
    set({ conversationId: id });
  },

  loadMessages: (conversationId, messages) => {
    set({ conversationId, messages, isStreaming: false });
  },

  clear: () => {
    set({ messages: [], isStreaming: false, conversationId: null });
  },
}));
