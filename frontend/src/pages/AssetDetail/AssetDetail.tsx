import { useCallback, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Alert from "@/components/common/Alert";
import Badge from "@/components/common/Badge";
import Button from "@/components/common/Button";
import Card from "@/components/common/Card";
import Icon from "@/components/common/Icon";
import PageHeader from "@/components/common/PageHeader";
import { Skeleton, SkeletonTable } from "@/components/common/Skeleton";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import Timeline from "@/components/common/Timeline";
import { useAuth } from "@/hooks/useAuth";
import { useFetch } from "@/hooks/useFetch";
import StartMaintenanceModal from "@/pages/Maintenance/StartMaintenanceModal";
import { assetService } from "@/services/assetService";
import { loanService } from "@/services/loanService";
import { maintenanceService } from "@/services/maintenanceService";
import type { Asset, AuditEntry } from "@/types/asset";
import type { Loan } from "@/types/loan";
import type { MaintenanceRecord } from "@/types/maintenance";
import { formatDate, isOverdue } from "@/utils/format";
import {
  ASSET_STATUS,
  ASSET_TYPE_LABEL,
  LOAN_STATUS,
  MAINTENANCE_STATUS,
  MAINTENANCE_TYPE_LABEL,
} from "@/utils/labels";
import { toTimelineItems } from "@/utils/timeline";

const loanColumns: TableColumn<Loan>[] = [
  {
    key: "responsible_name",
    label: "Responsable",
    render: (loan) => (
      <span className="cell-strong">{loan.responsible_name}</span>
    ),
  },
  {
    key: "loan_date",
    label: "Prestado",
    render: (loan) => formatDate(loan.loan_date),
  },
  {
    key: "expected_return_date",
    label: "Prevista",
    render: (loan) => formatDate(loan.expected_return_date),
  },
  {
    key: "actual_return_date",
    label: "Devuelto",
    render: (loan) => formatDate(loan.actual_return_date),
  },
  {
    key: "status",
    label: "Estado",
    render: (loan) => (
      <Badge tone={LOAN_STATUS[loan.status].tone}>
        {LOAN_STATUS[loan.status].label}
      </Badge>
    ),
  },
];

const maintenanceColumns: TableColumn<MaintenanceRecord>[] = [
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
    key: "status",
    label: "Estado",
    render: (item) => (
      <Badge tone={MAINTENANCE_STATUS[item.status].tone}>
        {MAINTENANCE_STATUS[item.status].label}
      </Badge>
    ),
  },
];

