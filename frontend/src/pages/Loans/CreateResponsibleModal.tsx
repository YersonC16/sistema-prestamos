import { useState, type FormEvent } from "react";
import Alert from "@/components/common/Alert";
import Button from "@/components/common/Button";
import Input from "@/components/common/Input";
import Modal from "@/components/common/Modal";
import Select from "@/components/common/Select";
import { responsibleService } from "@/services/responsibleService";
import type { DocumentType, Responsible } from "@/types/responsible";
import { getErrorMessage } from "@/utils/errors";

interface CreateResponsibleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (responsible: Responsible) => void;
}

function CreateResponsibleModal({
  isOpen,
  onClose,
  onCreated,
}: CreateResponsibleModalProps) {
  const [fullName, setFullName] = useState("");
  const [documentType, setDocumentType] = useState<DocumentType>("CC");
  const [documentNumber, setDocumentNumber] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const close = () => {
    setFullName("");
    setDocumentType("CC");
    setDocumentNumber("");
    setPhone("");
    setError("");
    onClose();
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (fullName.trim().length < 2)
      return setError("El nombre debe tener al menos 2 caracteres");
    if (documentNumber.trim().length < 4)
      return setError("Ingresa un número de documento válido");

    setIsSaving(true);
    setError("");
    try {
      const responsible = await responsibleService.create({
        full_name: fullName.trim(),
        document_type: documentType,
        document_number: documentNumber.trim(),
        phone: phone.trim() || undefined,
      });
      onCreated(responsible);
      close();
    } catch (err) {
      setError(getErrorMessage(err, "No se pudo registrar el responsable"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={close} title="Nuevo responsable">
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
        />
        <Input
          label="Teléfono (opcional)"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="3001234567"
        />
        {error && <Alert>{error}</Alert>}
        <div className="form-actions">
          <Button variant="secondary" onClick={close}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={isSaving}>
            Guardar responsable
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default CreateResponsibleModal;
