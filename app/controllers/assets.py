from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.asset import AssetRead, AssetUpdate, CryptocurrencyCreate
from app.services import asset_service


router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(asset: CryptocurrencyCreate, db: Session = Depends(get_db)):
    return asset_service.create_asset(db=db, asset=asset)


@router.get("/", response_model=list[AssetRead])
def list_assets(db: Session = Depends(get_db)):
    return asset_service.list_assets(db=db)


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    return asset_service.get_asset(db=db, asset_id=asset_id)


@router.put("/{asset_id}", response_model=AssetRead)
def update_asset(asset_id: int, asset: AssetUpdate, db: Session = Depends(get_db)):
    return asset_service.update_asset(db=db, asset_id=asset_id, asset=asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset_service.delete_asset(db=db, asset_id=asset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
