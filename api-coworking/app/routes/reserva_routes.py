from datetime import date

from fastapi import APIRouter, Query, status

from app.dependencias import reserva_controller
from app.routes.schemas import FaturamentoSaida, ReservaEntrada, ReservaSaida

router = APIRouter(tags=["Reservas"])


@router.get("/reservas", response_model=list[ReservaSaida])
def listar_reservas(
    data: date | None = Query(default=None, description="Filtra pelo dia (AAAA-MM-DD)"),
    espaco_id: int | None = Query(default=None),
):
    return [r.para_resposta() for r in reserva_controller.listar(data, espaco_id)]


@router.post("/reservas", response_model=ReservaSaida, status_code=status.HTTP_201_CREATED)
def criar_reserva(entrada: ReservaEntrada):
    reserva = reserva_controller.criar(
        entrada.espaco_id, entrada.membro_id, entrada.inicio, entrada.fim
    )
    return reserva.para_resposta()


@router.get("/faturamento", response_model=FaturamentoSaida, tags=["Cálculo"])
def faturamento_do_dia(data: date = Query(description="Dia a calcular (AAAA-MM-DD)")):
    return reserva_controller.faturamento_do_dia(data)
