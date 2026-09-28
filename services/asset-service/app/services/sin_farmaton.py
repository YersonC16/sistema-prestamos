from app.models.asset import Asset, AssetType, AssetStatus

##sin farmaton 


def create_asset(
    asset_type: AssetType,
    name: str,
    description: str | None = None
) -> Asset:
    """
    Crea directamente un activo.

    Este archivo NO utiliza el patrón Factory Method.
    El tipo de activo se recibe directamente como parámetro
    y se utiliza para construir el objeto Asset.
    """

    # Validar que el tipo de activo sea válido
    if asset_type not in (
        AssetType.EQUIPO,
        AssetType.HERRAMIENTA,
        AssetType.OTRO,
    ):
        raise ValueError(
            f"Tipo de activo no soportado: {asset_type}"
        )

    # Validar el nombre
    if not name or not name.strip():
        raise ValueError(
            "El nombre del activo es obligatorio"
        )

    # Crear directamente el objeto Asset
    return Asset(
        name=name.strip(),
        description=description,
        asset_type=asset_type,
        status=AssetStatus.DISPONIBLE,
    )