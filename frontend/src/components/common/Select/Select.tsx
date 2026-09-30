import { useId, type SelectHTMLAttributes } from "react";
import "../Input/Input.css";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

function Select({
  label,
  error,
  className,
  id,
  children,
  ...rest
}: SelectProps) {
  const generatedId = useId();
  const selectId = id ?? generatedId;
  return (
    <div className="input-group">
      {label && (
        <label htmlFor={selectId} className="input-label">
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={`input-field ${error ? "input-error" : ""} ${className ?? ""}`}
        {...rest}
      >
        {children}
      </select>
      {error && <span className="input-error-message">{error}</span>}
    </div>
  );
}

export default Select;
