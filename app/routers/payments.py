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

DEFAULT_DB_NONE = "null"


class Payment(BaseModel):
    """Represents one payment in the database"""

    ITEM: str
    DATA_PAGAMENTO: str
    CATEGORIA: str
    PRECO_TOTAL: float
    LOJA: str
    METODO_PAGAMENTO: str
    PRECO_DOLAR: Optional[float] = DEFAULT_DB_NONE
    PRECO_MOEDA_ALTERNATIVA: Optional[float] = DEFAULT_DB_NONE
    NOME_MOEDA_ALTERNATIVA: Optional[str] = DEFAULT_DB_NONE
    NOME_PESSOA_PAGADOR: str = settings.default_payment_user
    FLAG_PAGO: int = 0
    URL: Optional[str] = DEFAULT_DB_NONE
    TAGS: Optional[str] = DEFAULT_DB_NONE
    PRESENTEADO: Optional[str] = DEFAULT_DB_NONE
    FLAG_EM_ROTA: int = 0
    SK_SUBSCRIPTION: Optional[int] = DEFAULT_DB_NONE
    EMOJI: Optional[str] = DEFAULT_DB_NONE
    ID: Optional[int] = DEFAULT_DB_NONE


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
                + " VALUES ({newid}, '{newitem}', {newdate}, '{newcategory}', {newprice}"
                + ", '{newstore}', '{newmethod}', {dolar}, {altcoin}, '{altcoinname}'"
                + ", '{person}', {payed}, '{url}', '{tags}', '{present}', {inroute}, '{emoji}')"
            )
            payment.ID = max_id[0][0] + 1
            # TODO: remove stringified Null values
            insert = insert_statement.format(
                newid=payment.ID,
                newitem=payment.ITEM,
                newdate="TO_DATE('" + payment.DATA_PAGAMENTO + "', 'YYYY-MM-DD')",
                newcategory=payment.METODO_PAGAMENTO,
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
            cursor.execute(insert)
            connection.commit()
            logger.info("Payment registered")
            logger.debug("Payment: {payment}", payment=str(payment))
    return {"message": "Payment registered"}
