import { assetApi } from "./apiClients";
import type {
  MaintenanceCreatePayload,
  MaintenanceEscalatePayload,
  MaintenanceRecord,
  MaintenanceStatus,
} from "@/types/maintenance";

interface MaintenanceFilters {
  status?: MaintenanceStatus;
  asset_id?: number;
}

export const maintenanceService = {
  getAll: async (
    filters: MaintenanceFilters = {},
  ): Promise<MaintenanceRecord[]> => {
    const { data } = await assetApi.get<MaintenanceRecord[]>("/maintenance/", {
      params: filters,
    });
    return data;
  },

  start: async (
    payload: MaintenanceCreatePayload,
  ): Promise<MaintenanceRecord> => {
    const { data } = await assetApi.post<MaintenanceRecord>(
      "/maintenance/",
      payload,
    );
    return data;
  },

  escalate: async (
    id: number,
    payload: MaintenanceEscalatePayload,
  ): Promise<MaintenanceRecord> => {
    const { data } = await assetApi.put<MaintenanceRecord>(
      `/maintenance/${id}/escalate`,
      payload,
    );
    return data;
  },

  finish: async (id: number, notes?: string): Promise<MaintenanceRecord> => {
    const { data } = await assetApi.put<MaintenanceRecord>(
      `/maintenance/${id}/finish`,
      { notes },
    );
    return data;
  },
};
