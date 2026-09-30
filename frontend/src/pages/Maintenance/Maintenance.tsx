import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import Alert from "@/components/common/Alert";
import Badge from "@/components/common/Badge";
import Button from "@/components/common/Button";
import Card from "@/components/common/Card";
import Icon from "@/components/common/Icon";
import Modal from "@/components/common/Modal";
import PageHeader from "@/components/common/PageHeader";
import { SkeletonTable } from "@/components/common/Skeleton";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import Textarea from "@/components/common/Textarea";
import { useAuth } from "@/hooks/useAuth";
import { useFetch } from "@/hooks/useFetch";
import { assetService } from "@/services/assetService";
import { maintenanceService } from "@/services/maintenanceService";
import type { Asset } from "@/types/asset";
import type { MaintenanceRecord, MaintenanceStatus } from "@/types/maintenance";
import { getErrorMessage } from "@/utils/errors";
import { formatDate } from "@/utils/format";
import { MAINTENANCE_STATUS, MAINTENANCE_TYPE_LABEL } from "@/utils/labels";
import StartMaintenanceModal from "./StartMaintenanceModal";

type Filter = MaintenanceStatus | "todos";

const TABS: { value: Filter; label: string }[] = [
  { value: "en_proceso", label: "En proceso" },
  { value: "finalizado", label: "Finalizados" },
  { value: "todos", label: "Todos" },
];

function Maintenance() {
  const { user } = useAuth();
  const canManage =
    user?.role === "administrador" || user?.role === "almacenista";

  const [filter, setFilter] = useState<Filter>("en_proceso");
  const fetchList = useCallback(
    () =>
      maintenanceService.getAll({
        status: filter === "todos" ? undefined : filter,
      }),
    [filter],
  );
  const {
    data: records,
    isLoading,
    error,
    refetch,
  } = useFetch<MaintenanceRecord[]>(fetchList);

  const fetchAvailable = useCallback(() => assetService.getAvailable(), []);
  const { data: availableAssets, refetch: refetchAssets } =
    useFetch<Asset[]>(fetchAvailable);

  const [isStartOpen, setIsStartOpen] = useState(false);
  const [finishing, setFinishing] = useState<MaintenanceRecord | null>(null);
  const [finishNotes, setFinishNotes] = useState("");
  const [finishError, setFinishError] = useState("");
  const [isFinishing, setIsFinishing] = useState(false);

  const closeFinish = () => {
    setFinishing(null);
    setFinishNotes("");
    setFinishError("");
  };

  const handleFinish = async () => {
    if (!finishing) return;
    setIsFinishing(true);
    setFinishError("");
    try {
      await maintenanceService.finish(
        finishing.id,
        finishNotes.trim() || undefined,
      );
      closeFinish();
      refetch();
      refetchAssets();
    } catch (err) {
      setFinishError(
        getErrorMessage(err, "No se pudo finalizar el mantenimiento"),
      );
    } finally {
      setIsFinishing(false);
    }
  };

  const columns: TableColumn<MaintenanceRecord>[] = [
    {
      key: "asset",
      label: "Activo",
      render: (item) => (
        <Link to={`/inventario/${item.asset_id}`}>
          {item.asset_name ?? `#${item.asset_id}`}
        </Link>
      ),
    },
    {
      key: "assigned_to",
      label: "Asignado a",
      render: (item) => <span className="cell-strong">{item.assigned_to}</span>,
    },
    {
      key: "maintenance_type",
      label: "Tipo",
      render: (item) => MAINTENANCE_TYPE_LABEL[item.maintenance_type],
    },
    { key: "reason", label: "Motivo" },
    {
      key: "started_at",
      label: "Inicio",
      render: (item) => formatDate(item.started_at),
    },
    {
      key: "expected_end_date",
      label: "Prevista",
      render: (item) => formatDate(item.expected_end_date),
    },
    {
      key: "status",
      label: "Estado",
      render: (item) => (
        <Badge tone={MAINTENANCE_STATUS[item.status].tone}>
          {MAINTENANCE_STATUS[item.status].label}
        </Badge>
      ),
    },
    {
      key: "actions",
      label: "Acción",
      render: (item) =>
        canManage && item.status === "en_proceso" ? (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setFinishing(item)}
          >
            Finalizar
          </Button>
        ) : (
          "—"
        ),
    },
  ];

  return (
    <div className="page">
      <PageHeader
        title="Mantenimiento"
        subtitle="Cada mantenimiento queda asignado a una persona responsable."
        actions={
          canManage ? (
            <Button onClick={() => setIsStartOpen(true)}>
              <Icon name="plus" size={16} /> Enviar a mantenimiento
            </Button>
          ) : null
        }
      />

      <div className="tabs" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.value}
            role="tab"
            aria-selected={filter === tab.value}
            className={`tab ${filter === tab.value ? "tab-active" : ""}`}
            onClick={() => setFilter(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <Card>
        {isLoading && <SkeletonTable rows={4} columns={6} />}
        {error && <Alert>{error}</Alert>}
        {!isLoading && !error && (
          <Table<MaintenanceRecord>
            columns={columns}
            data={records ?? []}
            keyExtractor={(item) => item.id}
            emptyMessage="No hay mantenimientos en esta vista"
          />
        )}
      </Card>

      <StartMaintenanceModal
        isOpen={isStartOpen}
        onClose={() => setIsStartOpen(false)}
        onCreated={() => {
          refetch();
          refetchAssets();
        }}
        assets={availableAssets ?? []}
      />

      <Modal
        isOpen={finishing !== null}
        onClose={closeFinish}
        title="Finalizar mantenimiento"
      >
        {finishing && (
          <div className="form-stack">
            <p>
              <strong>
                {finishing.asset_name ?? `#${finishing.asset_id}`}
              </strong>{" "}
              a cargo de <strong>{finishing.assigned_to}</strong>. Al finalizar,
              el activo vuelve a estar disponible.
            </p>
            <Textarea
              label="Observaciones (opcional)"
              value={finishNotes}
              onChange={(e) => setFinishNotes(e.target.value)}
              placeholder="Trabajo realizado"
            />
            {finishError && <Alert>{finishError}</Alert>}
            <div className="form-actions">
              <Button variant="secondary" onClick={closeFinish}>
                Cancelar
              </Button>
              <Button onClick={handleFinish} isLoading={isFinishing}>
                Finalizar mantenimiento
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default Maintenance;
