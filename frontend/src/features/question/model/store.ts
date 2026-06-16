import { create } from 'zustand';

import type { Question } from '@/entities/question/types';

import {
  createQuestion as apiCreate,
  type CreateQuestionPayload,
  deleteQuestion as apiDelete,
  type DrillPayload,
  drillQuestion as apiDrill,
  getQuestion,
  listQuestions,
} from '../api/question-api';

interface QuestionState {
  questions: Question[];
  selectedQuestion: Question | null;
  isLoading: boolean;
  error: string | null;
  fetchQuestions: () => Promise<void>;
  fetchQuestion: (id: string) => Promise<void>;
  createQuestion: (payload: CreateQuestionPayload) => Promise<Question>;
  deleteQuestion: (id: string) => Promise<void>;
  drillQuestion: (id: string, drill: DrillPayload) => Promise<Question>;
}

export const useQuestionStore = create<QuestionState>((set, get) => ({
  questions: [],
  selectedQuestion: null,
  isLoading: false,
  error: null,

  fetchQuestions: async () => {
    set({ isLoading: true, error: null });
    try {
      const questions = await listQuestions();
      set({ questions, isLoading: false });
    } catch (error) {
      set({ error: String(error), isLoading: false });
    }
  },

  fetchQuestion: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const selectedQuestion = await getQuestion(id);
      set({ selectedQuestion, isLoading: false });
    } catch (error) {
      set({ error: String(error), isLoading: false });
    }
  },

  createQuestion: async (payload) => {
    const question = await apiCreate(payload);
    set((s) => ({ questions: [question, ...s.questions] }));
    return question;
  },

  deleteQuestion: async (id) => {
    set((s) => ({ questions: s.questions.filter((q) => q.id !== id) }));
    try {
      await apiDelete(id);
    } catch (error) {
      // re-fetch to restore consistent state on failure
      const questions = await listQuestions();
      set({ questions, error: String(error) });
    }
  },

  drillQuestion: async (id, drill) => {
    set({ isLoading: true, error: null });
    try {
      const result = await apiDrill(id, drill);
      set((s) => ({ questions: [result, ...s.questions], isLoading: false }));
      return result;
    } catch (error) {
      set({ error: String(error), isLoading: false });
      throw error;
    }
  },

  // expose getQuestion for imperative use outside React (dashboard detail fan-out)
  getQuestion: (id: string) => get().questions.find((q) => q.id === id) ?? null,
}));
