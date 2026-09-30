export const PASSWORD_HINT =
  "Mínimo 8 caracteres, con mayúscula, minúscula y número";

/** Devuelve un mensaje de error, o null si la contraseña es válida. */
export function validatePassword(value: string): string | null {
  if (value.length < 8) return "La contraseña debe tener al menos 8 caracteres";
  if (!/[A-Z]/.test(value)) return "La contraseña debe incluir una mayúscula";
  if (!/[a-z]/.test(value)) return "La contraseña debe incluir una minúscula";
  if (!/\d/.test(value)) return "La contraseña debe incluir un número";
  return null;
}
