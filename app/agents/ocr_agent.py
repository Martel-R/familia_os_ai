import base64
from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.schemas import ReciboExtraido
from app.config import settings

class OCRAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY

    def processar_recibo(self, imagem_bytes: bytes, mime_type: str = "image/jpeg") -> ReciboExtraido:
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY não configurada. Defina a variável de ambiente.")

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.1
        )

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

        resultado = structured_llm.invoke([mensagem])
        return resultado

ocr_agent = OCRAgent()
