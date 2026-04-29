from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.asset import Asset, Cryptocurrency
from app.schemas.asset import AssetUpdate, CryptocurrencyCreate


def list_assets(db: Session):
    """
    Obtiene el listado completo de activos financieros disponibles.
    """
    return db.query(Asset).order_by(Asset.id).all()


def get_asset(db: Session, asset_id: int):
    """
    Recupera un activo por su identificador.
    Lanza una excepcion 404 si no se encuentra.
    """
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return asset


def create_asset(db: Session, asset: CryptocurrencyCreate):
    """
    Registra un nuevo activo en el sistema, comunmente una criptomoneda.
    Verifica que el simbolo y el identificador de API no se dupliquen.
    """
    existing_symbol = db.query(Asset).filter(Asset.symbol == asset.symbol).first()
    if existing_symbol:
        raise HTTPException(status_code=409, detail="El simbolo ya existe")

    existing_api_id = (
        db.query(Cryptocurrency)
        .filter(Cryptocurrency.api_id == asset.api_id)
        .first()
    )
    if existing_api_id:
        raise HTTPException(status_code=409, detail="El api_id ya esta registrado")

    db_asset = Cryptocurrency(
        name=asset.name,
        symbol=asset.symbol,
        api_id=asset.api_id,
    )
    db.add(db_asset)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible crear el activo")

    db.refresh(db_asset)
    return db_asset


def update_asset(db: Session, asset_id: int, asset: AssetUpdate):
    """
    Modifica los detalles de un activo especifico.
    Controla colisiones de simbolos o identificadores de la API externa.
    """
    db_asset = get_asset(db=db, asset_id=asset_id)

    if asset.name is not None:
        db_asset.name = asset.name

    if asset.symbol is not None and asset.symbol != db_asset.symbol:
        existing_symbol = (
            db.query(Asset)
            .filter(Asset.symbol == asset.symbol, Asset.id != asset_id)
            .first()
        )
        if existing_symbol:
            raise HTTPException(status_code=409, detail="El simbolo ya existe")
        db_asset.symbol = asset.symbol

    if asset.api_id is not None and hasattr(db_asset, "api_id"):
        existing_api_id = (
            db.query(Cryptocurrency)
            .filter(Cryptocurrency.api_id == asset.api_id, Cryptocurrency.id != asset_id)
            .first()
        )
        if existing_api_id:
            raise HTTPException(status_code=409, detail="El api_id ya esta registrado")
        db_asset.api_id = asset.api_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible actualizar el activo")

    db.refresh(db_asset)
    return db_asset


def delete_asset(db: Session, asset_id: int):
    """
    Borra un activo del registro del sistema.
    """
    db_asset = get_asset(db=db, asset_id=asset_id)
    db.delete(db_asset)
    db.commit()
