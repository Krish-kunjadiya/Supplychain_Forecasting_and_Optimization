import { create } from 'zustand';

export const useDashboardStore = create((set) => ({
  activeJobId: null,
  selectedSku: null,
  setJobId: (id) => set({ activeJobId: id }),
  setSelectedSku: (sku) => set({ selectedSku: sku })
}));
