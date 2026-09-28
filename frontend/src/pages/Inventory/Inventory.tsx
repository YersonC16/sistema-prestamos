import { useState, useCallback } from "react";
import Card from "@/components/common/Card";
import Button from "@/components/common/Button";
import Input from "@/components/common/Input";
import Modal from "@/components/common/Modal";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import { SkeletonTable } from "@/components/common/Skeleton";
import { useFetch } from "@/hooks/useFetch";
import { assetService } from "@/services/assetService";
import type { Asset, AssetType } from "@/types/asset";
import "./Inventory.css";
import { useAuth } from "@/hooks/useAuth";

const STATUS_LABELS: Record<string, string> = {
  disponible: "Disponible",
  prestado: "Prestado",
  mantenimiento: "Mantenimiento",
};

function Inventory() {
  const fetchAssets = useCallback(() => assetService.getAll(), []);
  const {
    data: assets,
    isLoading,
    error,
    refetch,
  } = useFetch<Asset[]>(fetchAssets);

  const { user } = useAuth();
  const canManageAssets =
    user?.role === "administrador" || user?.role === "almacenista";

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [assetType, setAssetType] = useState<AssetType>("equipo");
  const [description, setDescription] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [formError, setFormError] = useState("");

  const columns: TableColumn<Asset>[] = [
    { key: "name", label: "Nombre" },
    { key: "asset_type", label: "Tipo" },
    {
      key: "status",
      label: "Estado",
      render: (row) => STATUS_LABELS[row.status] ?? row.status,
    },
    { key: "description", label: "Descripción" },
  ];

  const handleCreate = async () => {
    if (!name.trim()) {
      setFormError("El nombre es obligatorio");
      return;
    }
    setIsSaving(true);
    setFormError("");
    try {
      await assetService.create({ name, asset_type: assetType, description });
      setName("");
      setDescription("");
      setAssetType("equipo");
      setIsModalOpen(false);
      refetch();
    } catch {
      setFormError("No se pudo registrar el activo. Intenta de nuevo.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="inventory-page">
      <div className="inventory-header">
        <h2>Inventario de activos</h2>
        {canManageAssets && (
          <Button onClick={() => setIsModalOpen(true)}>
            + Registrar activo
          </Button>
        )}
      </div>

      <Card>
        {isLoading && <SkeletonTable rows={4} columns={4} />}
        {error && <p className="inventory-error">{error}</p>}
        {!isLoading && !error && (
          <Table<Asset>
            columns={columns}
            data={assets ?? []}
            keyExtractor={(row) => row.id}
          />
        )}
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Registrar nuevo activo"
      >
        <div className="inventory-form">
          <Input
            label="Nombre"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ej. Taladro"
          />

          <div className="input-group">
            <label className="input-label">Tipo de activo</label>
            <select
              className="input-field"
              value={assetType}
              onChange={(e) => setAssetType(e.target.value as AssetType)}
            >
              <option value="equipo">Equipo</option>
              <option value="herramienta">Herramienta</option>
              <option value="otro">Otro</option>
            </select>
          </div>

          <Input
            label="Descripción (opcional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Detalles adicionales"
          />

          {formError && <p className="inventory-error">{formError}</p>}

          <Button onClick={handleCreate} isLoading={isSaving}>
            Guardar activo
          </Button>
        </div>
      </Modal>
    </div>
  );
}

export default Inventory;
