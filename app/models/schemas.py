from typing import List, Optional
from pydantic import BaseModel, Field

class ItemExtraido(BaseModel):
    nome_produto: str = Field(description="Nome ou descrição do item comprado")
    quantidade: float = Field(default=1.0, description="Quantidade comprada do produto")
    valor_unitario: float = Field(description="Valor unitário ou total do item")
    categoria_sugerida: Optional[str] = Field(default="Geral", description="Categoria do item (ex: Alimentação, Limpeza, Farmácia)")

class ReciboExtraido(BaseModel):
    fornecedor: Optional[str] = Field(default=None, description="Nome do estabelecimento comercial ou supermercado")
    data_compra: Optional[str] = Field(default=None, description="Data da compra no formato AAAA-MM-DD se identificável")
    valor_total: float = Field(description="Valor total da compra / nota fiscal")
    itens: List[ItemExtraido] = Field(default_factory=list, description="Lista de todos os itens identificados no cupom")

class ChatRequest(BaseModel):
    pergunta: str = Field(description="Pergunta em linguagem natural sobre o inventário, manutenções ou contatos")

class ChatResponse(BaseModel):
    resposta: str = Field(description="Resposta humanizada gerada pelo agente")
    consulta_realizada: Optional[str] = Field(default=None, description="Informações ou SQL de consulta utilizado")
