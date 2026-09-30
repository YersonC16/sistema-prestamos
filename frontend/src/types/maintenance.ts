export type MaintenanceType = "preventivo" | "correctivo";
export type MaintenanceStatus = "en_proceso" | "finalizado";

export interface MaintenanceRecord {
  id: number;
  asset_id: number;
  asset_name: string | null;
  assigned_to: string;
  maintenance_type: MaintenanceType;
  reason: string;
  status: MaintenanceStatus;
  started_at: string;
  expected_end_date: string | null;
  finished_at: string | null;
  finish_notes: string | null;
  created_by: string | null;
}

export interface MaintenanceCreatePayload {
  asset_id: number;
  assigned_to: string;
  maintenance_type: MaintenanceType;
  reason: string;
  expected_end_date?: string;
}
