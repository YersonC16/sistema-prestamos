import { useState, useCallback } from "react";
import Card from "@/components/common/Card";
import Button from "@/components/common/Button";
import Input from "@/components/common/Input";
import Modal from "@/components/common/Modal";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import { SkeletonTable } from "@/components/common/Skeleton";
import { useFetch } from "@/hooks/useFetch";
import { loanService } from "@/services/loanService";
import { assetService } from "@/services/assetService";
import type { Loan } from "@/types/loan";
import type { Asset } from "@/types/asset";
import "./Loans.css";

const STATUS_LABELS: Record<string, string> = {
  activo: "Activo",
  devuelto: "Devuelto",
  atrasado: "Atrasado",
};

function Loans() {
  const fetchLoans = useCallback(() => loanService.getAll(), []);
  const {
    data: loans,
    isLoading,
    error,
    refetch,
  } = useFetch<Loan[]>(fetchLoans);

  const fetchAvailable = useCallback(() => assetService.getAvailable(), []);
  const { data: availableAssets, refetch: refetchAssets } =
    useFetch<Asset[]>(fetchAvailable);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [assetId, setAssetId] = useState<number | "">("");
  const [responsibleName, setResponsibleName] = useState("");
  const [expectedReturnDate, setExpectedReturnDate] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [formError, setFormError] = useState("");

  const columns: TableColumn<Loan>[] = [
    { key: "asset_id", label: "Activo (ID)" },
    { key: "responsible_name", label: "Responsable" },
    {
      key: "loan_date",
      label: "Fecha préstamo",
      render: (row) => new Date(row.loan_date).toLocaleDateString(),
    },
    {
      key: "expected_return_date",
      label: "Devolución prevista",
      render: (row) => new Date(row.expected_return_date).toLocaleDateString(),
    },
    {
      key: "status",
      label: "Estado",
      render: (row) => STATUS_LABELS[row.status] ?? row.status,
    },
    {
      key: "id",
      label: "Acción",
      render: (row) =>
        row.status === "activo" ? (
          <Button variant="secondary" onClick={() => handleReturn(row.id)}>
            Marcar devuelto
          </Button>
        ) : (
          "—"
        ),
    },
  ];

  const handleCreate = async () => {
    if (!assetId || !responsibleName.trim() || !expectedReturnDate) {
      setFormError("Todos los campos son obligatorios");
      return;
    }
    setIsSaving(true);
    setFormError("");
    try {
      await loanService.create({
        asset_id: Number(assetId),
        responsible_name: responsibleName,
        loan_date: new Date().toISOString(),
        expected_return_date: new Date(expectedReturnDate).toISOString(),
      });
      setAssetId("");
      setResponsibleName("");
      setExpectedReturnDate("");
      setIsModalOpen(false);
      refetch();
      refetchAssets();
    } catch {
      setFormError("No se pudo registrar el préstamo. Verifica los datos.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleReturn = async (loanId: number) => {
    await loanService.returnLoan(loanId);
    refetch();
    refetchAssets();
  };

  return (
    <div className="loans-page">
      <div className="loans-header">
        <h2>Préstamos</h2>
        <Button onClick={() => setIsModalOpen(true)}>+ Nuevo préstamo</Button>
      </div>

      <Card>
        {isLoading && <SkeletonTable rows={4} columns={6} />}
        {error && <p className="loans-error">{error}</p>}
        {!isLoading && !error && (
          <Table<Loan>
            columns={columns}
            data={loans ?? []}
            keyExtractor={(row) => row.id}
          />
        )}
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Registrar nuevo préstamo"
      >
        <div className="loans-form">
          <div className="input-group">
            <label className="input-label">Activo disponible</label>
            <select
              className="input-field"
              value={assetId}
              onChange={(e) =>
                setAssetId(e.target.value ? Number(e.target.value) : "")
              }
            >
              <option value="">Selecciona un activo</option>
              {(availableAssets ?? []).map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name} (#{asset.id})
                </option>
              ))}
            </select>
          </div>

          <Input
            label="Responsable"
            value={responsibleName}
            onChange={(e) => setResponsibleName(e.target.value)}
            placeholder="Nombre de quien recibe"
          />

          <Input
            label="Fecha prevista de devolución"
            type="date"
            value={expectedReturnDate}
            onChange={(e) => setExpectedReturnDate(e.target.value)}
          />

          {formError && <p className="loans-error">{formError}</p>}

          <Button onClick={handleCreate} isLoading={isSaving}>
            Registrar préstamo
          </Button>
        </div>
      </Modal>
    </div>
  );
}

export default Loans;
