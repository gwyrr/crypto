from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.portfolio import PortfolioSummary
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.services import transaction_service


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    created_transaction = transaction_service.create_transaction(
        db=db,
        transaction=transaction,
        user_id=current_user.id,
    )
    return transaction_service.to_transaction_read(created_transaction)


@router.get("/", response_model=list[TransactionRead])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = transaction_service.list_transactions(db=db, user_id=current_user.id)
    return [transaction_service.to_transaction_read(item) for item in transactions]


@router.get("/portfolio", response_model=PortfolioSummary)
def get_current_user_portfolio_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transaction_service.get_user_portfolio_report(db=db, user_id=current_user.id)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = transaction_service.get_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id,
    )
    return transaction_service.to_transaction_read(transaction)


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_transaction = transaction_service.update_transaction(
        db=db,
        transaction_id=transaction_id,
        transaction=transaction,
        user_id=current_user.id,
    )
    return transaction_service.to_transaction_read(updated_transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction_service.delete_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
