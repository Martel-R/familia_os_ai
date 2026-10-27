from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import (
    ReciboExtraido,
    ContrachequeExtraido,
    DocumentoFinanceiroExtraido,
    ChatRequest,
    ChatResponse,
)
from app.agents.ocr_agent import ocr_agent
from app.agents.sql_agent import sql_agent

app = FastAPI(
    title="Familia OS - Agente IA",
    description="Serviço isolado para OCR de cupons fiscais, análise de contracheques, extratos bancários, faturas de cartão e consultas em linguagem natural (Text-to-SQL).",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {
        "servico": "Familia OS - Agente IA",
        "status": "online",
        "versao": "1.2.0",
        "endpoints": {
            "ocr_cupom": "/api/ocr/receipt",
            "ocr_contracheque": "/api/ocr/payslip",
            "ocr_documento_financeiro": "/api/ocr/financial-doc",
            "chat_sql": "/api/chat",
            "docs": "/docs"
        }
    }

@app.post("/api/ocr/receipt", response_model=ReciboExtraido, summary="OCR de Cupom Fiscal com Visão Computacional")
async def extrair_cupom(file: UploadFile = File(...)):
    """
    Recebe o upload de foto de cupom fiscal (JPEG/PNG) e utiliza o Gemini 2.5 Flash
    para extrair fornecedor, data, valor total e itens discriminados.
    """
    if not (file.content_type.startswith("image/") or file.content_type == "application/pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser uma imagem ou PDF.")

    try:
        conteudo_bytes = await file.read()
        return ocr_agent.processar_recibo(conteudo_bytes, mime_type=file.content_type or "image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar cupom: {str(e)}")

@app.post("/api/ocr/payslip", response_model=ContrachequeExtraido, summary="Extração Inteligente de Contracheque / Holerite")
async def extrair_contracheque(file: UploadFile = File(...)):
    """
    Recebe o upload de contracheque (PDF ou imagem) e extrai:
    - Empregador / Fonte pagadora
    - Mês e ano de competência
    - Salário bruto, total de descontos e valor líquido
    - Rubricas discriminadas
    """
    content_type = file.content_type or "application/pdf"
    if not (content_type == "application/pdf" or content_type.startswith("image/")):
        raise HTTPException(status_code=400, detail="Formato inválido. Envie um arquivo PDF ou imagem (PNG/JPEG).")

    try:
        conteudo_bytes = await file.read()
        return ocr_agent.processar_contracheque(conteudo_bytes, mime_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar contracheque: {str(e)}")

@app.post(
    "/api/ocr/financial-doc",
    response_model=DocumentoFinanceiroExtraido,
    summary="Extração de Extratos Bancários e Faturas de Cartão",
)
async def extrair_documento_financeiro(file: UploadFile = File(...)):
    """
    Recebe o upload de fatura de cartão de crédito ou extrato bancário (PDF ou imagem)
    e extrai todas as compras e movimentações individuais para conciliação no fluxo de caixa.
    """
    content_type = file.content_type or "application/pdf"
    if not (content_type == "application/pdf" or content_type.startswith("image/")):
        raise HTTPException(status_code=400, detail="Formato inválido. Envie um arquivo PDF ou imagem (PNG/JPEG).")

    try:
        conteudo_bytes = await file.read()
        return ocr_agent.processar_documento_financeiro(conteudo_bytes, mime_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar documento financeiro: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse, summary="Consulta conversacional ao inventário e rotinas (Text-to-SQL)")
async def conversar_com_banco(requisicao: ChatRequest):
    """
    Recebe uma pergunta em linguagem natural e consulta o schema 'familialm' no PostgreSQL via Gemini.
    """
    if not requisicao.pergunta.strip():
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    resultado = sql_agent.responder(requisicao.pergunta)
    return ChatResponse(
        resposta=resultado["resposta"],
        consulta_realizada=resultado.get("consulta_realizada")
    )
