import { assetApi } from "./apiClients";
import type { User, UserCreatePayload, UserUpdatePayload } from "@/types/auth";

export const userService = {
  getAll: async (): Promise<User[]> => {
    const { data } = await assetApi.get<User[]>("/users/");
    return data;
  },

  create: async (payload: UserCreatePayload): Promise<User> => {
    const { data } = await assetApi.post<User>("/auth/register", payload);
    return data;
  },

  update: async (id: number, payload: UserUpdatePayload): Promise<User> => {
    const { data } = await assetApi.patch<User>(`/users/${id}`, payload);
    return data;
  },

  resetPassword: async (id: number, newPassword: string): Promise<void> => {
    await assetApi.post(`/users/${id}/reset-password`, {
      new_password: newPassword,
    });
  },
};
