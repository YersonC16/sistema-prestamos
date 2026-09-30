import requests

from app.core.config import settings


class AssetServiceError(Exception):
    pass


class AssetServiceClient:
    """Consulta a asset-service reenviando el token del usuario."""

    def __init__(self, token: str | None, timeout: int = 5):
        self._headers = {"Authorization": f"Bearer {token}"}
        self._timeout = timeout

    def get_available_assets(self) -> list[dict]:
        try:
            response = requests.get(
                f"{settings.asset_service_url}/assets/available",
                headers=self._headers,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise AssetServiceError("No se pudo contactar al servicio de activos") from exc
        if response.status_code != 200:
            raise AssetServiceError("El servicio de activos rechazó la consulta")
        return response.json()