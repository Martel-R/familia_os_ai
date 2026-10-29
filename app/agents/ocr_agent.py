import base64
from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.schemas import (
    ReciboExtraido,
    ContrachequeExtraido,
    DocumentoFinanceiroExtraido,
    ExameMedicoExtraido,
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
            "1. Identifique o nome do paciente (se legível), a data do exame no formato AAAA-MM-DD, o laboratório ou clínica emissora, "
            "e o médico solicitante (se houver). "
            "2. Extraia o título ou tipo do exame (ex: 'Hemograma Completo', 'Perfil Lipídico', 'Glicemia de Jejum', 'Urina Tipo 1', 'TSH e T4 Livre', 'Ecocardiograma'). "
            "3. Extraia a conclusão ou resumo diagnóstico do laudo. "
            "4. Extraia CADA UMA das métricas e medições laboratoriais encontradas: "
            "tipo_metrica ('glicemia', 'colesterol', 'pressao', 'hemoglobina', 'plaquetas', 'leucocitos', 'tsh', 'vitamina_d', 'creatinina', 'peso', etc.), "
            "nome_parametro (ex: 'Glicose em Jejum', 'Colesterol HDL', 'Hemoglobina'), "
            "valor_obtido (número float), unidade (ex: 'mg/dL', 'g/dL', '%', 'mcUI/mL'), "
            "valor_referencia (ex: '70 a 99 mg/dL'), e status_resultado ('normal', 'alterado_alto' ou 'alterado_baixo')."
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

ocr_agent = OCRAgent()
