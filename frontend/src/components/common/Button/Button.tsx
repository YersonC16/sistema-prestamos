import type { ButtonHTMLAttributes, ReactNode } from "react";
import "./Button.css";

type ButtonVariant = "primary" | "secondary" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
  isLoading?: boolean;
}

function Button({
  children,
  variant = "primary",
  isLoading = false,
  disabled,
  className,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} ${className ?? ""}`}
      disabled={disabled || isLoading}
      {...rest}
    >
      {isLoading ? "Cargando..." : children}
    </button>
  );
}

export default Button;
