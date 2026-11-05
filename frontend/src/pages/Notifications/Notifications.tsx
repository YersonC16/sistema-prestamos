import { useCallback, useState } from "react";
import Alert from "@/components/common/Alert";
import Badge from "@/components/common/Badge";
import Button from "@/components/common/Button";
import Card from "@/components/common/Card";
import PageHeader from "@/components/common/PageHeader";
import Pagination from "@/components/common/Pagination";
import Select from "@/components/common/Select";
import { SkeletonTable } from "@/components/common/Skeleton";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import { useAuth } from "@/hooks/useAuth";
import { useFetch } from "@/hooks/useFetch";
import { usePagination } from "@/hooks/usePagination";
import { notificationService } from "@/services/notificationService";
import type { NotificationEntry } from "@/types/notification";
import { formatDateTime } from "@/utils/format";
import { actionMeta, notificationStatus } from "@/utils/labels";
import LabPanel from "./LabPanel";

type Tab = "history" | "lab";

const columns: TableColumn<NotificationEntry>[] = [
  {
    key: "created_at",
    label: "Fecha",
    render: (n) => formatDateTime(n.created_at),
  },
  {
    key: "event_type",
    label: "Evento",
    render: (n) => (
      <Badge tone={actionMeta(n.event_type).tone}>
        {actionMeta(n.event_type).label}
      </Badge>
    ),
  },
  {
    key: "site",
    label: "Sede",
    render: (n) => n.site.charAt(0).toUpperCase() + n.site.slice(1),
  },
  { key: "asset_name", label: "Activo" },
  {
    key: "recipient",
    label: "Destinatario",
    render: (n) =>
      n.recipient_email ? (
        <>
          {n.recipient_name}
          <div className="muted" style={{ fontSize: "12px" }}>
            {n.recipient_email}
          </div>
        </>
      ) : (
        "—"
      ),
  },
  {
    key: "status",
    label: "Estado",
    render: (n) => (
      <Badge tone={notificationStatus(n.status).tone}>
        {notificationStatus(n.status).label}
      </Badge>
    ),
  },
  { key: "error", label: "Detalle" },
];

function Notifications() {
  const { user } = useAuth();
  const isAdmin = user?.role === "administrador";

  const [tab, setTab] = useState<Tab>("history");
  const [status, setStatus] = useState("");

  const fetchLog = useCallback(
    () => notificationService.getAll(status || undefined, 100),
    [status],
  );
  const { data, isLoading, error, refetch } =
    useFetch<NotificationEntry[]>(fetchLog);
  const { page, setPage, totalPages, pageItems, total } = usePagination(
    data ?? [],
    10,
  );

  return (
    <div className="page">
      <PageHeader
        title="Notificaciones"
        subtitle="Avisos enviados al jefe de planta cuando algo cambia en su sede."
        actions={
          tab === "history" ? (
            <Button variant="secondary" onClick={refetch}>
              Actualizar
            </Button>
          ) : null
        }
      />

      <div className="tabs" role="tablist">
        <button
          role="tab"
          aria-selected={tab === "history"}
          className={`tab ${tab === "history" ? "tab-active" : ""}`}
          onClick={() => setTab("history")}
        >
          Historial de envíos
        </button>
        {isAdmin && (
          <button
            role="tab"
            aria-selected={tab === "lab"}
            className={`tab ${tab === "lab" ? "tab-active" : ""}`}
            onClick={() => setTab("lab")}
          >
            Pruebas de patrones
          </button>
        )}
      </div>

      {tab === "history" && (
        <>
          <div className="toolbar">
            <Select
              label="Estado"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="">Todos</option>
              <option value="enviado">Enviado</option>
              <option value="simulado">Simulado</option>
              <option value="fallido">Fallido</option>
              <option value="sin_destinatario">Sin destinatario</option>
            </Select>
          </div>

          {isAdmin && (
            <Alert tone="info">
              Con Mailpit puedes ver los correos que llegan en
              http://localhost:8025. Si el estado es "Sin destinatario", falta
              un usuario con rol Jefe de planta activo en esa sede.
            </Alert>
          )}

          <Card>
            {isLoading && <SkeletonTable rows={5} columns={7} />}
            {error && <Alert>{error}</Alert>}
            {!isLoading && !error && (
              <>
                <Table<NotificationEntry>
                  columns={columns}
                  data={pageItems}
                  keyExtractor={(n) => n.id}
                  emptyMessage="Aún no hay notificaciones"
                />
                <Pagination
                  page={page}
                  totalPages={totalPages}
                  total={total}
                  pageSize={10}
                  onChange={setPage}
                />
              </>
            )}
          </Card>
        </>
      )}

      {tab === "lab" && isAdmin && <LabPanel />}
    </div>
  );
}

export default Notifications;
