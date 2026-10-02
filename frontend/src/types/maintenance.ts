export type MaintenanceLocation = "interno" | "externo";
export type MaintenanceType = "preventivo" | "correctivo";
export type MaintenanceStatus = "en_proceso" | "finalizado";
export type MaintenanceSource = "manual" | "devolucion_con_novedad";

export interface MaintenanceRecord {
  id: number;
  asset_id: number;
  asset_name: string | null;
  location: MaintenanceLocation;
  assigned_to: string | null;
  provider_name: string | null;
  maintenance_type: MaintenanceType;
  reason: string;
  status: MaintenanceStatus;
  source: MaintenanceSource;
  source_loan_id: number | null;
  started_at: string;
  expected_end_date: string | null;
  finished_at: string | null;
  finish_notes: string | null;
  created_by: string | null;
}

export interface MaintenanceCreatePayload {
  asset_id: number;
  location: MaintenanceLocation;
  assigned_to?: string;
  provider_name?: string;
  maintenance_type: MaintenanceType;
  reason: string;
  expected_end_date?: string;
}

export interface MaintenanceEscalatePayload {
  provider_name: string;
  notes?: string;
}
