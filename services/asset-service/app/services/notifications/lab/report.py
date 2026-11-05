class LabReport:
    """Bitácora de una variante: qué pasos hizo y a quién entregó."""

    def __init__(self, mode: str):
        self.mode = mode
        self.steps: list[str] = []
        self.deliveries: list[dict] = []
        self.elapsed_ms = 0.0

    def step(self, text: str) -> None:
        self.steps.append(text)

    def delivery(self, recipient: str, channel: str, status: str, error: str | None = None) -> None:
        self.deliveries.append({"recipient": recipient, "channel": channel, "status": status, "error": error})

    def as_dict(self) -> dict:
        return {
            "mode": self.mode,
            "steps": self.steps,
            "deliveries": self.deliveries,
            "elapsed_ms": round(self.elapsed_ms, 2),
        }