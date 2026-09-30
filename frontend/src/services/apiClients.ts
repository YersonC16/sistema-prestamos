import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

const TOKEN_KEY = "auth_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

function attachToken(
  config: InternalAxiosRequestConfig,
): InternalAxiosRequestConfig {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}

function handleResponseError(error: AxiosError): Promise<never> {
  const isLoginRequest = error.config?.url?.includes("/auth/login") ?? false;
  if (error.response?.status === 401 && !isLoginRequest && getToken()) {
    clearToken();
    if (window.location.pathname !== "/login") {
      window.location.assign("/login");
    }
  }
  return Promise.reject(error);
}

function createClient(baseURL: string) {
  const client = axios.create({
    baseURL,
    headers: { "Content-Type": "application/json" },
    timeout: 15000,
  });
  client.interceptors.request.use(attachToken);
  client.interceptors.response.use((response) => response, handleResponseError);
  return client;
}

export const assetApi = createClient(import.meta.env.VITE_ASSET_SERVICE_URL);
export const loanApi = createClient(import.meta.env.VITE_LOAN_SERVICE_URL);
