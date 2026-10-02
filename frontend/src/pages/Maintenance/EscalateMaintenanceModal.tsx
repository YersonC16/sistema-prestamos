import { useState, type FormEvent } from "react";
import Alert from "@/components/common/Alert";
import Button from "@/components/common/Button";
import Input from "@/components/common/Input";
import Modal from "@/components/common/Modal";
import Textarea from "@/components/common/Textarea";
import { maintenanceService } from "@/services/maintenanceService";
import type { MaintenanceRecord } from "@/types/maintenance";
import { getErrorMessage } from "@/utils/errors";

interface EscalateMaintenanceModalProps {
  maintenance: MaintenanceRecord;
  onClose: () => void;
  onEscalated: () => void;
}

function EscalateMaintenanceModal({
  maintenance,
  onClose,
  onEscalated,
}: EscalateMaintenanceModalProps) {
  const [providerName, setProviderName] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (providerName.trim().length < 2)
      return setError("Indica el proveedor o taller al que se envía");

    setIsSaving(true);
    setError("");
    try {
      await maintenanceService.escalate(maintenance.id, {
        provider_name: providerName.trim(),
        notes: notes.trim() || undefined,
      });
      onEscalated();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err, "No se pudo escalar el mantenimiento"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal isOpen onClose={onClose} title="Escalar a mantenimiento externo">
      <form className="form-stack" onSubmit={handleSubmit}>
        <p>
          <strong>
            {maintenance.asset_name ?? `#${maintenance.asset_id}`}
          </strong>{" "}
          no se pudo resolver con <strong>{maintenance.assigned_to}</strong>.
          Indica a qué proveedor o taller se envía.
        </p>
        <Input
          label="Proveedor o taller"
          value={providerName}
          onChange={(e) => setProviderName(e.target.value)}
          required
        />
        <Textarea
          label="Notas (opcional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Qué se intentó internamente"
        />
        {error && <Alert>{error}</Alert>}
        <div className="form-actions">
          <Button variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={isSaving}>
            Enviar a externo
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default EscalateMaintenanceModal;
