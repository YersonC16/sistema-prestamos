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
import {
  MAINTENANCE_LOCATION_LABEL,
  MAINTENANCE_SOURCE_LABEL,
  MAINTENANCE_STATUS,
  MAINTENANCE_TYPE_LABEL,
} from "@/utils/labels";
import EscalateMaintenanceModal from "./EscalateMaintenanceModal";
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
  const [escalating, setEscalating] = useState<MaintenanceRecord | null>(null);
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
      key: "location",
      label: "Dónde",
      render: (item) => (
        <>
          <Badge tone={item.location === "interno" ? "info" : "warning"}>
            {MAINTENANCE_LOCATION_LABEL[item.location]}
          </Badge>
          <div className="muted" style={{ fontSize: "12px", marginTop: "4px" }}>
            {item.location === "interno"
              ? item.assigned_to
              : item.provider_name}
          </div>
        </>
      ),
    },
    {
      key: "maintenance_type",
      label: "Tipo",
      render: (item) => MAINTENANCE_TYPE_LABEL[item.maintenance_type],
    },
    { key: "reason", label: "Motivo" },
    {
      key: "source",
      label: "Origen",
      render: (item) => (
        <span className="muted" style={{ fontSize: "12px" }}>
          {MAINTENANCE_SOURCE_LABEL[item.source]}
          {item.source === "devolucion_con_novedad" &&
            item.source_loan_id &&
            ` (préstamo #${item.source_loan_id})`}
        </span>
      ),
    },
    {
      key: "started_at",
      label: "Inicio",
      render: (item) => formatDate(item.started_at),
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
          <div className="cell-actions">
            {item.location === "interno" && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setEscalating(item)}
              >
                Escalar a externo
              </Button>
            )}
            <Button
              size="sm"
              variant="secondary"
              onClick={() => setFinishing(item)}
            >
              Finalizar
            </Button>
          </div>
        ) : (
          "—"
        ),
    },
  ];

  return (
    <div className="page">
      <PageHeader
        title="Mantenimiento"
        subtitle="Interno (personal propio) o externo (proveedor/taller). Un mantenimiento interno sin solución se puede escalar a externo."
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
        {isLoading && <SkeletonTable rows={4} columns={7} />}
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

      {escalating && (
        <EscalateMaintenanceModal
          maintenance={escalating}
          onClose={() => setEscalating(null)}
          onEscalated={refetch}
        />
      )}

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
              a cargo de{" "}
              <strong>
                {finishing.location === "interno"
                  ? finishing.assigned_to
                  : finishing.provider_name}
              </strong>
              . Al finalizar, el activo vuelve a estar disponible.
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