function AssetDetail() {
  const { id } = useParams();
  const assetId = Number(id);
  const { user } = useAuth();
  const canManage =
    user?.role === "administrador" || user?.role === "almacenista";
  const [isMaintenanceOpen, setIsMaintenanceOpen] = useState(false);

  const fetchAsset = useCallback(
    () => assetService.getById(assetId),
    [assetId],
  );
  const fetchHolder = useCallback(
    () => loanService.getCurrentHolder(assetId),
    [assetId],
  );
  const fetchHistory = useCallback(
    () => assetService.getHistory(assetId),
    [assetId],
  );
  const fetchLoans = useCallback(
    () => loanService.getAll({ asset_id: assetId }),
    [assetId],
  );
  const fetchMaintenances = useCallback(
    () => maintenanceService.getAll({ asset_id: assetId }),
    [assetId],
  );

  const asset = useFetch<Asset>(fetchAsset);
  const holder = useFetch<Loan | null>(fetchHolder);
  const history = useFetch<AuditEntry[]>(fetchHistory);
  const loans = useFetch<Loan[]>(fetchLoans);
  const maintenances = useFetch<MaintenanceRecord[]>(fetchMaintenances);

  const openMaintenance = maintenances.data?.find(
    (item) => item.status === "en_proceso",
  );

  const refreshAll = () => {
    asset.refetch();
    holder.refetch();
    history.refetch();
    maintenances.refetch();
  };

  if (Number.isNaN(assetId)) {
    return <Alert>Identificador de activo inválido</Alert>;
  }

  return (
    <div className="page">
      <Link to="/inventario" className="back-link">
        <Icon name="arrowLeft" size={16} /> Volver al inventario
      </Link>

      {asset.isLoading && <Skeleton height="96px" borderRadius="14px" />}
      {asset.error && <Alert>{asset.error}</Alert>}

      {asset.data && (
        <>
          <PageHeader
            title={asset.data.name}
            subtitle={
              asset.data.code
                ? `Código ${asset.data.code}`
                : "Sin código asignado"
            }
            actions={
              canManage && asset.data.status === "disponible" ? (
                <Button
                  variant="secondary"
                  onClick={() => setIsMaintenanceOpen(true)}
                >
                  <Icon name="tool" size={16} /> Enviar a mantenimiento
                </Button>
              ) : null
            }
          />

          <div className="grid-2">
            <Card title="Datos del activo">
              <dl className="definition-list">
                <dt>Tipo</dt>
                <dd>{ASSET_TYPE_LABEL[asset.data.asset_type]}</dd>
                <dt>Estado</dt>
                <dd>
                  <Badge tone={ASSET_STATUS[asset.data.status].tone}>
                    {ASSET_STATUS[asset.data.status].label}
                  </Badge>
                </dd>
                <dt>Descripción</dt>
                <dd>{asset.data.description ?? "—"}</dd>
              </dl>
            </Card>

            <Card title="Responsable actual">
              {holder.isLoading && <Skeleton height="72px" />}
              {holder.error && <Alert>{holder.error}</Alert>}
              {!holder.isLoading && !holder.error && holder.data && (
                <dl className="definition-list">
                  <dt>Responsable</dt>
                  <dd>{holder.data.responsible_name}</dd>
                  <dt>Desde</dt>
                  <dd>{formatDate(holder.data.loan_date)}</dd>
                  <dt>Devolución</dt>
                  <dd
                    className={
                      isOverdue(
                        holder.data.expected_return_date,
                        holder.data.status,
                      )
                        ? "text-danger"
                        : undefined
                    }
                  >
                    {formatDate(holder.data.expected_return_date)}
                  </dd>
                  <dt>Entregado por</dt>
                  <dd>{holder.data.registered_by_name ?? "—"}</dd>
                </dl>
              )}
              {!holder.isLoading &&
                !holder.error &&
                !holder.data &&
                openMaintenance && (
                  <p>
                    En mantenimiento, asignado a{" "}
                    <strong>{openMaintenance.assigned_to}</strong> desde el{" "}
                    {formatDate(openMaintenance.started_at)}.
                  </p>
                )}
              {!holder.isLoading &&
                !holder.error &&
                !holder.data &&
                !openMaintenance && (
                  <p className="muted">
                    Sin préstamo abierto: el activo está en el almacén.
                  </p>
                )}
            </Card>
          </div>

          <Card title="Línea de tiempo">
            {history.isLoading && <SkeletonTable rows={3} columns={1} />}
            {history.error && <Alert>{history.error}</Alert>}
            {history.data && <Timeline items={toTimelineItems(history.data)} />}
          </Card>

          <Card title="Préstamos del activo">
            {loans.isLoading && <SkeletonTable rows={3} columns={5} />}
            {loans.error && <Alert>{loans.error}</Alert>}
            {!loans.isLoading && !loans.error && (
              <Table<Loan>
                columns={loanColumns}
                data={loans.data ?? []}
                keyExtractor={(loan) => loan.id}
                emptyMessage="Este activo aún no ha sido prestado"
              />
            )}
          </Card>

          <Card title="Mantenimientos">
            {maintenances.isLoading && <SkeletonTable rows={2} columns={5} />}
            {maintenances.error && <Alert>{maintenances.error}</Alert>}
            {!maintenances.isLoading && !maintenances.error && (
              <Table<MaintenanceRecord>
                columns={maintenanceColumns}
                data={maintenances.data ?? []}
                keyExtractor={(item) => item.id}
                emptyMessage="Sin mantenimientos registrados"
              />
            )}
          </Card>

          <StartMaintenanceModal
            isOpen={isMaintenanceOpen}
            onClose={() => setIsMaintenanceOpen(false)}
            onCreated={refreshAll}
            assets={[asset.data]}
            defaultAssetId={asset.data.id}
          />
        </>
      )}
    </div>
  );
}

export default AssetDetail;
