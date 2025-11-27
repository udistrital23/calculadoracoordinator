from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Microservice endpoint configuration (override via env vars)
ADD_URL = os.getenv("ADD_SERVICE_URL", "http://add-service:8000/add")
SUB_URL = os.getenv("SUB_SERVICE_URL", "http://sub-service:8000/sub")
MUL_URL = os.getenv("MUL_SERVICE_URL", "http://mul-service:8000/mul")
DIV_URL = os.getenv("DIV_SERVICE_URL", "http://div-service:8000/div")
BAS_URL = os.getenv("DIV_SERVICE_URL", "http://div-service:8000/bas")


class CalcRequest(BaseModel):
    a: str
    b: str
    base: int
    op: str


def int_to_base(num: int, base: int) -> str:
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if base < 2 or base > len(digits):
        raise ValueError("base must be between 2 and 36")
    if num == 0:
        return "0"
    sign = "" if num >= 0 else "-"
    num = abs(num)
    out = ""
    while num:
        out = digits[num % base] + out
        num //= base
    return sign + out


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("template.html", {"request": request})


@app.post("/calculate")
async def calculate(payload: CalcRequest):
    op = payload.op.lower()
    service_map = {
        "add": ADD_URL,
        "sum": ADD_URL,
        "subtract": SUB_URL,
        "sub": SUB_URL,
        "mul": MUL_URL,
        "multiply": MUL_URL,
        "div": DIV_URL,
        "divide": DIV_URL,
    }
    if op not in service_map:
        raise HTTPException(status_code=400, detail="Unsupported operation")

    url = service_map[op]
    json_payload = {"a": payload.a, "b": payload.b, "base": payload.base}

    # Try forwarding to microservice; on failure, perform local fallback
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=json_payload, timeout=5.0)
            resp.raise_for_status()
            # Expect microservice to return JSON like {"result": "..."}
            return JSONResponse(content=resp.json())
        except Exception:
            # Fallback: do the calculation locally using integers
            try:
                a_int = int(payload.a, payload.base)
                b_int = int(payload.b, payload.base)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid numbers for base {payload.base}: {e}")

            if op in ("add", "sum"):
                res = a_int + b_int
            elif op in ("subtract", "sub"):
                res = a_int - b_int
            elif op in ("mul", "multiply"):
                res = a_int * b_int
            elif op in ("div", "divide"):
                if b_int == 0:
                    raise HTTPException(status_code=400, detail="Division by zero")
                # Integer division; microservice semantics may differ
                res = a_int // b_int
            else:
                raise HTTPException(status_code=400, detail="Unsupported operation")

            return {"result": int_to_base(res, payload.base)}
