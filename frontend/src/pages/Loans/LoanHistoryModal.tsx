import { useCallback } from "react";
import Alert from "@/components/common/Alert";
import Modal from "@/components/common/Modal";
import { SkeletonTable } from "@/components/common/Skeleton";
import Timeline from "@/components/common/Timeline";
import { useFetch } from "@/hooks/useFetch";
import { loanService } from "@/services/loanService";
import type { Loan, LoanHistoryEntry } from "@/types/loan";
import { toTimelineItems } from "@/utils/timeline";

interface LoanHistoryModalProps {
  loan: Loan;
  onClose: () => void;
}

function LoanHistoryModal({ loan, onClose }: LoanHistoryModalProps) {
  const fetchHistory = useCallback(
    () => loanService.getHistory(loan.id),
    [loan.id],
  );
  const { data, isLoading, error } = useFetch<LoanHistoryEntry[]>(fetchHistory);

  return (
    <Modal
      isOpen
      onClose={onClose}
      title={`Historial del préstamo #${loan.id}`}
    >
      <div className="form-stack">
        <dl className="definition-list">
          <dt>Activo</dt>
          <dd>{loan.asset_name ?? `#${loan.asset_id}`}</dd>
          <dt>Responsable</dt>
          <dd>{loan.responsible_name}</dd>
          {loan.responsible_document && (
            <>
              <dt>Documento</dt>
              <dd>{loan.responsible_document}</dd>
            </>
          )}
          <dt>Entregado por</dt>
          <dd>{loan.registered_by_name ?? "—"}</dd>
          {loan.returned_by_name && (
            <>
              <dt>Recibido por</dt>
              <dd>{loan.returned_by_name}</dd>
            </>
          )}
          {loan.return_condition === "con_novedad" && (
            <>
              <dt>Novedad</dt>
              <dd>{loan.return_notes}</dd>
            </>
          )}
          {loan.notes && (
            <>
              <dt>Notas</dt>
              <dd>{loan.notes}</dd>
            </>
          )}
        </dl>

        {isLoading && <SkeletonTable rows={3} columns={1} />}
        {error && <Alert>{error}</Alert>}
        {data && <Timeline items={toTimelineItems(data)} />}
      </div>
    </Modal>
  );
}

export default LoanHistoryModal;
