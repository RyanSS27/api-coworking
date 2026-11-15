"""Regras de aplicação dos membros."""

from app.data.repositorio import Repositorio
from app.models.excecoes import ConflitoError, NaoEncontradoError
from app.models.membro import Membro


class MembroController:
    def __init__(self, repo_membros: Repositorio):
        self._repo = repo_membros

    def listar(self) -> list[Membro]:
        return [Membro.de_dict(d) for d in self._repo.listar()]

    def buscar(self, id: int) -> Membro:
        dados = self._repo.buscar_por_id(id)
        if dados is None:
            raise NaoEncontradoError(f"Membro {id} não encontrado.")
        return Membro.de_dict(dados)

    def criar(self, nome: str, email: str) -> Membro:
        membro = Membro(nome, email)  # model valida (422)
        if any(m.email == membro.email for m in self.listar()):
            raise ConflitoError(f"Já existe um membro com o e-mail {membro.email}.")
        salvo = self._repo.adicionar(membro.para_dict())
        membro.id = salvo["id"]
        return membro
