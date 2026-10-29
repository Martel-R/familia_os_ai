import base64
from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.schemas import (
    ReciboExtraido,
    ContrachequeExtraido,
    DocumentoFinanceiroExtraido,
    ExameMedicoExtraido,
    AvaliacaoClinicaRequest,
    AvaliacaoClinicaResponse,
)
from app.config import settings

class OCRAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY

    def _obter_llm(self):
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY não configurada. Defina a variável de ambiente.")
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.1
        )

    def processar_recibo(self, imagem_bytes: bytes, mime_type: str = "image/jpeg") -> ReciboExtraido:
        llm = self._obter_llm()
        structured_llm = llm.with_structured_output(ReciboExtraido)
        imagem_b64 = base64.b64encode(imagem_bytes).decode("utf-8")

        prompt = (
            "Você é um especialista em OCR e visão computacional para finanças domésticas. "
            "Analise cuidadosamente este cupom ou comprovante fiscal. "
            "Extraia o nome do fornecedor/loja, a data da compra (se legível), o valor total final, "
            "e cada item adquirido com sua respectiva quantidade e preço."
        )

        mensagem = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{imagem_b64}"
                }
            ]
        )

        return structured_llm.invoke([mensagem])

    def processar_contracheque(self, arquivo_bytes: bytes, mime_type: str = "application/pdf") -> ContrachequeExtraido:
        llm = self._obter_llm()
        structured_llm = llm.with_structured_output(ContrachequeExtraido)
        arquivo_b64 = base64.b64encode(arquivo_bytes).decode("utf-8")

        prompt = (
            "Você é um especialista em análise contábil e de folha de pagamento. "
            "Analise este documento de contracheque / holerite (imagem ou PDF). "
            "Extraia com precisão: o empregador/fonte pagadora, o mês/ano de referência da competência, "
            "a data de crédito/pagamento (AAAA-MM-DD), o total bruto de vencimentos/rendimentos, "
            "o total de deduções/descontos (INSS, IRRF, vales, etc.), e o valor líquido creditado. "
            "Liste também as principais rubricas (itens) identificadas com sua descrição, tipo (vencimento ou desconto) e valor."
        )

        mensagem = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{arquivo_b64}"
                }
            ]
        )

        return structured_llm.invoke([mensagem])

    def processar_documento_financeiro(
        self, arquivo_bytes: bytes, mime_type: str = "application/pdf"
    ) -> DocumentoFinanceiroExtraido:
        llm = self._obter_llm()
        structured_llm = llm.with_structured_output(DocumentoFinanceiroExtraido)
        arquivo_b64 = base64.b64encode(arquivo_bytes).decode("utf-8")

        prompt = (
            "Você é um especialista em inteligência financeira, conciliação bancária e análise de faturas de cartão de crédito. "
            "Analise com máxima atenção este documento financeiro (PDF ou imagem). "
            "1. Identifique se é uma fatura de cartão de crédito ('fatura_cartao') ou um extrato de conta ('extrato_bancario'). "
            "2. Extraia o nome da instituição bancária ou emissor do cartão (ex: Nubank, Itaú, Inter, etc.). "
            "3. Extraia o período/mês de referência e a data de vencimento da fatura (no formato AAAA-MM-DD), se houver. "
            "4. Extraia o valor total da fatura ou saldo final. "
            "5. Extraia CADA UMA das compras ou movimentações financeiras individuais listadas: data do lançamento (AAAA-MM-DD), "
            "descrição clara do estabelecimento/favorecido, categoria sugerida (ex: Alimentação, Transporte, Lazer, Assinatura, Mercado, Saúde, etc.), "
            "tipo ('despesa' para compras/débitos ou 'receita' para pagamentos/estornos/créditos) e valor numérico positivo."
        )

        mensagem = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{arquivo_b64}"
                }
            ]
        )

        return structured_llm.invoke([mensagem])

    def processar_exame_medico(
        self, arquivo_bytes: bytes, mime_type: str = "application/pdf"
    ) -> ExameMedicoExtraido:
        llm = self._obter_llm()
        structured_llm = llm.with_structured_output(ExameMedicoExtraido)
        arquivo_b64 = base64.b64encode(arquivo_bytes).decode("utf-8")

        prompt = (
            "Você é um médico patologista clínico e especialista em inteligência artificial para saúde familiar. "
            "Analise cuidadosamente este laudo ou documento de exame médico laboratorial/imagem (PDF ou imagem). "
            "MUITO IMPORTANTE: Um mesmo laudo ou arquivo costuma conter VÁRIOS exames diferentes realizados na mesma data "
            "(por exemplo: 1. Hemograma Completo, 2. Glicemia de Jejum, 3. Perfil Lipídico/Colesterol, 4. Ureia e Creatinina, "
            "5. TSH e Hormônios, 6. Urina EAS, 7. Parasitológico de Fezes, etc.). "
            "Você NÃO deve agrupar tudo em apenas um exame genérico. Identifique e extraia CADA EXAME separadamente dentro da lista `exames`. "
            "Para cada exame em `exames`: "
            "- `titulo_exame`: Título clínico claro do exame (ex: 'Hemograma Completo', 'Glicemia de Jejum', 'Perfil Lipídico', 'Função Renal - Ureia e Creatinina'). "
            "- `data_exame`: Data da realização ou liberação (AAAA-MM-DD). "
            "- `conclusao_ou_interpretacao`: Síntese ou conclusão clínica deste exame se houver. "
            "- `resultados`: Lista completa de TODOS os analitos/parâmetros medidos deste exame específico, com nome_parametro, "
            "resultado (texto ou número, ex: '92', '14.5', 'Não reagente', 'Negativo'), valor_numerico (float se mensurável), "
            "unidade (ex: 'mg/dL', 'g/dL', '%'), valor_referencia e status_resultado ('normal', 'alterado_alto', 'alterado_baixo' ou 'observacao'). "
            "Identifique também o nome do paciente, a data geral, o laboratório/clínica e o médico solicitante se constarem no cabeçalho/rodapé."
        )

        mensagem = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{arquivo_b64}"
                }
            ]
        )

        return structured_llm.invoke([mensagem])

    def gerar_avaliacao_clinica(self, dados: AvaliacaoClinicaRequest) -> AvaliacaoClinicaResponse:
        llm = self._obter_llm()
        structured_llm = llm.with_structured_output(AvaliacaoClinicaResponse)

        prompt = (
            f"Você é um médico de família experiente com foco em medicina preventiva e estilo de vida. "
            f"O paciente '{dados.nome_usuario}' deseja um relatório clínico para ter um 'norte' claro do que conversar "
            f"com o médico na sua próxima consulta. "
            f"Analise o prontuário e histórico de saúde disponível abaixo:\n\n"
            f"- Tipo Sanguíneo: {dados.tipo_sanguineo or 'Não informado'}\n"
            f"- Alergias Conhecidas: {dados.alergias or 'Nenhuma'}\n"
            f"- Medicamentos Contínuos: {dados.medicamentos_continuos or 'Nenhum'}\n"
            f"- Lembretes de Remédios Ativos: {', '.join(dados.remedios_ativos) if dados.remedios_ativos else 'Nenhum'}\n"
            f"- Histórico de Exames Recentes e Laudos: {dados.historico_exames}\n"
            f"- Diário de Métricas Vitais (Pressão, Glicemia, Peso, Temperatura): {dados.metricas_recentes}\n\n"
            f"Gere uma resposta estruturada contendo:\n"
            f"1. `resumo_clinico`: Síntese em tópicos dos achados de saúde do paciente em linguagem acessível e profissional. "
            f"Destaque tendências observadas (ex: níveis de glicose, perfil de colesterol, controle da pressão arterial, "
            f"deficiências de nutrientes ou vitaminas, funções renal/hepática) e possíveis pontos que merecem atenção clínica.\n"
            f"2. `orientacoes_medico`: Guia prático com 3 a 5 perguntas objetivas e tópicos prioritários para o paciente levar "
            f"e fazer diretamente ao médico na próxima consulta (ex: 'Perguntar se é necessário dosar insulina ou hemoglobina glicada', "
            f"'Questionar indicação de suplementação de Vitamina D', 'Avaliar necessidade de ajuste na dieta para redução de LDL').\n"
            f"3. `nivel_alerta`: Classifique como 'baixo' (parâmetros dentro da normalidade), 'moderado' (alterações que requerem acompanhamento "
            f"de rotina) ou 'alto' (alterações significativas que requerem atenção médica prioritária)."
        )

        mensagem = HumanMessage(content=prompt)
        return structured_llm.invoke([mensagem])

ocr_agent = OCRAgent()
