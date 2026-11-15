from fastapi import APIRouter, status

from app.dependencias import membro_controller
from app.routes.schemas import MembroEntrada, MembroSaida

router = APIRouter(prefix="/membros", tags=["Membros"])


@router.get("", response_model=list[MembroSaida])
def listar_membros():
    return [m.para_dict() for m in membro_controller.listar()]


@router.post("", response_model=MembroSaida, status_code=status.HTTP_201_CREATED)
def criar_membro(entrada: MembroEntrada):
    return membro_controller.criar(entrada.nome, entrada.email).para_dict()
