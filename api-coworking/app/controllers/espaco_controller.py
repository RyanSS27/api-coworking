"""Regras de aplicação dos espaços: chama o model e o repositório."""

from app.data.repositorio import Repositorio
from app.models.espaco import Espaco, criar_espaco, espaco_de_dict
from app.models.excecoes import ConflitoError, NaoEncontradoError


class EspacoController:
    def __init__(self, repo_espacos: Repositorio, repo_reservas: Repositorio):
        self._repo = repo_espacos
        self._repo_reservas = repo_reservas

    def listar(self, tipo: str | None = None) -> list[Espaco]:
        espacos = [espaco_de_dict(d) for d in self._repo.listar()]
        if tipo:
            espacos = [e for e in espacos if e.pertence_ao_tipo(tipo)]
        return espacos

    def buscar(self, id: int) -> Espaco:
        dados = self._repo.buscar_por_id(id)
        if dados is None:
            raise NaoEncontradoError(f"Espaço {id} não encontrado.")
        return espaco_de_dict(dados)

    def _garantir_nome_unico(self, nome: str, ignorar_id: int | None = None) -> None:
        for e in self.listar():
            if e.nome.lower() == nome.strip().lower() and e.id != ignorar_id:
                raise ConflitoError(f"Já existe um espaço chamado '{e.nome}'.")

    def criar(self, tipo: str, nome: str, capacidade: int) -> Espaco:
        espaco = criar_espaco(tipo, nome, capacidade)  # model valida (422)
        self._garantir_nome_unico(espaco.nome)          # 409
        salvo = self._repo.adicionar(espaco.para_dict())
        espaco.id = salvo["id"]
        return espaco

    def atualizar(self, id: int, nome: str | None = None, capacidade: int | None = None) -> Espaco:
        espaco = self.buscar(id)
        if nome is not None:
            self._garantir_nome_unico(nome, ignorar_id=id)
            espaco.nome = nome
        if capacidade is not None:
            espaco.capacidade = capacidade
        self._repo.atualizar(id, espaco.para_dict())
        return espaco

    def remover(self, id: int) -> None:
        self.buscar(id)
        if any(r["espaco_id"] == id for r in self._repo_reservas.listar()):
            raise ConflitoError("Espaço com reservas não pode ser removido.")
        self._repo.remover(id)
