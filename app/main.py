import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import httpx

# ===========================
# CONFIGURAR LOGGING
# ===========================
logger = logging.getLogger("uvicorn")  # usa el logger de uvicorn
logger.setLevel(logging.INFO)

# ===========================
# APP
# ===========================
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Microservices
CONVERTER_URL = os.getenv("CONVERTER_URL", "https://udistrital23baseconverterservice-f9akbhb3ffffbfcy.eastus2-01.azurewebsites.net/converter")
FORMATTER_URL = os.getenv("FORMATTER_URL", "https://udistrital23formatterservice-exbvc8gcdhandwc6.eastus2-01.azurewebsites.net/converter")

OP_URLS = {
    "add": os.getenv("ADD_URL", "https://udistrital23additionservice-b0bwfabmdsf3cyd3.eastus2-01.azurewebsites.net/suma"),
    "sub": os.getenv("SUB_URL", "https://udistrital23substracionservice-eec5g6bge9btfgg0.eastus2-01.azurewebsites.net/resta"),
    "mul": os.getenv("MUL_URL", "https://udistrital23multiplicationservice-htbeecdzd7grfud5.eastus2-01.azurewebsites.net/multiplicacion"),
    "div": os.getenv("DIV_URL", "https://udistrital23divisionservice-d5c3drceguggccem.eastus2-01.azurewebsites.net/division"),
}

class CalcRequest(BaseModel):
    a: str
    base_a: int
    b: str
    base_b: int
    op: str
    result_base: int


# ===========================
# HELPER: CALL SERVICE
# ===========================
async def call_service(url: str, payload: dict):
    logger.info(f"→ Enviando petición a {url} con payload: {payload}")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=5.0)
            logger.info(f"← Respuesta {resp.status_code} desde {url}: {resp.text}")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"❌ Error llamando {url}: {e}")
        raise


# ===========================
# ENDPOINTS
# ===========================
@app.get("/")
async def index(request: Request):
    logger.info("📄 Renderizando template.html")
    return templates.TemplateResponse("template.html", {"request": request})


@app.post("/calculate")
async def calculate(payload: CalcRequest):
    logger.info(f"📥 Petición /calculate recibida: {payload}")

    op = payload.op.lower()
    if op not in OP_URLS:
        logger.error(f"Operación no soportada: {op}")
        raise HTTPException(400, "Operación no soportada")

    # Convertir primer número
    try:
        logger.info("🔄 Convirtiendo primer número…")
        conv_a = await call_service(CONVERTER_URL, {
            "numero": payload.a,
            "base": payload.base_a
        })
        a_int = conv_a["numero"]
        logger.info(f"✔ Primer número convertido a int: {a_int}")
    except Exception as e:
        logger.error(f"Error convirtiendo primer número: {e}")
        raise HTTPException(400, f"Error convirtiendo primer número: {e}")

    # Convertir segundo número
    try:
        logger.info("🔄 Convirtiendo segundo número…")
        conv_b = await call_service(CONVERTER_URL, {
            "numero": payload.b,
            "base": payload.base_b
        })
        b_int = conv_b["numero"]
        logger.info(f"✔ Segundo número convertido a int: {b_int}")
    except Exception as e:
        logger.error(f"Error convirtiendo segundo número: {e}")
        raise HTTPException(400, f"Error convirtiendo segundo número: {e}")

    # Operación
    try:
        logger.info(f"🧮 Realizando operación: {op}")
        op_result = await call_service(OP_URLS[op], {
            "numero_a": a_int,
            "numero_b": b_int
        })
        raw_result = op_result["resultado"]
        logger.info(f"✔ Resultado operación: {raw_result}")
    except Exception as e:
        logger.error(f"Error en operación: {e}")
        raise HTTPException(400, f"Error en operación: {e}")

    # Formateo final
    try:
        logger.info(f"🔢 Formateando resultado en base {payload.result_base}")
        fmt = await call_service(FORMATTER_URL, {
            "numero": raw_result,
            "base_origen" : 10,
            "base_destino": payload.result_base
        })
        formatted = fmt["numero"]
        logger.info(f"✔ Resultado final formateado: {formatted}")
    except Exception as e:
        logger.error(f"Error formateando resultado: {e}")
        raise HTTPException(400, f"Error formateando resultado: {e}")

    logger.info(f"📤 Enviando resultado final: {formatted}")
    return {"result": formatted}
