import { create } from 'zustand';

import { type ConversationSummary, listConversations } from '@/features/chat/api/conversation-api';

interface ConversationsState {
  conversations: ConversationSummary[];
  loadConversations: () => Promise<void>;
}

export const useConversationsStore = create<ConversationsState>((set) => ({
  conversations: [],

  loadConversations: async () => {
    try {
      const conversations = await listConversations();
      set({ conversations });
    } catch {
      // silently ignore — sidebar list is non-critical
    }
  },
}));
