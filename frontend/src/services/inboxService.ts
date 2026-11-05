import { assetApi } from "./apiClients";
import type { InboxResponse } from "@/types/inbox";

export const inboxService = {
  get: async (limit = 15): Promise<InboxResponse> => {
    const { data } = await assetApi.get<InboxResponse>("/inbox/", {
      params: { limit },
    });
    return data;
  },

  markRead: async (id: number): Promise<void> => {
    await assetApi.put(`/inbox/${id}/read`);
  },

  markAllRead: async (): Promise<void> => {
    await assetApi.put("/inbox/read-all");
  },
};
