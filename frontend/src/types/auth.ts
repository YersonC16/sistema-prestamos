export type UserRole = "administrador" | "almacenista" | "personal_autorizado";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
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
}

export interface UserUpdatePayload {
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
}

export interface PasswordChangePayload {
  current_password: string;
  new_password: string;
}
