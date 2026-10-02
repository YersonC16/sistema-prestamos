import { useEffect, useState, type FormEvent } from "react";
import Alert from "@/components/common/Alert";
import Button from "@/components/common/Button";
import Input from "@/components/common/Input";
import Modal from "@/components/common/Modal";
import Select from "@/components/common/Select";
import { responsibleService } from "@/services/responsibleService";
import type { DocumentType, Responsible } from "@/types/responsible";
import { getErrorMessage } from "@/utils/errors";

interface ResponsibleFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaved: (responsible: Responsible) => void;
  responsible?: Responsible | null; // si viene, es edición
}

function ResponsibleFormModal({
  isOpen,
  onClose,
  onSaved,
  responsible,
}: ResponsibleFormModalProps) {
  const isEdit = Boolean(responsible);

  const [fullName, setFullName] = useState("");
  const [documentType, setDocumentType] = useState<DocumentType>("CC");
  const [documentNumber, setDocumentNumber] = useState("");
  const [phone, setPhone] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      // Inicializa el formulario al abrir el modal (o al cambiar el
      // responsable a editar). Es síncrono a propósito, para que los
      // campos no "parpadeen" vacíos antes de mostrar los datos reales.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFullName(responsible?.full_name ?? "");
      setDocumentType(responsible?.document_type ?? "CC");
      setDocumentNumber(responsible?.document_number ?? "");
      setPhone(responsible?.phone ?? "");
      setIsActive(responsible?.is_active ?? true);
      setError("");
    }
  }, [isOpen, responsible]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (fullName.trim().length < 2)
      return setError("El nombre debe tener al menos 2 caracteres");
    if (!isEdit && documentNumber.trim().length < 4)
      return setError("Ingresa un número de documento válido");

    setIsSaving(true);
    setError("");
    try {
      let saved: Responsible;
      if (isEdit && responsible) {
        saved = await responsibleService.update(responsible.id, {
          full_name: fullName.trim(),
          phone: phone.trim() || undefined,
          is_active: isActive,
        });
      } else {
        saved = await responsibleService.create({
          full_name: fullName.trim(),
          document_type: documentType,
          document_number: documentNumber.trim(),
          phone: phone.trim() || undefined,
        });
      }
      onSaved(saved);
      onClose();
    } catch (err) {
      setError(getErrorMessage(err, "No se pudo guardar el responsable"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? "Editar responsable" : "Nuevo responsable"}
    >
      <form className="form-stack" onSubmit={handleSubmit}>
        <Input
          label="Nombre completo"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
        <Select
          label="Tipo de documento"
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value as DocumentType)}
          disabled={isEdit}
        >
          <option value="CC">Cédula de ciudadanía</option>
          <option value="TI">Tarjeta de identidad</option>
          <option value="CE">Cédula de extranjería</option>
          <option value="PASAPORTE">Pasaporte</option>
        </Select>
        <Input
          label="Número de documento"
          value={documentNumber}
          onChange={(e) => setDocumentNumber(e.target.value)}
          required
          disabled={isEdit}
        />
        <Input
          label="Teléfono (opcional)"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="3001234567"
        />
        {isEdit && (
          <Select
            label="Estado"
            value={String(isActive)}
            onChange={(e) => setIsActive(e.target.value === "true")}
          >
            <option value="true">Activo</option>
            <option value="false">Desactivado</option>
          </Select>
        )}
        {error && <Alert>{error}</Alert>}
        <div className="form-actions">
          <Button variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={isSaving}>
            {isEdit ? "Guardar cambios" : "Guardar responsable"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default ResponsibleFormModal;
