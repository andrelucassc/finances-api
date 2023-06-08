from datetime import datetime
from typing import Optional

import oracledb
from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(prefix="/pay")
settings = get_settings()

oracledb.init_oracle_client(lib_dir=settings.db_client_lib)


class Payment(BaseModel):
    """Represents one payment in the database"""

    ITEM: str
    DATA_PAGAMENTO: str
    CATEGORIA: str
    PRECO_TOTAL: float
    LOJA: str
    METODO_PAGAMENTO: str
    PRECO_DOLAR: Optional[float] = None
    PRECO_MOEDA_ALTERNATIVA: Optional[float] = None
    NOME_MOEDA_ALTERNATIVA: Optional[str] = None
    NOME_PESSOA_PAGADOR: str = settings.default_payment_user
    FLAG_PAGO: int = 0
    URL: Optional[str] = None
    TAGS: Optional[str] = None
    PRESENTEADO: Optional[str] = None
    FLAG_EM_ROTA: int = 0
    SK_SUBSCRIPTION: Optional[int] = None
    EMOJI: Optional[str] = None
    ID: Optional[int] = None


@router.post("/")
async def register_payment(payment: Payment):
    with oracledb.connect(
        dsn=settings.db_dsn,
        user=settings.db_user,
        password=settings.db_password,
        wallet_location=settings.db_wallet,
    ) as connection:
        with connection.cursor() as cursor:
            sql = "SELECT MAX(ID) FROM PAGAMENTOS"
            max_id = [f for f in cursor.execute(sql)]
            logger.debug("DB responded with {response}", response=str(max_id))
        with connection.cursor() as cursor:
            insert_statement = (
                "INSERT INTO PAGAMENTOS (ID, ITEM, DATA_PAGAMENTO, CATEGORIA, PRECO_TOTAL"
                + ", LOJA, METODO_PAGAMENTO, PRECO_DOLAR, PRECO_MOEDA_ALTERNATIVA"
                + ", NOME_MOEDA_ALTERNATIVA, NOME_PESSOA_PAGADOR, FLAG_PAGO"
                + ", URL, TAGS, PRESENTEADO, FLAG_EM_ROTA, EMOJI)"
                + " VALUES (:newid, :newitem, :newdate, :newcategory, :newprice"
                + ", :newstore, :newmethod, :dolar, :altcoin, :altcoinname"
                + ", :person, :payed, :url, :tags, :present, :inroute, :emoji)"
            )
            payment.ID = max_id[0][0] + 1
            cursor.execute(
                insert_statement,
                newid=payment.ID,
                newitem=payment.ITEM,
                newdate=datetime.strptime(payment.DATA_PAGAMENTO, "%Y-%m-%d"),
                newcategory=payment.CATEGORIA,
                newprice=payment.PRECO_TOTAL,
                newstore=payment.LOJA,
                newmethod=payment.METODO_PAGAMENTO,
                dolar=payment.PRECO_DOLAR,
                altcoin=payment.PRECO_MOEDA_ALTERNATIVA,
                altcoinname=payment.NOME_MOEDA_ALTERNATIVA,
                person=payment.NOME_PESSOA_PAGADOR,
                payed=payment.FLAG_PAGO,
                url=payment.URL,
                tags=payment.TAGS,
                present=payment.PRESENTEADO,
                inroute=payment.FLAG_EM_ROTA,
                emoji=payment.EMOJI,
            )

            connection.commit()
            logger.info("Payment registered")
            logger.debug("Payment: {payment}", payment=str(payment))
    return {"message": "Payment registered"}
