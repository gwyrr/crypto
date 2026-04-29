# CONTROLADOR DE ACTIVOS
# Este modulo define las rutas de la API para gestionar el catalogo de activos (monedas).
# Actua como puente entre las peticiones HTTP y la logica de negocio en asset_service.

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.asset import AssetRead, AssetUpdate, CryptocurrencyCreate
from app.services import asset_service


# Definicion del router con prefijo /assets para organizar la API
router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(asset: CryptocurrencyCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo activo financiero disponible para transacciones.
    Requiere permisos de administrador (en una app real).
    """
    return asset_service.create_asset(db=db, asset=asset)


@router.get("/", response_model=list[AssetRead])
def list_assets(db: Session = Depends(get_db)):
    """
    Obtiene la lista completa de monedas registradas en el sistema.
    Util para llenar selectores en el frontend.
    """
    return asset_service.list_assets(db=db)


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """
    Consulta los detalles de una moneda especifica mediante su ID unico.
    """
    return asset_service.get_asset(db=db, asset_id=asset_id)


@router.put("/{asset_id}", response_model=AssetRead)
def update_asset(asset_id: int, asset: AssetUpdate, db: Session = Depends(get_db)):
    """
    Actualiza la informacion de una moneda (simbolo, nombre o ID de API).
    """
    return asset_service.update_asset(db=db, asset_id=asset_id, asset=asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """
    Elimina una moneda del sistema.
    """
    asset_service.delete_asset(db=db, asset_id=asset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
