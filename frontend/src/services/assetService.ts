import { assetApi } from "./apiClients";
import type { Asset, AssetCreatePayload } from "@/types/asset";

export const assetService = {
  getAll: async (): Promise<Asset[]> => {
    const { data } = await assetApi.get<Asset[]>("/assets/");
    return data;
  },

  getAvailable: async (): Promise<Asset[]> => {
    const { data } = await assetApi.get<Asset[]>("/assets/available");
    return data;
  },

  create: async (payload: AssetCreatePayload): Promise<Asset> => {
    const { data } = await assetApi.post<Asset>("/assets/", payload);
    return data;
  },
};
