export type LoanStatus = "activo" | "devuelto" | "atrasado";

export interface Loan {
  id: number;
  asset_id: number;
  responsible_name: string;
  loan_date: string;
  expected_return_date: string;
  actual_return_date: string | null;
  status: LoanStatus;
}

export interface LoanCreatePayload {
  asset_id: number;
  responsible_name: string;
  loan_date: string;
  expected_return_date: string;
}
