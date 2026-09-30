import { loanApi } from "./apiClients";
import type {
  Loan,
  LoanCreatePayload,
  LoanHistoryEntry,
  LoanReturnPayload,
  LoanStatus,
  LoanSummary,
} from "@/types/loan";

interface LoanFilters {
  status?: LoanStatus;
  asset_id?: number;
}

export const loanService = {
  getAll: async (filters: LoanFilters = {}): Promise<Loan[]> => {
    const { data } = await loanApi.get<Loan[]>("/loans/", { params: filters });
    return data;
  },

  create: async (payload: LoanCreatePayload): Promise<Loan> => {
    const { data } = await loanApi.post<Loan>("/loans/", payload);
    return data;
  },

  returnLoan: async (
    loanId: number,
    payload: LoanReturnPayload,
  ): Promise<Loan> => {
    const { data } = await loanApi.put<Loan>(
      `/loans/${loanId}/return`,
      payload,
    );
    return data;
  },

  getSummary: async (): Promise<LoanSummary> => {
    const { data } = await loanApi.get<LoanSummary>("/loans/summary");
    return data;
  },

  getMovements: async (limit = 50): Promise<LoanHistoryEntry[]> => {
    const { data } = await loanApi.get<LoanHistoryEntry[]>("/loans/history", {
      params: { limit },
    });
    return data;
  },

  getCurrentHolder: async (assetId: number): Promise<Loan | null> => {
    const { data } = await loanApi.get<Loan | null>(
      `/loans/asset/${assetId}/current`,
    );
    return data;
  },

  getHistory: async (loanId: number): Promise<LoanHistoryEntry[]> => {
    const { data } = await loanApi.get<LoanHistoryEntry[]>(
      `/loans/${loanId}/history`,
    );
    return data;
  },
};
