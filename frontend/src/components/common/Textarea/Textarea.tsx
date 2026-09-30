import { useId, type TextareaHTMLAttributes } from "react";
import "../Input/Input.css";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

function Textarea({ label, error, className, id, ...rest }: TextareaProps) {
  const generatedId = useId();
  const textareaId = id ?? generatedId;
  return (
    <div className="input-group">
      {label && (
        <label htmlFor={textareaId} className="input-label">
          {label}
        </label>
      )}
      <textarea
        id={textareaId}
        className={`input-field ${error ? "input-error" : ""} ${className ?? ""}`}
        {...rest}
      />
      {error && <span className="input-error-message">{error}</span>}
    </div>
  );
}

export default Textarea;
