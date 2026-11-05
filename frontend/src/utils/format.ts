// Las fechas de préstamos llegan sin zona horaria (son UTC). Sin la "Z",
// el navegador las interpretaría como hora local y mostraría 5 horas de diferencia.
const HAS_TIMEZONE = /(Z|[+-]\d{2}:?\d{2})$/;

export function parseServerDate(value: string): Date {
  return new Date(HAS_TIMEZONE.test(value) ? value : `${value}Z`);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return parseServerDate(value).toLocaleDateString("es-CO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  return parseServerDate(value).toLocaleString("es-CO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Fecha de hoy en formato yyyy-mm-dd (hora local), para <input type="date">. */
export function todayInputValue(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

/** Convierte una fecha elegida (yyyy-mm-dd) al final de ese día, en ISO. */
export function endOfDayIso(dateInput: string): string {
  const [year, month, day] = dateInput.split("-").map(Number);
  return new Date(year, month - 1, day, 23, 59, 0).toISOString();
}

export function isOverdue(expectedReturn: string, status: string): boolean {
  return (
    status !== "devuelto" &&
    parseServerDate(expectedReturn).getTime() < Date.now()
  );
}

export function firstName(fullName: string): string {
  return fullName.trim().split(/\s+/)[0] || fullName;
}

export function initials(fullName: string): string {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  return ((parts[0]?.[0] ?? "") + (parts[1]?.[0] ?? "")).toUpperCase() || "?";
}

/** Tiempo transcurrido en lenguaje natural: "hace 5 min". Pasadas 24 horas muestra la fecha. */
export function timeAgo(value: string): string {
  const seconds = Math.max(
    0,
    Math.floor((Date.now() - parseServerDate(value).getTime()) / 1000),
  );
  if (seconds < 60) return "hace un momento";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `hace ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `hace ${hours} h`;
  return formatDateTime(value);
}
