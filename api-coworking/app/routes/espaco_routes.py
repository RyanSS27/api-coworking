from fastapi import APIRouter, Query, Response, status

from app.dependencias import espaco_controller
from app.routes.schemas import EspacoAlteracao, EspacoEntrada, EspacoSaida, TipoEspaco

router = APIRouter(prefix="/espacos", tags=["Espaços"])


@router.get("", response_model=list[EspacoSaida])
def listar_espacos(tipo: TipoEspaco | None = Query(default=None)):
    return [e.para_dict() for e in espaco_controller.listar(tipo)]


@router.get("/{id}", response_model=EspacoSaida)
def buscar_espaco(id: int):
    return espaco_controller.buscar(id).para_dict()


@router.post("", response_model=EspacoSaida, status_code=status.HTTP_201_CREATED)
def criar_espaco(entrada: EspacoEntrada):
    return espaco_controller.criar(entrada.tipo, entrada.nome, entrada.capacidade).para_dict()


@router.put("/{id}", response_model=EspacoSaida)
def alterar_espaco(id: int, entrada: EspacoAlteracao):
    return espaco_controller.atualizar(id, entrada.nome, entrada.capacidade).para_dict()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_espaco(id: int):
    espaco_controller.remover(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
