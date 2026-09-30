import { assetApi } from "./apiClients";
import type {
  LoginPayload,
  PasswordChangePayload,
  TokenResponse,
  User,
} from "@/types/auth";

export const authService = {
  login: async ({
    username,
    password,
  }: LoginPayload): Promise<TokenResponse> => {
    const body = new URLSearchParams();
    body.append("username", username);
    body.append("password", password);
    const { data } = await assetApi.post<TokenResponse>("/auth/login", body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return data;
  },

  getMe: async (): Promise<User> => {
    const { data } = await assetApi.get<User>("/auth/me");
    return data;
  },

  changePassword: async (payload: PasswordChangePayload): Promise<void> => {
    await assetApi.post("/auth/change-password", payload);
  },
};
