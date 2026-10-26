from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import ReciboExtraido, ChatRequest, ChatResponse
from app.agents.ocr_agent import ocr_agent
from app.agents.sql_agent import sql_agent

app = FastAPI(
    title="Familia OS - Agente IA",
    description="Serviço isolado para OCR de cupons fiscais e consultas em linguagem natural (Text-to-SQL) sobre o ecossistema familiar.",
    version="1.0.0"
)

# Configuração de CORS para permitir acesso do Dashboard Web e App Android
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
        "versao": "1.0.0",
        "endpoints": {
            "ocr": "/api/ocr/receipt",
            "chat_sql": "/api/chat",
            "docs": "/docs"
        }
    }

@app.post("/api/ocr/receipt", response_model=ReciboExtraido, summary="OCR de Cupom Fiscal com Visão Computacional")
async def extrair_cupom(file: UploadFile = File(...)):
    """
    Recebe o upload de uma foto de cupom fiscal (JPEG/PNG) e utiliza o Gemini Vision
    via LangChain para extrair os itens, fornecedor e valor total estruturados.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado deve ser uma imagem válida.")

    try:
        conteudo_bytes = await file.read()
        resultado = ocr_agent.processar_recibo(conteudo_bytes, mime_type=file.content_type)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem do cupom: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse, summary="Consulta conversacional ao inventário e rotinas (Text-to-SQL)")
async def conversar_com_banco(requisicao: ChatRequest):
    """
    Recebe uma pergunta em linguagem natural (ex: 'Onde está a furadeira?', 'Quantas moedas o Gabriel tem?')
    e consulta o schema 'familialm' no banco de dados via LangChain SQL Agent.
    """
    if not requisicao.pergunta.strip():
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    resultado = sql_agent.responder(requisicao.pergunta)
    return ChatResponse(
        resposta=resultado["resposta"],
        consulta_realizada=resultado.get("consulta_realizada")
    )
