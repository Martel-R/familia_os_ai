import base64
from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.schemas import ReciboExtraido, ContrachequeExtraido
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

ocr_agent = OCRAgent()
