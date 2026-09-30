import { assetApi } from "./apiClients";
import type {
  Asset,
  AssetCreatePayload,
  AssetSummary,
  AuditEntry,
} from "@/types/asset";

export const assetService = {
  getAll: async (): Promise<Asset[]> => {
    const { data } = await assetApi.get<Asset[]>("/assets/");
    return data;
  },

  getAvailable: async (): Promise<Asset[]> => {
    const { data } = await assetApi.get<Asset[]>("/assets/available");
    return data;
  },

  getById: async (id: number): Promise<Asset> => {
    const { data } = await assetApi.get<Asset>(`/assets/${id}`);
    return data;
  },

  create: async (payload: AssetCreatePayload): Promise<Asset> => {
    const { data } = await assetApi.post<Asset>("/assets/", payload);
    return data;
  },

  getSummary: async (): Promise<AssetSummary> => {
    const { data } = await assetApi.get<AssetSummary>("/assets/summary");
    return data;
  },

  getHistory: async (id: number): Promise<AuditEntry[]> => {
    const { data } = await assetApi.get<AuditEntry[]>(`/assets/${id}/history`);
    return data;
  },
};
