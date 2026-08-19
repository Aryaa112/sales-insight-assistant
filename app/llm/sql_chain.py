from app.llm.llm_config import get_llm
from app.llm.prompts import SQL_GENERATION_PROMPT


def get_sql_chain():
    llm = get_llm()

    chain = SQL_GENERATION_PROMPT | llm

    return chain