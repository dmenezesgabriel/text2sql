import { create } from 'zustand';

import type { AgentEvent,AgentMessage } from '@/entities/agent/types';

interface ChatState {
  messages: AgentMessage[];
  isStreaming: boolean;
  conversationId: string | null;

  addMessage: (message: AgentMessage) => void;
  appendToLastAssistant: (fragment: string) => void;
  handleEvent: (event: AgentEvent) => void;
  setStreaming: (streaming: boolean) => void;
  setConversationId: (id: string) => void;
  clear: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isStreaming: false,
  conversationId: null,

  addMessage: (message) =>
    { set((state) => ({
      messages: [...state.messages, message],
    })); },

  appendToLastAssistant: (fragment) =>
    { set((state) => {
      const messages = [...state.messages];
      const last = messages.at(-1);
      if (last && last.role === 'assistant') {
        messages[messages.length - 1] = {
          ...last,
          content: last.content + fragment,
        };
      }
      return { messages };
    }); },

  handleEvent: (event) => {
    if (event.type === 'SpecFragmentEvent') {
      get().appendToLastAssistant(JSON.stringify(event.payload));
    }
  },

  setStreaming: (streaming) => { set({ isStreaming: streaming }); },

  setConversationId: (id) => { set({ conversationId: id }); },

  clear: () =>
    { set({
      messages: [],
      isStreaming: false,
      conversationId: null,
    }); },
}));
