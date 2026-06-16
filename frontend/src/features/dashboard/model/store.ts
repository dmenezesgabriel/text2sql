import { create } from 'zustand';

import type { Dashboard } from '@/entities/dashboard/types';

import {
  createDashboard as apiCreate,
  type CreateDashboardPayload,
  deleteDashboard as apiDelete,
  filterDashboard as apiFilter,
  type FilterPayload,
  getDashboard,
  listDashboards,
} from '../api/dashboard-api';

interface DashboardState {
  dashboards: Dashboard[];
  selectedDashboard: Dashboard | null;
  activeFilters: Record<string, unknown>;
  isLoading: boolean;
  error: string | null;
  fetchDashboards: () => Promise<void>;
  fetchDashboard: (id: string) => Promise<void>;
  createDashboard: (payload: CreateDashboardPayload) => Promise<Dashboard>;
  deleteDashboard: (id: string) => Promise<void>;
  applyFilter: (dashboardId: string, payload: FilterPayload) => Promise<void>;
  clearFilters: () => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  dashboards: [],
  selectedDashboard: null,
  activeFilters: {},
  isLoading: false,
  error: null,

  fetchDashboards: async () => {
    set({ isLoading: true, error: null });
    try {
      const dashboards = await listDashboards();
      set({ dashboards, isLoading: false });
    } catch (error) {
      set({ error: String(error), isLoading: false });
    }
  },

  fetchDashboard: async (id) => {
    set({ isLoading: true, error: null, activeFilters: {} });
    try {
      const selectedDashboard = await getDashboard(id);
      set({ selectedDashboard, isLoading: false });
    } catch (error) {
      set({ error: String(error), isLoading: false });
    }
  },

  createDashboard: async (payload) => {
    const dashboard = await apiCreate(payload);
    set((s) => ({ dashboards: [dashboard, ...s.dashboards] }));
    return dashboard;
  },

  deleteDashboard: async (id) => {
    set((s) => ({ dashboards: s.dashboards.filter((d) => d.id !== id) }));
    await apiDelete(id);
  },

  applyFilter: async (dashboardId, payload) => {
    await apiFilter(dashboardId, payload);
    set((s) => ({
      activeFilters: { ...s.activeFilters, [payload.source_tile]: payload.value },
    }));
  },

  clearFilters: () => {
    set({ activeFilters: {} });
  },
}));
