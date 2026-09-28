import axios from "axios";

const TOKEN_KEY = "auth_token";

export const assetApi = axios.create({
  baseURL: import.meta.env.VITE_ASSET_SERVICE_URL,
  headers: { "Content-Type": "application/json" },
});

export const loanApi = axios.create({
  baseURL: import.meta.env.VITE_LOAN_SERVICE_URL,
  headers: { "Content-Type": "application/json" },
});

function attachToken(config: import("axios").InternalAxiosRequestConfig) {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}

assetApi.interceptors.request.use(attachToken);
loanApi.interceptors.request.use(attachToken);

export function saveToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
