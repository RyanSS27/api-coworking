from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.models.excecoes import ErroNegocio
from app.routes import espaco_routes, membro_routes, reserva_routes

app = FastAPI(
    title="Coworking API",
    description="Reservas de mesas, salas de reunião e auditórios de um coworking.",
    version="1.0.0",
)


@app.exception_handler(ErroNegocio)
def tratar_erro_negocio(request: Request, erro: ErroNegocio):
    # Cada exceção já sabe o próprio código HTTP (404, 409 ou 422).
    return JSONResponse(status_code=erro.status_code, content={"detail": erro.mensagem})


app.include_router(espaco_routes.router)
app.include_router(membro_routes.router)
app.include_router(reserva_routes.router)


@app.get("/", include_in_schema=False)
def raiz():
    return {"mensagem": "Coworking API no ar. Acesse /docs para o Swagger."}
