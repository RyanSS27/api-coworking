"""Liga os controllers aos repositórios JSON. As rotas importam daqui."""

from app.controllers.espaco_controller import EspacoController
from app.controllers.membro_controller import MembroController
from app.controllers.reserva_controller import ReservaController
from app.data.repositorio import RepositorioJson

_repo_espacos = RepositorioJson("espacos.json")
_repo_membros = RepositorioJson("membros.json")
_repo_reservas = RepositorioJson("reservas.json")

espaco_controller = EspacoController(_repo_espacos, _repo_reservas)
membro_controller = MembroController(_repo_membros)
reserva_controller = ReservaController(_repo_reservas, espaco_controller, membro_controller)

__all__ = [
    "EspacoController", "MembroController", "ReservaController",
    "espaco_controller", "membro_controller", "reserva_controller",
]
