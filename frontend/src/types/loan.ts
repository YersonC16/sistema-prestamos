export type LoanStatus = "activo" | "devuelto" | "atrasado";
export type ReturnCondition = "bueno" | "con_novedad";

export interface Loan {
  id: number;
  asset_id: number;
  asset_name: string | null;
  responsible_name: string;
  notes: string | null;
  loan_date: string;
  expected_return_date: string;
  actual_return_date: string | null;
  status: LoanStatus;
  registered_by_name: string | null;
  returned_by_name: string | null;
  return_condition: string | null;
  return_notes: string | null;
}

export interface LoanCreatePayload {
  asset_id: number;
  responsible_name: string;
  expected_return_date: string;
  notes?: string;
}

export interface LoanReturnPayload {
  condition: ReturnCondition;
  notes?: string;
}

export interface LoanHistoryEntry {
  id: number;
  loan_id: number;
  asset_id: number;
  action: string;
  detail: string | null;
  performed_by: string;
  performed_by_role: string | null;
  created_at: string;
}

export interface LoanSummary {
  total: number;
  activo: number;
  devuelto: number;
  atrasado: number;
}
