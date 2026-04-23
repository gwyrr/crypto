from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.portfolio import AssetPerformance, PortfolioSummary
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.services import market_service


def _ensure_user_exists(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def _ensure_asset_exists(db: Session, asset_id: int) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return asset


def _ensure_transaction_owner(transaction: Transaction, user_id: int) -> Transaction:
    if transaction.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para acceder a esta transaccion",
        )
    return transaction


def _empty_portfolio_summary(user_id: int) -> PortfolioSummary:
    return PortfolioSummary(
        user_id=user_id,
        total_investment=0.0,
        current_total_value=0.0,
        total_profit_loss=0.0,
        assets=[],
    )


def list_transactions(db: Session, user_id: int | None = None) -> list[Transaction]:
    query = db.query(Transaction).order_by(Transaction.id)
    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    return query.all()


def get_transaction(
    db: Session,
    transaction_id: int,
    user_id: int | None = None,
) -> Transaction:
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
    _ensure_user_exists(db=db, user_id=user_id)
    _ensure_asset_exists(db=db, asset_id=transaction.asset_id)

    db_transaction = Transaction(
        user_id=user_id,
        asset_id=transaction.asset_id,
        amount=transaction.amount,
        buy_price=transaction.buy_price,
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
    db_transaction = get_transaction(db=db, transaction_id=transaction_id, user_id=user_id)

    if transaction.asset_id is not None:
        _ensure_asset_exists(db=db, asset_id=transaction.asset_id)
        db_transaction.asset_id = transaction.asset_id

    if transaction.amount is not None:
        db_transaction.amount = transaction.amount

    if transaction.buy_price is not None:
        db_transaction.buy_price = transaction.buy_price

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: int, user_id: int) -> None:
    db_transaction = get_transaction(db=db, transaction_id=transaction_id, user_id=user_id)
    db.delete(db_transaction)
    db.commit()


def to_transaction_read(transaction: Transaction) -> TransactionRead:
    return TransactionRead(
        id=transaction.id,
        user_id=transaction.user_id,
        asset_id=transaction.asset_id,
        amount=transaction.amount,
        buy_price=transaction.buy_price,
        date=transaction.date,
        investment=transaction.calculate_investment(),
    )


def get_user_portfolio_report(db: Session, user_id: int) -> PortfolioSummary:
    _ensure_user_exists(db=db, user_id=user_id)
    transactions = list_transactions(db=db, user_id=user_id)

    if not transactions:
        return _empty_portfolio_summary(user_id)

    portfolio_data: dict[int, dict[str, float | str]] = {}
    market_ids: list[str] = []

    for tx in transactions:
        asset = tx.asset
        market_id = asset.market_identifier()

        if asset.id not in portfolio_data:
            portfolio_data[asset.id] = {
                "symbol": asset.symbol,
                "market_id": market_id,
                "amount": 0.0,
                "total_cost": 0.0,
            }
            market_ids.append(market_id)

        portfolio_data[asset.id]["amount"] += tx.amount
        portfolio_data[asset.id]["total_cost"] += tx.amount * tx.buy_price

    current_prices = market_service.get_simple_prices(asset_ids=market_ids, vs_currency="usd")

    report_assets: list[AssetPerformance] = []
    total_investment = 0.0
    current_total_value = 0.0

    for asset_data in portfolio_data.values():
        symbol = str(asset_data["symbol"])
        market_id = str(asset_data["market_id"])
        amount = float(asset_data["amount"])
        purchase_value = float(asset_data["total_cost"])
        current_price = float(current_prices.get(market_id, {}).get("usd", 0.0))
        current_value = amount * current_price
        profit_loss = current_value - purchase_value

        total_investment += purchase_value
        current_total_value += current_value

        report_assets.append(
            AssetPerformance(
                symbol=symbol,
                amount=amount,
                purchase_value=purchase_value,
                current_value=current_value,
                profit_loss=profit_loss,
                percentage_change=(profit_loss / purchase_value) * 100 if purchase_value > 0 else 0.0,
            )
        )

    return PortfolioSummary(
        user_id=user_id,
        total_investment=total_investment,
        current_total_value=current_total_value,
        total_profit_loss=current_total_value - total_investment,
        assets=report_assets,
    )
