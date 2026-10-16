import { useCallback } from "react";
import { Link } from "react-router-dom";
import Alert from "@/components/common/Alert";
import Card from "@/components/common/Card";
import Icon from "@/components/common/Icon";
import PageHeader from "@/components/common/PageHeader";
import { Skeleton, SkeletonTable } from "@/components/common/Skeleton";
import StatCard from "@/components/common/StatCard";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import Timeline from "@/components/common/Timeline";
import { useAuth } from "@/hooks/useAuth";
import { useFetch } from "@/hooks/useFetch";
import { assetService } from "@/services/assetService";
import { loanService } from "@/services/loanService";
import type { AssetSummary } from "@/types/asset";
import type { Loan, LoanHistoryEntry, LoanSummary } from "@/types/loan";
import { firstName, formatDate } from "@/utils/format";
import { ROLE_LABEL } from "@/utils/labels";
import { toTimelineItems } from "@/utils/timeline";
import { lazy, Suspense } from "react";

const AssetStatusChart = lazy(() => import("./AssetStatusChart"));
const LoanStatusChart = lazy(() => import("./LoanStatusChart"));
import "./Dashboard.css";

const OVERDUE_LIMIT = 5;
const MOVEMENTS_LIMIT = 5;

const overdueColumns: TableColumn<Loan>[] = [
  {
    key: "asset",
    label: "Activo",
    render: (loan) => loan.asset_name ?? `#${loan.asset_id}`,
  },
  { key: "responsible_name", label: "Responsable" },
  {
    key: "expected_return_date",
    label: "Debía devolver",
    render: (loan) => (
      <span className="text-danger">
        {formatDate(loan.expected_return_date)}
      </span>
    ),
  },
];

function Dashboard() {
  const { user } = useAuth();
  const canSeeMovements =
    user?.role === "administrador" || user?.role === "almacenista";

  const fetchAssetSummary = useCallback(() => assetService.getSummary(), []);
  const fetchLoanSummary = useCallback(() => loanService.getSummary(), []);
  const fetchOverdue = useCallback(
    () => loanService.getAll({ status: "atrasado" }),
    [],
  );
  const fetchMovements = useCallback(
    () =>
      canSeeMovements
        ? loanService.getMovements(MOVEMENTS_LIMIT)
        : Promise.resolve([] as LoanHistoryEntry[]),
    [canSeeMovements],
  );

  const assets = useFetch<AssetSummary>(fetchAssetSummary);
  const loans = useFetch<LoanSummary>(fetchLoanSummary);
  const overdue = useFetch<Loan[]>(fetchOverdue);
  const movements = useFetch<LoanHistoryEntry[]>(fetchMovements);

  const statsError = assets.error ?? loans.error;
  const overdueList = (overdue.data ?? []).slice(0, OVERDUE_LIMIT);
  const hasMoreOverdue = (overdue.data?.length ?? 0) > OVERDUE_LIMIT;

  return (
    <div className="page dashboard-fade-in">
      <PageHeader
        title={user ? `Hola, ${firstName(user.full_name)}` : "Panel"}
        subtitle="Resumen de la sede de Concreto"
      />

      {statsError && <Alert>{statsError}</Alert>}

      {assets.data && loans.data ? (
        <div className="stats-grid">
          <StatCard
            label="Activos registrados"
            value={assets.data.total}
            icon="package"
            tone="info"
          />
          <StatCard
            label="Disponibles"
            value={assets.data.disponible}
            icon="package"
            tone="success"
          />
          <StatCard
            label="Prestados"
            value={assets.data.prestado}
            icon="repeat"
            tone="info"
          />
          <StatCard
            label="En mantenimiento"
            value={assets.data.mantenimiento}
            icon="tool"
            tone="warning"
          />
          <StatCard
            label="Préstamos activos"
            value={loans.data.activo}
            icon="clock"
            tone="neutral"
          />
          <StatCard
            label="Préstamos atrasados"
            value={loans.data.atrasado}
            icon="clock"
            tone="danger"
          />
        </div>
      ) : (
        !statsError && (
          <div className="stats-grid">
            {Array.from({ length: 6 }).map((_, index) => (
              <Skeleton key={index} height="76px" borderRadius="14px" />
            ))}
          </div>
        )
      )}

      <div className="grid-2">
        <Card title="Estado del inventario">
          {assets.isLoading && <Skeleton height="220px" borderRadius="14px" />}
          {assets.error && <Alert>{assets.error}</Alert>}
          {assets.data && (
            <Suspense
              fallback={<Skeleton height="220px" borderRadius="14px" />}
            >
              <AssetStatusChart summary={assets.data} />
            </Suspense>
          )}
        </Card>

        <Card title="Préstamos por estado">
          {loans.isLoading && <Skeleton height="220px" borderRadius="14px" />}
          {loans.error && <Alert>{loans.error}</Alert>}
          {loans.data && (
            <Suspense
              fallback={<Skeleton height="220px" borderRadius="14px" />}
            >
              <LoanStatusChart summary={loans.data} />
            </Suspense>
          )}
        </Card>
      </div>

      <div className="grid-2">
        <Card title="Préstamos atrasados">
          {overdue.isLoading && <SkeletonTable rows={3} columns={3} />}
          {overdue.error && <Alert>{overdue.error}</Alert>}
          {!overdue.isLoading && !overdue.error && (
            <>
              <Table<Loan>
                columns={overdueColumns}
                data={overdueList}
                keyExtractor={(loan) => loan.id}
                emptyMessage="No hay préstamos atrasados"
              />
              {hasMoreOverdue && (
                <Link
                  to="/prestamos?status=atrasado"
                  className="dashboard-see-all"
                >
                  Ver todos los atrasados <Icon name="arrowRight" size={14} />
                </Link>
              )}
            </>
          )}
        </Card>

        {canSeeMovements ? (
          <Card title="Últimos movimientos">
            {movements.isLoading && <SkeletonTable rows={4} columns={1} />}
            {movements.error && <Alert>{movements.error}</Alert>}
            {movements.data && (
              <>
                <Timeline items={toTimelineItems(movements.data)} />
                <Link to="/trazabilidad" className="dashboard-see-all">
                  Ver toda la trazabilidad <Icon name="arrowRight" size={14} />
                </Link>
              </>
            )}
          </Card>
        ) : (
          <Card title="Tu acceso">
            <p>
              Tu rol es <strong>{user ? ROLE_LABEL[user.role] : ""}</strong>.
              Puedes consultar el inventario, los préstamos y el mantenimiento.
              El registro de préstamos y devoluciones lo realiza el almacenista.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
