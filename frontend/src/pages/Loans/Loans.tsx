import { useCallback, useMemo, useState, type FormEvent } from "react";
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
import Textarea from "@/components/common/Textarea";
import { useAuth } from "@/hooks/useAuth";
import { useFetch } from "@/hooks/useFetch";
import { assetService } from "@/services/assetService";
import { loanService } from "@/services/loanService";
import type { Asset } from "@/types/asset";
import type { Loan, LoanStatus, ReturnCondition } from "@/types/loan";
import { getErrorMessage } from "@/utils/errors";
import {
  endOfDayIso,
  formatDate,
  isOverdue,
  todayInputValue,
} from "@/utils/format";
import { LOAN_STATUS } from "@/utils/labels";
import LoanHistoryModal from "./LoanHistoryModal";

function Loans() {
  const { user } = useAuth();
  const canManage =
    user?.role === "administrador" || user?.role === "almacenista";

  const [statusFilter, setStatusFilter] = useState<LoanStatus | "">("");
  const [search, setSearch] = useState("");

  const fetchLoans = useCallback(
    () => loanService.getAll({ status: statusFilter || undefined }),
    [statusFilter],
  );
  const {
    data: loans,
    isLoading,
    error,
    refetch,
  } = useFetch<Loan[]>(fetchLoans);

  const fetchAvailable = useCallback(() => assetService.getAvailable(), []);
  const { data: availableAssets, refetch: refetchAssets } =
    useFetch<Asset[]>(fetchAvailable);

  // Registrar préstamo
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [assetId, setAssetId] = useState("");
  const [responsible, setResponsible] = useState("");
  const [expectedDate, setExpectedDate] = useState("");
  const [notes, setNotes] = useState("");
  const [createError, setCreateError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  // Registrar devolución
  const [returning, setReturning] = useState<Loan | null>(null);
  const [condition, setCondition] = useState<ReturnCondition>("bueno");
  const [returnNotes, setReturnNotes] = useState("");
  const [returnError, setReturnError] = useState("");
  const [isReturning, setIsReturning] = useState(false);

  // Historial
  const [historyLoan, setHistoryLoan] = useState<Loan | null>(null);

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    return (loans ?? []).filter(
      (loan) =>
        !term ||
        loan.responsible_name.toLowerCase().includes(term) ||
        (loan.asset_name ?? "").toLowerCase().includes(term),
    );
  }, [loans, search]);

  const closeCreate = () => {
    setIsCreateOpen(false);
    setAssetId("");
    setResponsible("");
    setExpectedDate("");
    setNotes("");
    setCreateError("");
  };

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (!assetId) return setCreateError("Selecciona el activo");
    if (responsible.trim().length < 2)
      return setCreateError("Indica el nombre de quien recibe el activo");
    if (!expectedDate)
      return setCreateError("Indica la fecha prevista de devolución");
    if (expectedDate < todayInputValue())
      return setCreateError(
        "La fecha de devolución no puede ser anterior a hoy",
      );

    setIsSaving(true);
    setCreateError("");
    try {
      await loanService.create({
        asset_id: Number(assetId),
        responsible_name: responsible.trim(),
        expected_return_date: endOfDayIso(expectedDate),
        notes: notes.trim() || undefined,
      });
      closeCreate();
      refetch();
      refetchAssets();
    } catch (err) {
      setCreateError(getErrorMessage(err, "No se pudo registrar el préstamo"));
    } finally {
      setIsSaving(false);
    }
  };

  const closeReturn = () => {
    setReturning(null);
    setCondition("bueno");
    setReturnNotes("");
    setReturnError("");
  };

  const handleReturn = async (event: FormEvent) => {
    event.preventDefault();
    if (!returning) return;
    if (condition === "con_novedad" && !returnNotes.trim()) {
      return setReturnError("Describe la novedad encontrada en el activo");
    }

    setIsReturning(true);
    setReturnError("");
    try {
      await loanService.returnLoan(returning.id, {
        condition,
        notes: condition === "con_novedad" ? returnNotes.trim() : undefined,
      });
      closeReturn();
      refetch();
      refetchAssets();
    } catch (err) {
      setReturnError(
        getErrorMessage(err, "No se pudo registrar la devolución"),
      );
    } finally {
      setIsReturning(false);
    }
  };

  const columns: TableColumn<Loan>[] = [
    {
      key: "asset",
      label: "Activo",
      render: (loan) => (
        <span className="cell-strong">
          {loan.asset_name ?? `#${loan.asset_id}`}
        </span>
      ),
    },
    { key: "responsible_name", label: "Responsable" },
    {
      key: "loan_date",
      label: "Prestado",
      render: (loan) => formatDate(loan.loan_date),
    },
    {
      key: "expected_return_date",
      label: "Devolución prevista",
      render: (loan) => (
        <span
          className={
            isOverdue(loan.expected_return_date, loan.status)
              ? "text-danger"
              : undefined
          }
        >
          {formatDate(loan.expected_return_date)}
        </span>
      ),
    },
    {
      key: "status",
      label: "Estado",
      render: (loan) => {
        const effective: LoanStatus = isOverdue(
          loan.expected_return_date,
          loan.status,
        )
          ? "atrasado"
          : loan.status;
        return (
          <Badge tone={LOAN_STATUS[effective].tone}>
            {LOAN_STATUS[effective].label}
          </Badge>
        );
      },
    },
    { key: "registered_by_name", label: "Registró" },
    {
      key: "actions",
      label: "Acciones",
      render: (loan) => (
        <div className="cell-actions">
          {canManage && loan.status !== "devuelto" && (
            <Button
              size="sm"
              variant="secondary"
              onClick={() => setReturning(loan)}
            >
              Devolver
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setHistoryLoan(loan)}
          >
            Historial
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="page">
      <PageHeader
        title="Préstamos"
        subtitle="Entrega y recepción de equipos y herramientas."
        actions={
          canManage ? (
            <Button onClick={() => setIsCreateOpen(true)}>
              <Icon name="plus" size={16} /> Nuevo préstamo
            </Button>
          ) : null
        }
      />

      <div className="toolbar">
        <Input
          label="Buscar"
          placeholder="Responsable o activo"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select
          label="Estado"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as LoanStatus | "")}
        >
          <option value="">Todos</option>
          <option value="activo">Activos</option>
          <option value="atrasado">Atrasados</option>
          <option value="devuelto">Devueltos</option>
        </Select>
      </div>

      <Card>
        {isLoading && <SkeletonTable rows={5} columns={6} />}
        {error && <Alert>{error}</Alert>}
        {!isLoading && !error && (
          <Table<Loan>
            columns={columns}
            data={filtered}
            keyExtractor={(loan) => loan.id}
            emptyMessage="No hay préstamos para mostrar"
          />
        )}
      </Card>

      <Modal
        isOpen={isCreateOpen}
        onClose={closeCreate}
        title="Registrar préstamo"
      >
        <form className="form-stack" onSubmit={handleCreate}>
          {(availableAssets ?? []).length === 0 && (
            <Alert tone="info">
              No hay activos disponibles en este momento.
            </Alert>
          )}
          <Select
            label="Activo disponible"
            value={assetId}
            onChange={(e) => setAssetId(e.target.value)}
            required
          >
            <option value="">Selecciona un activo</option>
            {(availableAssets ?? []).map((asset) => (
              <option key={asset.id} value={asset.id}>
                {asset.name}
                {asset.code ? ` · ${asset.code}` : ""}
              </option>
            ))}
          </Select>
          <Input
            label="Responsable que recibe"
            value={responsible}
            onChange={(e) => setResponsible(e.target.value)}
            placeholder="Nombre de quien recibe"
            required
          />
          <Input
            label="Fecha prevista de devolución"
            type="date"
            min={todayInputValue()}
            value={expectedDate}
            onChange={(e) => setExpectedDate(e.target.value)}
            required
          />
          <Textarea
            label="Notas (opcional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Obra, uso previsto, accesorios entregados..."
          />
          {createError && <Alert>{createError}</Alert>}
          <div className="form-actions">
            <Button variant="secondary" onClick={closeCreate}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSaving}>
              Registrar préstamo
            </Button>
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={returning !== null}
        onClose={closeReturn}
        title="Registrar devolución"
      >
        {returning && (
          <form className="form-stack" onSubmit={handleReturn}>
            <p>
              <strong>
                {returning.asset_name ?? `#${returning.asset_id}`}
              </strong>{" "}
              entregado a <strong>{returning.responsible_name}</strong>.
            </p>
            <Select
              label="Estado en que se recibe"
              value={condition}
              onChange={(e) => setCondition(e.target.value as ReturnCondition)}
            >
              <option value="bueno">Buen estado</option>
              <option value="con_novedad">Con novedad</option>
            </Select>
            {condition === "con_novedad" && (
              <>
                <Textarea
                  label="Describe la novedad"
                  value={returnNotes}
                  onChange={(e) => setReturnNotes(e.target.value)}
                  placeholder="Daño, pieza faltante, desgaste..."
                />
                <Alert tone="info">
                  Con novedad, el activo pasará a mantenimiento hasta que se
                  revise.
                </Alert>
              </>
            )}
            {returnError && <Alert>{returnError}</Alert>}
            <div className="form-actions">
              <Button variant="secondary" onClick={closeReturn}>
                Cancelar
              </Button>
              <Button type="submit" isLoading={isReturning}>
                Confirmar devolución
              </Button>
            </div>
          </form>
        )}
      </Modal>

      {historyLoan && (
        <LoanHistoryModal
          loan={historyLoan}
          onClose={() => setHistoryLoan(null)}
        />
      )}
    </div>
  );
}

export default Loans;
