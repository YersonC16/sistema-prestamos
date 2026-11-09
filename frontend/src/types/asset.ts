export type AssetType = "equipo" | "herramienta" | "otro";
export type AssetStatus = "disponible" | "prestado" | "mantenimiento" | "baja";

export interface Asset {
  id: number;
  name: string;
  code: string | null;
  brand: string | null;
  serial_number: string | null;
  asset_type: AssetType;
  status: AssetStatus;
  description: string | null;
}

export interface AssetDetail extends Asset {
  decommissioned_at: string | null;
  decommission_reason: string | null;
  decommissioned_by: string | null;
}

export interface AssetCreatePayload {
  name: string;
  asset_type: AssetType;
  description?: string;
  code?: string;
  brand?: string;
  serial_number?: string;
}

export interface AssetDecommissionPayload {
  reason: string;
}

export interface AssetSummary {
  total: number;
  disponible: number;
  prestado: number;
  mantenimiento: number;
  baja: number;
}

export interface AuditEntry {
  id: number;
  entity_type: string;
  entity_id: number | null;
  action: string;
  detail: string | null;
  performed_by: string;
  performed_by_role: string | null;
  created_at: string;
}
