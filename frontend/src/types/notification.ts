export type LabMode =
  | "sin_patron"
  | "observer"
  | "strategy"
  | "observer_strategy";
export type LabChannel = "simulado" | "correo";

export interface NotificationEntry {
  id: number;
  event_type: string;
  site: string;
  asset_id: number | null;
  asset_name: string | null;
  recipient_email: string | null;
  recipient_name: string | null;
  channel: string;
  status: string;
  subject: string | null;
  error: string | null;
  created_at: string;
}

export interface LabRunPayload {
  event_type: string;
  site: string;
  channel: LabChannel;
}

export interface LabDelivery {
  recipient: string;
  channel: string;
  status: string;
  error: string | null;
}

export interface LabReport {
  mode: LabMode;
  steps: string[];
  deliveries: LabDelivery[];
  elapsed_ms: number;
}

export interface LabRunResult {
  event_type: string;
  site: string;
  channel: LabChannel;
  reports: LabReport[];
}
