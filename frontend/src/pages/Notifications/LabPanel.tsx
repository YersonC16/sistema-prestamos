import { useState, type FormEvent } from "react";
import Alert from "@/components/common/Alert";
import Badge from "@/components/common/Badge";
import Button from "@/components/common/Button";
import Card from "@/components/common/Card";
import Input from "@/components/common/Input";
import Select from "@/components/common/Select";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import { notificationService } from "@/services/notificationService";
import type { LabChannel, LabMode, LabRunResult } from "@/types/notification";
import { getErrorMessage } from "@/utils/errors";
import { EVENT_OPTIONS, notificationStatus } from "@/utils/labels";

const MODE_INFO: Record<LabMode, { title: string; idea: string; add: string }> =
  {
    sin_patron: {
      title: "Sin patrones",
      idea: "Quien detecta el evento llama directo a una función que lo hace todo, y el canal es un if/else.",
      add: "Agregar otra reacción o un canal nuevo obliga a editar esa función y a quien la llama.",
    },
    observer: {
      title: "Solo Observer",
      idea: "Quien detecta el evento solo avisa. Los observadores se enganchan con attach().",
      add: "Agregar otra reacción es agregar un observador. El canal sigue siendo un if/else dentro del observador.",
    },
    strategy: {
      title: "Solo Strategy",
      idea: "El canal es una clase intercambiable, pero quien detecta el evento sigue llamando directo a la función.",
      add: "Agregar WhatsApp es una clase nueva. Agregar otra reacción sigue obligando a editar la función.",
    },
    observer_strategy: {
      title: "Observer + Strategy",
      idea: "El observador decide a quién y cuándo. La estrategia decide cómo enviar.",
      add: "Otra reacción es un observador y WhatsApp es una clase. Ninguno toca al otro.",
    },
  };

interface ComparisonRow {
  variant: string;
  decouples: boolean;
  swappable: boolean;
}

const COMPARISON: ComparisonRow[] = [
  { variant: "Sin patrones", decouples: false, swappable: false },
  { variant: "Solo Observer", decouples: true, swappable: false },
  { variant: "Solo Strategy", decouples: false, swappable: true },
  { variant: "Observer + Strategy", decouples: true, swappable: true },
];

const yesNo = (value: boolean) => (
  <Badge tone={value ? "success" : "neutral"}>{value ? "Sí" : "No"}</Badge>
);

const COMPARISON_COLUMNS: TableColumn<ComparisonRow>[] = [
  {
    key: "variant",
    label: "Variante",
    render: (row) => <span className="cell-strong">{row.variant}</span>,
  },
  {
    key: "decouples",
    label: "Quien detecta el evento no conoce a quien reacciona",
    render: (row) => yesNo(row.decouples),
  },
  {
    key: "swappable",
    label: "El canal de envío es intercambiable",
    render: (row) => yesNo(row.swappable),
  },
];

const SITE_PATTERN = /^[a-z0-9_-]+$/i;

function LabPanel() {
  const [eventType, setEventType] = useState(EVENT_OPTIONS[0].value);
  const [site, setSite] = useState("concreto");
  const [channel, setChannel] = useState<LabChannel>("simulado");
  const [result, setResult] = useState<LabRunResult | null>(null);
  const [error, setError] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  const handleRun = async (event: FormEvent) => {
    event.preventDefault();
    if (!SITE_PATTERN.test(site.trim()))
      return setError(
        "La sede solo puede tener letras, números, guion y guion bajo",
      );

    setIsRunning(true);
    setError("");
    try {
      setResult(
        await notificationService.runLab({
          event_type: eventType,
          site: site.trim().toLowerCase(),
          channel,
        }),
      );
    } catch (err) {
      setError(getErrorMessage(err, "No se pudo ejecutar la prueba"));
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <>
      <Card title="Qué resuelve cada patrón">
        <Table<ComparisonRow>
          columns={COMPARISON_COLUMNS}
          data={COMPARISON}
          keyExtractor={(row) => row.variant}
        />
      </Card>

      <Card title="Simular un evento">
        <form className="form-stack" onSubmit={handleRun}>
          <div className="toolbar">
            <Select
              label="Evento"
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
            >
              {EVENT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
            <Input
              label="Sede"
              value={site}
              onChange={(e) => setSite(e.target.value)}
            />
            <Select
              label="Canal"
              value={channel}
              onChange={(e) => setChannel(e.target.value as LabChannel)}
            >
              <option value="simulado">Simulado (no envía nada)</option>
              <option value="correo">Correo (usa el SMTP configurado)</option>
            </Select>
          </div>
          {channel === "correo" && (
            <Alert tone="info">
              Cada variante envía su propio correo, con el asunto marcado como
              [Prueba: ...]. Con Mailpit llegan 4 en http://localhost:8025.
            </Alert>
          )}
          {error && <Alert>{error}</Alert>}
          <div className="form-actions">
            <Button type="submit" isLoading={isRunning}>
              Probar los 4 enfoques
            </Button>
          </div>
        </form>
      </Card>

      {result && (
        <div className="grid-2">
          {result.reports.map((report) => {
            const info = MODE_INFO[report.mode];
            return (
              <Card key={report.mode}>
                <div className="lab-card-title">
                  <h3>{info.title}</h3>
                  <Badge tone="neutral">{report.elapsed_ms} ms</Badge>
                </div>
                <p className="lab-note">{info.idea}</p>

                <ol className="lab-steps">
                  {report.steps.map((step, index) => (
                    <li key={index}>{step}</li>
                  ))}
                </ol>

                {report.deliveries.length === 0 ? (
                  <p className="muted">
                    Sin entregas: no hay un jefe de planta activo en la sede{" "}
                    {result.site}.
                  </p>
                ) : (
                  report.deliveries.map((delivery, index) => (
                    <div className="lab-delivery" key={index}>
                      <span>{delivery.recipient}</span>
                      <Badge tone={notificationStatus(delivery.status).tone}>
                        {notificationStatus(delivery.status).label}
                      </Badge>
                    </div>
                  ))
                )}

                <p
                  className="lab-note"
                  style={{ marginTop: "var(--spacing-md)" }}
                >
                  {info.add}
                </p>
              </Card>
            );
          })}
        </div>
      )}
    </>
  );
}

export default LabPanel;
