import { useCallback, useMemo, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import Alert from "@/components/common/Alert";
import Badge from "@/components/common/Badge";
import Button from "@/components/common/Button";
import Card from "@/components/common/Card";
import Icon from "@/components/common/Icon";
import Input from "@/components/common/Input";
import Modal from "@/components/common/Modal";
import PageHeader from "@/components/common/PageHeader";
import Select from "@/components/common/Select";
import { SkeletonTable } from "@/components/common/Skeleton";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import { useAuth } from "@/hooks/useAuth";
import { useFetch } from "@/hooks/useFetch";
import { assetService } from "@/services/assetService";
import type { Asset, AssetStatus, AssetType } from "@/types/asset";
import { getErrorMessage } from "@/utils/errors";
import { ASSET_STATUS, ASSET_TYPE_LABEL } from "@/utils/labels";
import Pagination from "@/components/common/Pagination";
import { usePagination } from "@/hooks/usePagination";

const columns: TableColumn<Asset>[] = [
  { key: "code", label: "Código" },
  {
    key: "name",
    label: "Nombre",
    render: (asset) => <span className="cell-strong">{asset.name}</span>,
  },
  {
    key: "asset_type",
    label: "Tipo",
    render: (asset) => ASSET_TYPE_LABEL[asset.asset_type],
  },
  {
    key: "status",
    label: "Estado",
    render: (asset) => (
      <Badge tone={ASSET_STATUS[asset.status].tone}>
        {ASSET_STATUS[asset.status].label}
      </Badge>
    ),
  },
  { key: "description", label: "Descripción" },
];

function Inventory() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const canManage =
    user?.role === "administrador" || user?.role === "almacenista";

  const fetchAssets = useCallback(() => assetService.getAll(), []);
  const {
    data: assets,
    isLoading,
    error,
    refetch,
  } = useFetch<Asset[]>(fetchAssets);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<AssetStatus | "">("");
  const [typeFilter, setTypeFilter] = useState<AssetType | "">("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [assetType, setAssetType] = useState<AssetType>("herramienta");
  const [description, setDescription] = useState("");
  const [formError, setFormError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    return (assets ?? []).filter(
      (asset) =>
        (!statusFilter || asset.status === statusFilter) &&
        (!typeFilter || asset.asset_type === typeFilter) &&
        (!term ||
          asset.name.toLowerCase().includes(term) ||
          (asset.code ?? "").toLowerCase().includes(term)),
    );
  }, [assets, search, statusFilter, typeFilter]);

  const { page, setPage, totalPages, pageItems, total } = usePagination(
    filtered,
    10,
  );

  const closeModal = () => {
    setIsModalOpen(false);
    setName("");
    setCode("");
    setAssetType("herramienta");
    setDescription("");
    setFormError("");
  };

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (name.trim().length < 2) {
      setFormError("El nombre debe tener al menos 2 caracteres");
      return;
    }
    setIsSaving(true);
    setFormError("");
    try {
      await assetService.create({
        name: name.trim(),
        asset_type: assetType,
        code: code.trim() || undefined,
        description: description.trim() || undefined,
      });
      closeModal();
      refetch();
    } catch (err) {
      setFormError(getErrorMessage(err, "No se pudo registrar el activo"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="page">
      <PageHeader
        title="Inventario"
        subtitle="Equipos y herramientas de la sede. Toca un activo para ver su ficha y su historial."
        actions={
          canManage ? (
            <Button onClick={() => setIsModalOpen(true)}>
              <Icon name="plus" size={16} /> Registrar activo
            </Button>
          ) : null
        }
      />

      <div className="toolbar">
        <Input
          label="Buscar"
          placeholder="Nombre o código"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select
          label="Estado"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as AssetStatus | "")}
        >
          <option value="">Todos</option>
          <option value="disponible">Disponible</option>
          <option value="prestado">Prestado</option>
          <option value="mantenimiento">Mantenimiento</option>
        </Select>
        <Select
          label="Tipo"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as AssetType | "")}
        >
          <option value="">Todos</option>
          <option value="equipo">Equipo</option>
          <option value="herramienta">Herramienta</option>
          <option value="otro">Otro</option>
        </Select>
      </div>

      <Card>
        {isLoading && <SkeletonTable rows={5} columns={5} />}
        {error && <Alert>{error}</Alert>}
        {!isLoading && !error && (
          <Table<Asset>
            columns={columns}
            data={pageItems}
            keyExtractor={(asset) => asset.id}
            onRowClick={(asset) => navigate(`/inventario/${asset.id}`)}
            emptyMessage="No hay activos que coincidan con la búsqueda"
          />
        )}
        <Pagination
          page={page}
          totalPages={totalPages}
          total={total}
          pageSize={10}
          onChange={setPage}
        />
      </Card>

      <Modal isOpen={isModalOpen} onClose={closeModal} title="Registrar activo">
        <form className="form-stack" onSubmit={handleCreate}>
          <Input
            label="Nombre"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ej. Taladro percutor"
            required
          />
          <Input
            label="Código (opcional, único)"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Ej. TAL-001"
          />
          <Select
            label="Tipo de activo"
            value={assetType}
            onChange={(e) => setAssetType(e.target.value as AssetType)}
          >
            <option value="equipo">Equipo</option>
            <option value="herramienta">Herramienta</option>
            <option value="otro">Otro</option>
          </Select>
          <Input
            label="Descripción (opcional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Marca, modelo, detalles"
          />
          {formError && <Alert>{formError}</Alert>}
          <div className="form-actions">
            <Button variant="secondary" onClick={closeModal}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSaving}>
              Guardar activo
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

export default Inventory;
