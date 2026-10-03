import { useCallback, useState } from "react";
import Alert from "@/components/common/Alert";
import Badge from "@/components/common/Badge";
import Button from "@/components/common/Button";
import Card from "@/components/common/Card";
import Icon from "@/components/common/Icon";
import PageHeader from "@/components/common/PageHeader";
import Pagination from "@/components/common/Pagination";
import { SkeletonTable } from "@/components/common/Skeleton";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import { useFetch } from "@/hooks/useFetch";
import { usePagination } from "@/hooks/usePagination";
import { responsibleService } from "@/services/responsibleService";
import type { Responsible } from "@/types/responsible";
import { DOCUMENT_TYPE_LABEL } from "@/utils/labels";
import ResponsibleFormModal from "./ResponsibleFormModal";

function Responsibles() {
  const fetchAll = useCallback(() => responsibleService.getAll(), []);
  const { data, isLoading, error, refetch } = useFetch<Responsible[]>(fetchAll);

  const { page, setPage, totalPages, pageItems, total } = usePagination(
    data ?? [],
    10,
  );

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editing, setEditing] = useState<Responsible | null>(null);

  const columns: TableColumn<Responsible>[] = [
    {
      key: "full_name",
      label: "Nombre",
      render: (r) => <span className="cell-strong">{r.full_name}</span>,
    },
    {
      key: "document",
      label: "Documento",
      render: (r) =>
        `${DOCUMENT_TYPE_LABEL[r.document_type]} ${r.document_number}`,
    },
    { key: "phone", label: "Teléfono" },
    {
      key: "is_active",
      label: "Estado",
      render: (r) => (
        <Badge tone={r.is_active ? "success" : "neutral"}>
          {r.is_active ? "Activo" : "Desactivado"}
        </Badge>
      ),
    },
    {
      key: "actions",
      label: "Acción",
      render: (r) => (
        <Button size="sm" variant="secondary" onClick={() => setEditing(r)}>
          Editar
        </Button>
      ),
    },
  ];

  return (
    <div className="page">
      <PageHeader
        title="Responsables"
        subtitle="Personas a quienes se les puede asignar un préstamo. Pensado para integrarse más adelante con otros procesos del empleado (nómina, EPP, dotación)."
        actions={
          <Button onClick={() => setIsCreateOpen(true)}>
            <Icon name="plus" size={16} /> Nuevo responsable
          </Button>
        }
      />

      <Card>
        {isLoading && <SkeletonTable rows={4} columns={5} />}
        {error && <Alert>{error}</Alert>}
        {!isLoading && !error && (
          <>
            <Table<Responsible>
              columns={columns}
              data={pageItems}
              keyExtractor={(r) => r.id}
              emptyMessage="No hay responsables registrados"
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

      <ResponsibleFormModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSaved={refetch}
      />
      <ResponsibleFormModal
        isOpen={editing !== null}
        onClose={() => setEditing(null)}
        onSaved={refetch}
        responsible={editing}
      />
    </div>
  );
}

export default Responsibles;
