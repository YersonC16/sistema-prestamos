import { useState, type FormEvent } from "react";
import Alert from "@/components/common/Alert";
import Button from "@/components/common/Button";
import Input from "@/components/common/Input";
import Modal from "@/components/common/Modal";
import { authService } from "@/services/authService";
import { getErrorMessage } from "@/utils/errors";
import { PASSWORD_HINT, validatePassword } from "@/utils/validation";

interface ChangePasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
}

function ChangePasswordModal({ isOpen, onClose }: ChangePasswordModalProps) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const close = () => {
    setCurrent("");
    setNext("");
    setConfirm("");
    setError("");
    setDone(false);
    onClose();
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const passwordError = validatePassword(next);
    if (passwordError) return setError(passwordError);
    if (next !== confirm)
      return setError("La confirmación no coincide con la nueva contraseña");

    setIsSaving(true);
    setError("");
    try {
      await authService.changePassword({
        current_password: current,
        new_password: next,
      });
      setDone(true);
    } catch (err) {
      setError(getErrorMessage(err, "No se pudo cambiar la contraseña"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={close} title="Cambiar contraseña">
      {done ? (
        <div className="form-stack">
          <Alert tone="success">Tu contraseña fue actualizada.</Alert>
          <div className="form-actions">
            <Button onClick={close}>Cerrar</Button>
          </div>
        </div>
      ) : (
        <form className="form-stack" onSubmit={handleSubmit}>
          <Input
            label="Contraseña actual"
            type="password"
            value={current}
            onChange={(e) => setCurrent(e.target.value)}
            autoComplete="current-password"
            required
          />
          <Input
            label="Nueva contraseña"
            type="password"
            value={next}
            onChange={(e) => setNext(e.target.value)}
            hint={PASSWORD_HINT}
            autoComplete="new-password"
            required
          />
          <Input
            label="Confirmar nueva contraseña"
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            autoComplete="new-password"
            required
          />
          {error && <Alert>{error}</Alert>}
          <div className="form-actions">
            <Button variant="secondary" onClick={close}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSaving}>
              Guardar
            </Button>
          </div>
        </form>
      )}
    </Modal>
  );
}

export default ChangePasswordModal;
