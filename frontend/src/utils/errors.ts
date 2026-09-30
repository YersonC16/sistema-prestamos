import axios from "axios";

/** Convierte cualquier error en un mensaje legible para el usuario. */
export function getErrorMessage(
  error: unknown,
  fallback = "Ocurrió un error inesperado",
): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return "No se pudo conectar con el servidor. Verifica tu conexión.";
    }
    const data = error.response.data as { detail?: unknown } | undefined;
    const detail = data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: unknown };
      if (typeof first?.msg === "string")
        return first.msg.replace(/^Value error, /, "");
    }
    return fallback;
  }
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}
