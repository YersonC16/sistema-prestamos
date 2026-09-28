export type AssetType = "equipo" | "herramienta" | "otro";
export type AssetStatus = "disponible" | "prestado" | "mantenimiento";

export interface Asset {
  id: number;
  name: string;
  asset_type: AssetType;
  status: AssetStatus;
  description: string | null;
}

export interface AssetCreatePayload {
  name: string;
  asset_type: AssetType;
  description?: string;
}
