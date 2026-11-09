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
  baja: { label: "Dado de baja", tone: "neutral" },
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

export const MAINTENANCE_LOCATION_LABEL: Record<string, string> = {
  interno: "Interno",
  externo: "Proveedor externo",
};

export const MAINTENANCE_SOURCE_LABEL: Record<string, string> = {
  manual: "Registrado manualmente",
  devolucion_con_novedad: "Devolución con novedad",
};

export const DOCUMENT_TYPE_LABEL: Record<string, string> = {
  CC: "Cédula de ciudadanía",
  TI: "Tarjeta de identidad",
  CE: "Cédula de extranjería",
  PASAPORTE: "Pasaporte",
};

export const ROLE_LABEL: Record<UserRole, string> = {
  administrador: "Administrador",
  almacenista: "Almacenista",
  jefe_de_planta: "Jefe de planta",
  gerente: "Gerente",
};

export function roleText(role: string | null): string {
  if (!role) return "";
  if (role === "sistema") return "Sistema";
  return ROLE_LABEL[role as UserRole] ?? role;
}

export const NOTIFICATION_STATUS: Record<string, LabelTone> = {
  enviado: { label: "Enviado", tone: "success" },
  simulado: { label: "Simulado", tone: "info" },
  fallido: { label: "Fallido", tone: "danger" },
  sin_destinatario: { label: "Sin destinatario", tone: "warning" },
};

export function notificationStatus(status: string): LabelTone {
  return NOTIFICATION_STATUS[status] ?? { label: status, tone: "neutral" };
}

export const EVENT_OPTIONS = [
  { value: "activo_registrado", label: "Ingreso de un activo" },
  { value: "activo_dado_de_baja", label: "Activo dado de baja" },
  { value: "prestamo_creado", label: "Préstamo registrado" },
  { value: "prestamo_devuelto", label: "Devolución en buen estado" },
  { value: "devolucion_con_novedad", label: "Devolución con novedad" },
  { value: "prestamo_atrasado", label: "Préstamo atrasado" },
  { value: "mantenimiento_iniciado", label: "Mantenimiento iniciado" },
  {
    value: "mantenimiento_escalado_externo",
    label: "Mantenimiento escalado a externo",
  },
  { value: "mantenimiento_finalizado", label: "Mantenimiento finalizado" },
];

const ACTIONS: Record<string, LabelTone> = {
  activo_registrado: { label: "Activo registrado", tone: "info" },
  activo_dado_de_baja: { label: "Activo dado de baja", tone: "danger" },
  prestamo_creado: { label: "Préstamo registrado", tone: "info" },
  prestamo_devuelto: { label: "Devolución registrada", tone: "success" },
  devolucion_con_novedad: { label: "Devolución con novedad", tone: "warning" },
  prestamo_atrasado: { label: "Préstamo atrasado", tone: "danger" },
  mantenimiento_iniciado: { label: "Mantenimiento iniciado", tone: "warning" },
  mantenimiento_escalado_externo: {
    label: "Mantenimiento escalado a externo",
    tone: "warning",
  },
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

export function actionMeta(action: string): LabelTone {
  return (
    ACTIONS[action] ?? { label: action.replace(/_/g, " "), tone: "neutral" }
  );
}
