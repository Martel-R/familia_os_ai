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

class ItemContracheque(BaseModel):
    descricao: str = Field(description="Descrição da verba ou rubrica (ex: Salário Base, INSS, IRRF, Vale Refeição)")
    tipo: str = Field(description="'vencimento' se for provento/crédito, 'desconto' se for dedução")
    valor: float = Field(description="Valor numérico da rubrica")

class ContrachequeExtraido(BaseModel):
    fonte_pagadora: Optional[str] = Field(default=None, description="Nome do empregador, empresa ou órgão pagador")
    mes_ano_referencia: Optional[str] = Field(default=None, description="Mês e ano de competência (ex: 10/2026 ou Outubro/2026)")
    data_pagamento: Optional[str] = Field(default=None, description="Data de crédito ou pagamento no formato AAAA-MM-DD se legível")
    total_vencimentos: float = Field(description="Total bruto dos proventos/vencimentos")
    total_descontos: float = Field(description="Total geral de deduções e descontos")
    valor_liquido: float = Field(description="Valor líquido creditado ao trabalhador (vencimentos - descontos)")
    itens: List[ItemContracheque] = Field(default_factory=list, description="Lista discriminada das rubricas de vencimentos e descontos")

class TransacaoDocumento(BaseModel):
    data: Optional[str] = Field(default=None, description="Data da transação ou compra no formato AAAA-MM-DD se legível")
    descricao: str = Field(description="Nome do estabelecimento, favorecido ou descrição do lançamento")
    categoria_sugerida: Optional[str] = Field(default="Geral", description="Categoria provável (ex: Alimentação, Transporte, Lazer, Saúde, Serviços)")
    tipo: str = Field(default="despesa", description="'despesa' para compras/débitos/saídas ou 'receita' para créditos/entradas")
    valor: float = Field(description="Valor monetário positivo da transação")

class DocumentoFinanceiroExtraido(BaseModel):
    tipo_documento: str = Field(description="'fatura_cartao' para fatura de cartão de crédito ou 'extrato_bancario' para extrato de conta corrente/poupança")
    instituicao: Optional[str] = Field(default=None, description="Nome do banco ou emissor do cartão (ex: Nubank, Itaú, Inter, Bradesco)")
    periodo_referencia: Optional[str] = Field(default=None, description="Mês de referência ou período do extrato/fatura")
    data_vencimento_fatura: Optional[str] = Field(default=None, description="Data de vencimento da fatura do cartão no formato AAAA-MM-DD")
    valor_total: Optional[float] = Field(default=0.0, description="Valor total da fatura ou saldo final do extrato")
    transacoes: List[TransacaoDocumento] = Field(default_factory=list, description="Lista de todas as compras ou movimentações extraídas do documento")

class ChatRequest(BaseModel):
    pergunta: str = Field(description="Pergunta em linguagem natural sobre o inventário, manutenções ou contatos")

class ChatResponse(BaseModel):
    resposta: str = Field(description="Resposta humanizada gerada pelo agente")
    consulta_realizada: Optional[str] = Field(default=None, description="Informações ou SQL de consulta utilizado")

class ItemResultadoLaboratorial(BaseModel):
    nome_parametro: str = Field(description="Nome do parâmetro medido (ex: Glicose em Jejum, Hemoglobina, Colesterol HDL, TSH, Plaquetas, Ureia, Creatinina, Leucócitos)")
    resultado: str = Field(description="Resultado medido em texto ou número (ex: '92', '14.2', 'Não reagente', 'Negativo', 'Normal', '120/80')")
    valor_numerico: Optional[float] = Field(default=None, description="Valor numérico float se mensurável (ex: 92.0, 14.2)")
    unidade: Optional[str] = Field(default="", description="Unidade de medida (ex: 'mg/dL', 'g/dL', '%', 'mcUI/mL', '/mm³', 'ng/mL')")
    valor_referencia: Optional[str] = Field(default=None, description="Valores de referência indicados no laudo (ex: '70 a 99 mg/dL', 'Não reagente')")
    status_resultado: Optional[str] = Field(default="normal", description="'normal', 'alterado_alto', 'alterado_baixo' ou 'observacao'")

class ExameIndividual(BaseModel):
    titulo_exame: str = Field(description="Nome do exame individual (ex: 'Hemograma Completo', 'Glicemia de Jejum', 'Perfil Lipídico', 'Função Renal', 'TSH e Hormônios', 'Vitamina D', 'Urina Tipo 1')")
    data_exame: Optional[str] = Field(default=None, description="Data da realização do exame no formato AAAA-MM-DD")
    conclusao_ou_interpretacao: Optional[str] = Field(default=None, description="Interpretação, impressão diagnóstica ou conclusão clínica deste exame")
    resultados: List[ItemResultadoLaboratorial] = Field(default_factory=list, description="Lista completa de parâmetros e analitos medidos neste exame")

class ExameMedicoExtraido(BaseModel):
    paciente_nome: Optional[str] = Field(default=None, description="Nome do paciente identificado no laudo")
    data_geral: Optional[str] = Field(default=None, description="Data geral do laudo ou liberação no formato AAAA-MM-DD")
    laboratorio_ou_clinica: Optional[str] = Field(default=None, description="Nome do laboratório, hospital ou clínica (ex: Fleury, Dasa, Sabin)")
    medico_solicitante: Optional[str] = Field(default=None, description="Nome do médico solicitante ou responsável técnico")
    resumo_geral: Optional[str] = Field(default=None, description="Resumo ou conclusão geral dos achados clínicos")
    exames: List[ExameIndividual] = Field(default_factory=list, description="Lista de TODOS os exames laboratoriais ou médicos identificados no arquivo")
