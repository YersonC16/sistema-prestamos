import type { InputHTMLAttributes } from "react";
import "./Input.css";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

function Input({ label, error, className, id, ...rest }: InputProps) {
  return (
    <div className="input-group">
      {label && (
        <label htmlFor={id} className="input-label">
          {label}
        </label>
      )}
      <input
        id={id}
        className={`input-field ${error ? "input-error" : ""} ${className ?? ""}`}
        {...rest}
      />
      {error && <span className="input-error-message">{error}</span>}
    </div>
  );
}

export default Input;
