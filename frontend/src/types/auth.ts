export type UserRole =
  | "administrador"
  | "almacenista"
  | "jefe_de_planta"
  | "gerente";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  site: string;
  is_active: boolean;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserCreatePayload {
  full_name: string;
  email: string;
  password: string;
  role: UserRole;
  site?: string;
}

export interface UserUpdatePayload {
  full_name?: string;
  role?: UserRole;
  site?: string;
  is_active?: boolean;
}

export interface PasswordChangePayload {
  current_password: string;
  new_password: string;
}
