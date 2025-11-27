# Calculador Coordinator (FastAPI)

Proyecto ejemplo que expone una UI (template HTML) para una calculadora de múltiples bases.
La aplicación actúa como coordinador y reenvía las operaciones a microservicios especializados (que se implementarán en proyectos separados). Si el microservicio no responde, la app realiza una operación de respaldo en local.

Endpoints de microservicios (esperados):

- `POST http://add-service:8000/add` — suma
- `POST http://sub-service:8000/sub` — resta
- `POST http://mul-service:8000/mul` — multiplicación
- `POST http://div-service:8000/div` — división

Formato JSON esperado por cada microservicio (ejemplo):

```
{
  "a": "1010",
  "b": "111",
  "base": 2
}
```

Respuesta esperada (ejemplo):

```
{ "result": "10001" }
```

Cómo ejecutar localmente (sin Docker):

1. Crear y activar un virtualenv (opcional)
2. Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

3. Ejecutar:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Construir y ejecutar con Docker:

```bash
docker build -t calculador-coordinator:latest .
docker run -p 8000:8000 \
  -e ADD_SERVICE_URL=http://add-service:8000/add \
  -e SUB_SERVICE_URL=http://sub-service:8000/sub \
  -e MUL_SERVICE_URL=http://mul-service:8000/mul \
  -e DIV_SERVICE_URL=http://div-service:8000/div \
  calculador-coordinator:latest
```

La UI estará disponible en `http://localhost:8000/`.

Nota: los servicios `add-service`, `sub-service`, etc. son nombres de ejemplo (p. ej. en Docker Compose o Kubernetes puede usarse ese nombre como host). Si ejecuta los microservicios en otras rutas/hosts, ajuste las variables de entorno.
