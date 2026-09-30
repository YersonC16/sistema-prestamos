import { useCallback, useState } from "react";
import Alert from "@/components/common/Alert";
import Badge from "@/components/common/Badge";
import Card from "@/components/common/Card";
import PageHeader from "@/components/common/PageHeader";
import Select from "@/components/common/Select";
import { SkeletonTable } from "@/components/common/Skeleton";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import { useAuth } from "@/hooks/useAuth";
import { useFetch } from "@/hooks/useFetch";
import { auditService } from "@/services/auditService";
import { loanService } from "@/services/loanService";
import type { AuditEntry } from "@/types/asset";
import type { LoanHistoryEntry } from "@/types/loan";
import { formatDateTime } from "@/utils/format";
import { actionMeta, roleText } from "@/utils/labels";

type Tab = "movements" | "audit";

const movementColumns: TableColumn<LoanHistoryEntry>[] = [
  {
    key: "created_at",
    label: "Fecha",
    render: (entry) => formatDateTime(entry.created_at),
  },
  {
    key: "action",
    label: "Acción",
    render: (entry) => (
      <Badge tone={actionMeta(entry.action).tone}>
        {actionMeta(entry.action).label}
      </Badge>
    ),
  },
  { key: "asset_id", label: "Activo", render: (entry) => `#${entry.asset_id}` },
  { key: "detail", label: "Detalle" },
  {
    key: "performed_by",
    label: "Realizado por",
    render: (entry) =>
      `${entry.performed_by}${entry.performed_by_role ? ` (${roleText(entry.performed_by_role)})` : ""}`,
  },
];

const auditColumns: TableColumn<AuditEntry>[] = [
  {
    key: "created_at",
    label: "Fecha",
    render: (entry) => formatDateTime(entry.created_at),
  },
  {
    key: "action",
    label: "Acción",
    render: (entry) => (
      <Badge tone={actionMeta(entry.action).tone}>
        {actionMeta(entry.action).label}
      </Badge>
    ),
  },
  {
    key: "entity",
    label: "Sobre",
    render: (entry) =>
      `${entry.entity_type === "asset" ? "Activo" : "Usuario"}${entry.entity_id ? ` #${entry.entity_id}` : ""}`,
  },
  { key: "detail", label: "Detalle" },
  {
    key: "performed_by",
    label: "Realizado por",
    render: (entry) =>
      `${entry.performed_by}${entry.performed_by_role ? ` (${roleText(entry.performed_by_role)})` : ""}`,
  },
];

function Traceability() {
  const { user } = useAuth();
  const isAdmin = user?.role === "administrador";

  const [tab, setTab] = useState<Tab>("movements");
  const [entityFilter, setEntityFilter] = useState("");

  const fetchMovements = useCallback(
    () =>
      tab === "movements"
        ? loanService.getMovements(100)
        : Promise.resolve([] as LoanHistoryEntry[]),
    [tab],
  );
  const fetchAudit = useCallback(
    () =>
      isAdmin && tab === "audit"
        ? auditService.getAll(entityFilter || undefined, 100)
        : Promise.resolve([] as AuditEntry[]),
    [isAdmin, tab, entityFilter],
  );

  const movements = useFetch<LoanHistoryEntry[]>(fetchMovements);
  const audit = useFetch<AuditEntry[]>(fetchAudit);

  return (
    <div className="page">
      <PageHeader
        title="Trazabilidad"
        subtitle="Quién hizo qué y cuándo. Los últimos 100 registros de cada vista."
      />

      <div className="tabs" role="tablist">
        <button
          role="tab"
          aria-selected={tab === "movements"}
          className={`tab ${tab === "movements" ? "tab-active" : ""}`}
          onClick={() => setTab("movements")}
        >
          Movimientos de préstamos
        </button>
        {isAdmin && (
          <button
            role="tab"
            aria-selected={tab === "audit"}
            className={`tab ${tab === "audit" ? "tab-active" : ""}`}
            onClick={() => setTab("audit")}
          >
            Auditoría del sistema
          </button>
        )}
      </div>

      {tab === "audit" && (
        <div className="toolbar">
          <Select
            label="Sobre"
            value={entityFilter}
            onChange={(e) => setEntityFilter(e.target.value)}
          >
            <option value="">Todo</option>
            <option value="asset">Activos</option>
            <option value="user">Usuarios y sesiones</option>
          </Select>
        </div>
      )}

      <Card>
        {tab === "movements" && (
          <>
            {movements.isLoading && <SkeletonTable rows={6} columns={5} />}
            {movements.error && <Alert>{movements.error}</Alert>}
            {!movements.isLoading && !movements.error && (
              <Table<LoanHistoryEntry>
                columns={movementColumns}
                data={movements.data ?? []}
                keyExtractor={(entry) => entry.id}
                emptyMessage="Aún no hay movimientos"
              />
            )}
          </>
        )}
        {tab === "audit" && (
          <>
            {audit.isLoading && <SkeletonTable rows={6} columns={5} />}
            {audit.error && <Alert>{audit.error}</Alert>}
            {!audit.isLoading && !audit.error && (
              <Table<AuditEntry>
                columns={auditColumns}
                data={audit.data ?? []}
                keyExtractor={(entry) => entry.id}
                emptyMessage="Sin registros de auditoría"
              />
            )}
          </>
        )}
      </Card>
    </div>
  );
}

export default Traceability;
