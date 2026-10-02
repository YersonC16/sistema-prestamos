import type { AssetStatus, AssetType } from "@/types/asset";
import type { UserRole } from "@/types/auth";
import type { LoanStatus } from "@/types/loan";
import type { MaintenanceStatus, MaintenanceType } from "@/types/maintenance";
import type { Tone } from "@/types/ui";

interface LabelTone {
  label: string;
  tone: Tone;
}

export const ASSET_STATUS: Record<AssetStatus, LabelTone> = {
  disponible: { label: "Disponible", tone: "success" },
  prestado: { label: "Prestado", tone: "info" },
  mantenimiento: { label: "Mantenimiento", tone: "warning" },
};

export const ASSET_TYPE_LABEL: Record<AssetType, string> = {
  equipo: "Equipo",
  herramienta: "Herramienta",
  otro: "Otro",
};

export const LOAN_STATUS: Record<LoanStatus, LabelTone> = {
  activo: { label: "Activo", tone: "info" },
  devuelto: { label: "Devuelto", tone: "success" },
  atrasado: { label: "Atrasado", tone: "danger" },
};

export const MAINTENANCE_STATUS: Record<MaintenanceStatus, LabelTone> = {
  en_proceso: { label: "En proceso", tone: "warning" },
  finalizado: { label: "Finalizado", tone: "success" },
};

export const MAINTENANCE_TYPE_LABEL: Record<MaintenanceType, string> = {
  preventivo: "Preventivo",
  correctivo: "Correctivo",
};

export const ROLE_LABEL: Record<UserRole, string> = {
  administrador: "Administrador",
  almacenista: "Almacenista",
  personal_autorizado: "Personal autorizado",
};

export function roleText(role: string | null): string {
  if (!role) return "";
  if (role === "sistema") return "Sistema";
  return ROLE_LABEL[role as UserRole] ?? role;
}

const ACTIONS: Record<string, LabelTone> = {
  activo_registrado: { label: "Activo registrado", tone: "info" },
  prestamo_creado: { label: "Préstamo registrado", tone: "info" },
  prestamo_devuelto: { label: "Devolución registrada", tone: "success" },
  devolucion_con_novedad: { label: "Devolución con novedad", tone: "warning" },
  prestamo_atrasado: { label: "Préstamo atrasado", tone: "danger" },
  mantenimiento_iniciado: { label: "Mantenimiento iniciado", tone: "warning" },
  mantenimiento_finalizado: {
    label: "Mantenimiento finalizado",
    tone: "success",
  },
  usuario_creado: { label: "Usuario creado", tone: "info" },
  usuario_modificado: { label: "Usuario modificado", tone: "neutral" },
  login_exitoso: { label: "Inicio de sesión", tone: "neutral" },
  login_fallido: { label: "Intento de sesión fallido", tone: "danger" },
  usuario_bloqueado_temporalmente: {
    label: "Usuario bloqueado temporalmente",
    tone: "danger",
  },
  password_cambiada: { label: "Contraseña cambiada", tone: "neutral" },
  password_restablecida: { label: "Contraseña restablecida", tone: "warning" },
};

export const DOCUMENT_TYPE_LABEL: Record<string, string> = {
  CC: "Cédula de ciudadanía",
  TI: "Tarjeta de identidad",
  CE: "Cédula de extranjería",
  PASAPORTE: "Pasaporte",
};

export const MAINTENANCE_LOCATION_LABEL: Record<string, string> = {
  interno: "Interno",
  externo: "Proveedor externo",
};

export const MAINTENANCE_SOURCE_LABEL: Record<string, string> = {
  manual: "Registrado manualmente",
  devolucion_con_novedad: "Devolución con novedad",
};

export function actionMeta(action: string): LabelTone {
  return (
    ACTIONS[action] ?? { label: action.replace(/_/g, " "), tone: "neutral" }
  );
}
