export type DocumentType = "CC" | "TI" | "CE" | "PASAPORTE";

export interface Responsible {
  id: number;
  full_name: string;
  document_type: DocumentType;
  document_number: string;
  phone: string | null;
  is_active: boolean;
}

export interface ResponsibleCreatePayload {
  full_name: string;
  document_type: DocumentType;
  document_number: string;
  phone?: string;
}

export interface ResponsibleUpdatePayload {
  full_name?: string;
  phone?: string;
  is_active?: boolean;
}
