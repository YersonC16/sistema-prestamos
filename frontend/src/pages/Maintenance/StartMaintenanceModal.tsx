import { useState, type FormEvent } from "react";
import Alert from "@/components/common/Alert";
import Button from "@/components/common/Button";
import Input from "@/components/common/Input";
import Modal from "@/components/common/Modal";
import Select from "@/components/common/Select";
import Textarea from "@/components/common/Textarea";
import { maintenanceService } from "@/services/maintenanceService";
import type { Asset } from "@/types/asset";
import type { MaintenanceLocation, MaintenanceType } from "@/types/maintenance";
import { getErrorMessage } from "@/utils/errors";
import { endOfDayIso, todayInputValue } from "@/utils/format";

interface StartMaintenanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
  assets: Asset[];
  defaultAssetId?: number;
}

function StartMaintenanceModal({
  isOpen,
  onClose,
  onCreated,
  assets,
  defaultAssetId,
}: StartMaintenanceModalProps) {
  const initialAsset = defaultAssetId ? String(defaultAssetId) : "";
  const [assetId, setAssetId] = useState(initialAsset);
  const [location, setLocation] = useState<MaintenanceLocation>("interno");
  const [assignedTo, setAssignedTo] = useState("");
  const [providerName, setProviderName] = useState("");
  const [type, setType] = useState<MaintenanceType>("preventivo");
  const [reason, setReason] = useState("");
  const [expectedEnd, setExpectedEnd] = useState("");
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const close = () => {
    setAssetId(initialAsset);
    setLocation("interno");
    setAssignedTo("");
    setProviderName("");
    setType("preventivo");
    setReason("");
    setExpectedEnd("");
    setError("");
    onClose();
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!assetId) return setError("Selecciona el activo");
    if (location === "interno" && assignedTo.trim().length < 2)
      return setError("Indica a quién se asigna internamente");
    if (location === "externo" && providerName.trim().length < 2)
      return setError("Indica el proveedor o taller externo");
    if (reason.trim().length < 3)
      return setError("Describe el motivo del mantenimiento");
    if (expectedEnd && expectedEnd < todayInputValue())
      return setError("La fecha prevista no puede ser anterior a hoy");

    setIsSaving(true);
    setError("");
    try {
      await maintenanceService.start({
        asset_id: Number(assetId),
        location,
        assigned_to: location === "interno" ? assignedTo.trim() : undefined,
        provider_name: location === "externo" ? providerName.trim() : undefined,
        maintenance_type: type,
        reason: reason.trim(),
        expected_end_date: expectedEnd ? endOfDayIso(expectedEnd) : undefined,
      });
      close();
      onCreated();
    } catch (err) {
      setError(getErrorMessage(err, "No se pudo iniciar el mantenimiento"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={close} title="Enviar a mantenimiento">
      <form className="form-stack" onSubmit={handleSubmit}>
        <Select
          label="Activo"
          value={assetId}
          onChange={(e) => setAssetId(e.target.value)}
          disabled={Boolean(defaultAssetId)}
          required
        >
          <option value="">Selecciona un activo</option>
          {assets.map((asset) => (
            <option key={asset.id} value={asset.id}>
              {asset.name}
              {asset.code ? ` · ${asset.code}` : ""}
            </option>
          ))}
        </Select>

        <Select
          label="¿Dónde se atiende?"
          value={location}
          onChange={(e) => setLocation(e.target.value as MaintenanceLocation)}
        >
          <option value="interno">
            Mantenimiento interno (con personal propio)
          </option>
          <option value="externo">Proveedor o taller externo</option>
        </Select>

        {location === "interno" ? (
          <Input
            label="Asignado a"
            value={assignedTo}
            onChange={(e) => setAssignedTo(e.target.value)}
            placeholder="Persona o técnico responsable"
            required
          />
        ) : (
          <Input
            label="Proveedor o taller"
            value={providerName}
            onChange={(e) => setProviderName(e.target.value)}
            placeholder="Nombre del proveedor/taller"
            required
          />
        )}

        <Select
          label="Tipo de mantenimiento"
          value={type}
          onChange={(e) => setType(e.target.value as MaintenanceType)}
        >
          <option value="preventivo">Preventivo</option>
          <option value="correctivo">Correctivo</option>
        </Select>
        <Textarea
          label="Motivo"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Ej. Cambio de carbones, revisión general"
          required
        />
        <Input
          label="Fecha prevista de finalización (opcional)"
          type="date"
          min={todayInputValue()}
          value={expectedEnd}
          onChange={(e) => setExpectedEnd(e.target.value)}
        />
        {error && <Alert>{error}</Alert>}
        <div className="form-actions">
          <Button variant="secondary" onClick={close}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={isSaving}>
            Iniciar mantenimiento
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default StartMaintenanceModal;
