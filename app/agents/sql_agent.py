from typing import Optional, Dict, Any
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

class SQLAgent:
    def __init__(self, db_url: Optional[str] = None, api_key: Optional[str] = None):
        self.db_url = db_url or settings.SUPABASE_DB_URL
        self.api_key = api_key or settings.GOOGLE_API_KEY

    def responder(self, pergunta: str, familia_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "resposta": "A chave GOOGLE_API_KEY não foi configurada. Por favor, adicione-a ao arquivo .env.",
                "consulta_realizada": None
            }

        if not self.db_url:
            return {
                "resposta": "A URL de conexão com o banco de dados (SUPABASE_DB_URL) não foi configurada no .env.",
                "consulta_realizada": None
            }

        tenant_id = familia_id or settings.DEFAULT_FAMILIA_ID

        try:
            # Conexão direta com PostgreSQL mapeando o schema familialm
            db = SQLDatabase.from_uri(
                self.db_url,
                schema="familialm",
                include_tables=[
                    "familias",
                    "usuarios",
                    "inventario_itens",
                    "historico_manutencoes",
                    "agenda_contatos",
                    "transacoes_financeiras",
                    "tarefas_rotinas",
                    "eventos"
                ]
            )

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.api_key,
                temperature=0.0
            )

            prefixo = (
                "Você é o assistente inteligente multi-tenant do ecossistema Familia OS. "
                "Sua missão é responder perguntas da família consultando o banco de dados PostgreSQL. "
                "Todas as tabelas relevantes estão no schema 'familialm'. "
                f"REGRA DE ISOLAMENTO MULTI-TENANT OBRIGATÓRIA: Sempre filtre os registros pela família ativa "
                f"usando `WHERE (familia_id = '{tenant_id}' OR familia_id IS NULL)`. "
                "Nunca retorne dados de outro `familia_id`. "
                "Responda sempre em Português do Brasil (pt-BR) de forma amigável, clara e concisa."
            )

            agent = create_sql_agent(
                llm=llm,
                db=db,
                agent_type="tool-calling",
                verbose=False,
                prefix=prefixo
            )

            resultado = agent.invoke({"input": pergunta})
            saida = resultado.get("output", "Não foi possível obter uma resposta precisa.")
            if isinstance(saida, list) and len(saida) > 0:
                primeiro = saida[0]
                if isinstance(primeiro, dict) and "text" in primeiro:
                    saida = primeiro["text"]
                elif hasattr(primeiro, "content"):
                    saida = primeiro.content
                else:
                    saida = str(primeiro)

            return {
                "resposta": str(saida),
                "consulta_realizada": f"Consulta SQL multi-tenant executada no schema familialm (familia_id={tenant_id})."
            }

        except Exception as e:
            return {
                "resposta": f"Erro ao consultar o banco de dados do Familia OS: {str(e)}",
                "consulta_realizada": None
            }

sql_agent = SQLAgent()
