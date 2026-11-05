import { assetApi } from "./apiClients";
import type {
  LabRunPayload,
  LabRunResult,
  NotificationEntry,
} from "@/types/notification";

export const notificationService = {
  getAll: async (status?: string, limit = 50): Promise<NotificationEntry[]> => {
    const { data } = await assetApi.get<NotificationEntry[]>(
      "/notifications/",
      { params: { status, limit } },
    );
    return data;
  },

  runLab: async (payload: LabRunPayload): Promise<LabRunResult> => {
    const { data } = await assetApi.post<LabRunResult>(
      "/lab/notifications",
      payload,
    );
    return data;
  },
};
