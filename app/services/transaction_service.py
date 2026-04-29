# SERVICIO DE TRANSACCIONES

# Este modulo contiene las reglas matematicas y de negocio del portafolio.
# Aqui se previene que un usuario venda activos que no tiene y se calcula
# dinamicamente la ganancia (PnL) realizada y no realizada consultando precios.

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.portfolio import AssetPerformance, PortfolioSummary
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.services import market_service


# --- FUNCIONES AUXILIARES DE VALIDACION ---

def _ensure_user_exists(db: Session, user_id: int) -> User:
    """Verifica si el usuario existe en la DB antes de operar."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def _ensure_asset_exists(db: Session, asset_id: int) -> Asset:
    """Verifica si la criptomoneda existe en el catalogo."""
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return asset


def _ensure_transaction_owner(transaction: Transaction, user_id: int) -> Transaction:
    """Seguridad: Verifica que la transaccion pertenezca al usuario que la solicita."""
    if transaction.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para acceder a esta transaccion",
        )
    return transaction


def _empty_portfolio_summary(user_id: int) -> PortfolioSummary:
    """Retorna un objeto de resumen vacio para usuarios sin transacciones."""
    return PortfolioSummary(
        user_id=user_id,
        total_investment=0.0,
        current_total_value=0.0,
        total_profit_loss=0.0,
        assets=[],
    )


def _get_current_holding(db: Session, user_id: int, asset_id: int, exclude_transaction_id: int | None = None) -> float:
    """
    Calcula la cantidad neta (compras - ventas) que un usuario posee de un activo.
    Se usa para evitar 'ventas en corto' o saldos negativos.
    """
    from sqlalchemy.sql import func
    
    buy_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id, Transaction.asset_id == asset_id, Transaction.type == "buy"
    )
    sell_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id, Transaction.asset_id == asset_id, Transaction.type == "sell"
    )
    
    # Util al actualizar una transaccion existente
    if exclude_transaction_id is not None:
        buy_query = buy_query.filter(Transaction.id != exclude_transaction_id)
        sell_query = sell_query.filter(Transaction.id != exclude_transaction_id)
        
    buy_amount = buy_query.scalar() or 0.0
    sell_amount = sell_query.scalar() or 0.0
    
    return float(buy_amount - sell_amount)


# --- OPERACIONES CRUD ---

def list_transactions(db: Session, user_id: int | None = None, asset_id: int | None = None) -> list[Transaction]:
    """
    Recupera el historial de transacciones, con filtros opcionales
    para un usuario o activo especifico.
    """
    query = db.query(Transaction).order_by(Transaction.id)
    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    if asset_id is not None:
        query = query.filter(Transaction.asset_id == asset_id)
    return query.all()


def get_transaction(
    db: Session,
    transaction_id: int,
    user_id: int | None = None,
) -> Transaction:
    """
    Obtiene los detalles de una transaccion puntual.
    Si se provee un user_id, asegura que la transaccion le pertenezca.
    """
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada")
    if user_id is not None:
        _ensure_transaction_owner(transaction, user_id)
    return transaction


def create_transaction(
    db: Session,
    transaction: TransactionCreate,
    user_id: int,
) -> Transaction:
    """
    Registra una nueva operacion de compra o venta para el usuario indicado.
    Realiza validaciones de saldo disponible en caso de tratarse de una venta.
    """
    _ensure_user_exists(db=db, user_id=user_id)
    _ensure_asset_exists(db=db, asset_id=transaction.asset_id)

    # Validacion de inventario antes de vender
    if transaction.type == "sell":
        current_holding = _get_current_holding(db=db, user_id=user_id, asset_id=transaction.asset_id)
        if current_holding < transaction.amount:
            raise HTTPException(status_code=400, detail="Saldo insuficiente para vender")

    db_transaction = Transaction(
        user_id=user_id,
        asset_id=transaction.asset_id,
        amount=transaction.amount,
        buy_price=transaction.buy_price,
        type=transaction.type,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction: TransactionUpdate,
    user_id: int,
) -> Transaction:
    """
    Modifica una transaccion existente, recalculando la validez del saldo neto resultante.
    """
    db_transaction = get_transaction(db=db, transaction_id=transaction_id, user_id=user_id)

    new_asset_id = transaction.asset_id if transaction.asset_id is not None else db_transaction.asset_id
    new_amount = transaction.amount if transaction.amount is not None else db_transaction.amount
    new_type = transaction.type if transaction.type is not None else db_transaction.type

    # Validar que esta actualizacion no resulte en un saldo negativo considerando otras transacciones
    current_holding_without_this_tx = _get_current_holding(
        db=db, user_id=user_id, asset_id=new_asset_id, exclude_transaction_id=transaction_id
    )

    if new_type == "sell":
        if current_holding_without_this_tx < new_amount:
            raise HTTPException(status_code=400, detail="Saldo insuficiente para esta actualizacion")
    else:
        # Si se reduce una compra, verificar que las ventas posteriores sigan siendo validas
        if current_holding_without_this_tx + new_amount < 0:
            raise HTTPException(status_code=400, detail="Esta modificacion dejaria el saldo negativo debido a ventas posteriores")

    # Actualizacion de campos
    if transaction.asset_id is not None:
        _ensure_asset_exists(db=db, asset_id=transaction.asset_id)
        db_transaction.asset_id = transaction.asset_id

    if transaction.amount is not None:
        db_transaction.amount = transaction.amount

    if transaction.buy_price is not None:
        db_transaction.buy_price = transaction.buy_price
        
    if transaction.type is not None:
        db_transaction.type = transaction.type

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: int, user_id: int) -> None:
    """Elimina una transaccion del historial."""
    db_transaction = get_transaction(db=db, transaction_id=transaction_id, user_id=user_id)
    db.delete(db_transaction)
    db.commit()


def to_transaction_read(transaction: Transaction) -> TransactionRead:
    """Mapper de Modelo (SQLAlchemy) a Schema (Pydantic)."""
    return TransactionRead(
        id=transaction.id,
        user_id=transaction.user_id,
        asset_id=transaction.asset_id,
        type=transaction.type,
        amount=transaction.amount,
        buy_price=transaction.buy_price,
        date=transaction.date,
        investment=transaction.calculate_investment(),
    )


# --- GENERACION DE REPORTES (Logica Financiera) ---

def get_user_portfolio_report(db: Session, user_id: int) -> PortfolioSummary:
    """
    Genera un informe completo del portafolio del usuario.
    Agrupa sus transacciones, calcula saldos promedios y obtiene
    los precios del mercado en tiempo real para estimar ganancias o perdidas.
    """
    _ensure_user_exists(db=db, user_id=user_id)
    transactions = list_transactions(db=db, user_id=user_id)

    if not transactions:
        return _empty_portfolio_summary(user_id)

    # Diccionario para agrupar datos por moneda
    portfolio_data: dict[int, dict[str, float | str]] = {}
    market_ids: list[str] = []
    
    total_realized_profit = 0.0

    # 1. Agregacion de transacciones y calculo de costo promedio
    for tx in transactions:
        asset = tx.asset
        market_id = asset.market_identifier()

        if asset.id not in portfolio_data:
            portfolio_data[asset.id] = {
                "symbol": asset.symbol,
                "market_id": market_id,
                "amount": 0.0,
                "total_cost": 0.0,
                "realized_pnl": 0.0,
            }
            market_ids.append(market_id)

        if tx.is_buy:
            # Aumentamos posicion y costo total
            cost = tx.amount * tx.buy_price
            portfolio_data[asset.id]["amount"] += tx.amount
            portfolio_data[asset.id]["total_cost"] += cost
        else:
            # Al vender, calculamos la ganancia realizada (Realized PnL)
            revenue = tx.amount * tx.buy_price
            
            current_amount = portfolio_data[asset.id]["amount"]
            if current_amount > 0:
                avg_cost = portfolio_data[asset.id]["total_cost"] / current_amount
                cost_of_sale = tx.amount * avg_cost
                portfolio_data[asset.id]["total_cost"] -= cost_of_sale
                portfolio_data[asset.id]["realized_pnl"] += (revenue - cost_of_sale)
                total_realized_profit += (revenue - cost_of_sale)
            else:
                # Caso borde (deberia estar validado): venta sin compra previa
                portfolio_data[asset.id]["realized_pnl"] += revenue
                total_realized_profit += revenue
            portfolio_data[asset.id]["amount"] -= tx.amount

    # 2. Consulta de precios actuales a la API (CoinGecko)
    current_prices = market_service.get_simple_prices(asset_ids=market_ids, vs_currency="usd")

    # 3. Construccion del reporte final
    report_assets: list[AssetPerformance] = []
    total_investment = 0.0
    current_total_value = 0.0

    for asset_data in portfolio_data.values():
        symbol = str(asset_data["symbol"])
        market_id = str(asset_data["market_id"])
        amount = float(asset_data["amount"])
        purchase_value = float(asset_data["total_cost"])
        realized_pnl = float(asset_data["realized_pnl"])
        
        current_price = float(current_prices.get(market_id, {}).get("usd", 0.0))
        current_value = amount * current_price
        
        # PnL no realizado = valor actual - costo de lo que aun se tiene
        unrealized_pnl = current_value - purchase_value
        # PnL Total = Ganancia por ventas pasadas + Ganancia latente por lo que se tiene
        total_asset_pnl = unrealized_pnl + realized_pnl
        
        percentage_change = (total_asset_pnl / purchase_value) * 100 if purchase_value > 0 else 0.0

        # Omitir activos vacios sin historial relevante
        if amount <= 0.000001 and abs(total_asset_pnl) < 0.01:
            continue

        total_investment += purchase_value
        current_total_value += current_value

        report_assets.append(
            AssetPerformance(
                symbol=symbol,
                amount=amount,
                purchase_value=purchase_value,
                current_value=current_value,
                profit_loss=total_asset_pnl,
                percentage_change=percentage_change,
            )
        )

    return PortfolioSummary(
        user_id=user_id,
        total_investment=total_investment,
        current_total_value=current_total_value,
        # PnL Global = (Valor actual - Inversion pendiente) + Ganancias ya retiradas
        total_profit_loss=(current_total_value - total_investment) + total_realized_profit,
        assets=report_assets,
    )
