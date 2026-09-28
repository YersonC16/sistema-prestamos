import { loanApi } from "./apiClients";
import type { Loan, LoanCreatePayload } from "@/types/loan";

export const loanService = {
  getAll: async (): Promise<Loan[]> => {
    const { data } = await loanApi.get<Loan[]>("/loans/");
    return data;
  },

  create: async (payload: LoanCreatePayload): Promise<Loan> => {
    const { data } = await loanApi.post<Loan>("/loans/", payload);
    return data;
  },

  returnLoan: async (loanId: number): Promise<Loan> => {
    const { data } = await loanApi.put<Loan>(`/loans/${loanId}/return`);
    return data;
  },
};
