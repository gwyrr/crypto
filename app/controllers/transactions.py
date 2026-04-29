# CONTROLADOR DE TRANSACCIONES
# Este es el nucleo operativo del portafolio. Permite a los usuarios
# registrar sus compras/ventas y consultar el estado de sus inversiones.

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.portfolio import PortfolioSummary
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.services import transaction_service


# Definicion del router para transacciones
router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    # Requiere que el usuario este autenticado
    current_user: User = Depends(get_current_user),
):
    """
    REGISTRAR OPERACION
    Crea una nueva compra o venta para el usuario que tiene la sesion activa.
    """
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
    """
    HISTORIAL DE TRANSACCIONES
    Retorna todas las operaciones realizadas por el usuario logueado.
    """
    transactions = transaction_service.list_transactions(db=db, user_id=current_user.id)
    return [transaction_service.to_transaction_read(item) for item in transactions]


@router.get("/portfolio", response_model=PortfolioSummary)
def get_current_user_portfolio_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    REPORTE DE PORTAFOLIO
    Genera el resumen financiero: inversion total, valor actual y PnL (ganancias/perdidas).
    Calcula todo en tiempo real consultando la API de mercado.
    """
    return transaction_service.get_user_portfolio_report(db=db, user_id=current_user.id)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    DETALLE DE TRANSACCION
    Obtiene los datos de una operacion especifica validando que pertenezca al usuario.
    """
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
    """
    EDITAR TRANSACCION
    Permite corregir errores en montos o precios de una transaccion pasada.
    """
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
    """
    ELIMINAR TRANSACCION
    Borra una operacion del historial.
    """
    transaction_service.delete_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
