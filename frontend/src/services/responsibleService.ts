import { loanApi } from "./apiClients";
import type {
  Responsible,
  ResponsibleCreatePayload,
  ResponsibleUpdatePayload,
} from "@/types/responsible";

export const responsibleService = {
  getAll: async (activeOnly = false): Promise<Responsible[]> => {
    const { data } = await loanApi.get<Responsible[]>("/responsibles/", {
      params: { active_only: activeOnly },
    });
    return data;
  },

  create: async (payload: ResponsibleCreatePayload): Promise<Responsible> => {
    const { data } = await loanApi.post<Responsible>("/responsibles/", payload);
    return data;
  },

  update: async (
    id: number,
    payload: ResponsibleUpdatePayload,
  ): Promise<Responsible> => {
    const { data } = await loanApi.patch<Responsible>(
      `/responsibles/${id}`,
      payload,
    );
    return data;
  },
};
