import { assetApi } from "./apiClients";
import type { AuditEntry } from "@/types/asset";

export const auditService = {
  getAll: async (entityType?: string, limit = 100): Promise<AuditEntry[]> => {
    const { data } = await assetApi.get<AuditEntry[]>("/audit/", {
      params: { entity_type: entityType, limit },
    });
    return data;
  },
};
