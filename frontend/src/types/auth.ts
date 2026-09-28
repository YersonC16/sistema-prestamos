export type UserRole = "administrador" | "almacenista" | "personal_autorizado";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
