import { useState, type FormEvent } from "react";
import Alert from "@/components/common/Alert";
import Button from "@/components/common/Button";
import Modal from "@/components/common/Modal";
import Textarea from "@/components/common/Textarea";
import { assetService } from "@/services/assetService";
import type { AssetDetail } from "@/types/asset";
import { getErrorMessage } from "@/utils/errors";

interface DecommissionModalProps {
  asset: AssetDetail;
  isOpen: boolean;
  onClose: () => void;
  onDone: () => void;
}

function DecommissionModal({
  asset,
  isOpen,
  onClose,
  onDone,
}: DecommissionModalProps) {
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const close = () => {
    setReason("");
    setError("");
    onClose();
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (reason.trim().length < 5)
      return setError("Describe el motivo de la baja (mínimo 5 caracteres)");

    setIsSaving(true);
    setError("");
    try {
      await assetService.decommission(asset.id, { reason: reason.trim() });
      close();
      onDone();
    } catch (err) {
      setError(getErrorMessage(err, "No se pudo dar de baja el activo"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={close} title="Dar de baja el activo">
      <form className="form-stack" onSubmit={handleSubmit}>
        <p>
          Vas a dar de baja <strong>{asset.name}</strong>
          {asset.code ? ` (${asset.code})` : ""}.
        </p>
        <Alert>
          Esta acción es definitiva: el activo no volverá a prestarse ni a
          enviarse a mantenimiento. Quedará en el historial con el motivo y tu
          nombre, y se avisará al jefe de planta.
        </Alert>
        <Textarea
          label="Motivo de la baja"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Ej. Irreparable, obsoleto, extraviado"
          required
        />
        {error && <Alert>{error}</Alert>}
        <div className="form-actions">
          <Button variant="secondary" onClick={close}>
            Cancelar
          </Button>
          <Button type="submit" variant="danger" isLoading={isSaving}>
            Confirmar baja
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default DecommissionModal;
