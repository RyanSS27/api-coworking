"""Regras de aplicação das reservas e do faturamento."""

from datetime import date, datetime

from app.controllers.espaco_controller import EspacoController
from app.controllers.membro_controller import MembroController
from app.data.repositorio import Repositorio
from app.models.reserva import Reserva


class ReservaController:
    def __init__(
        self,
        repo_reservas: Repositorio,
        espacos: EspacoController,
        membros: MembroController,
    ):
        self._repo = repo_reservas
        self._espacos = espacos
        self._membros = membros

    def _montar(self, dados: dict) -> Reserva:
        """Remonta a composição: busca os objetos Espaco e Membro pelos ids."""
        return Reserva(
            espaco=self._espacos.buscar(dados["espaco_id"]),
            membro=self._membros.buscar(dados["membro_id"]),
            inicio=datetime.fromisoformat(dados["inicio"]),
            fim=datetime.fromisoformat(dados["fim"]),
            id=dados["id"],
        )

    def listar(self, dia: date | None = None, espaco_id: int | None = None) -> list[Reserva]:
        reservas = [self._montar(d) for d in self._repo.listar()]
        if dia:
            reservas = [r for r in reservas if r.acontece_em(dia)]
        if espaco_id:
            reservas = [r for r in reservas if r.espaco.id == espaco_id]
        return reservas

    def criar(
        self,
        espaco_id: int,
        membro_id: int,
        inicio: datetime,
        fim: datetime,
        agora: datetime | None = None,
    ) -> Reserva:
        reserva = Reserva(
            espaco=self._espacos.buscar(espaco_id),   # 404 se não existir
            membro=self._membros.buscar(membro_id),   # 404 se não existir
            inicio=inicio,
            fim=fim,
        )
        existentes = self.listar(espaco_id=espaco_id)
        reserva.validar(agora or datetime.now(), existentes)  # 422 ou 409
        salvo = self._repo.adicionar(reserva.para_dict())
        reserva.id = salvo["id"]
        return reserva

    def faturamento_do_dia(self, dia: date) -> dict:
        """Soma o valor_total() de todas as reservas do dia.

        O mesmo método é chamado para qualquer tipo de espaço (polimorfismo):
        nenhum if sobre o tipo decide o cálculo.
        """
        reservas = self.listar(dia=dia)
        por_tipo: dict[str, float] = {}
        for r in reservas:
            por_tipo[r.espaco.tipo] = round(por_tipo.get(r.espaco.tipo, 0) + r.valor_total(), 2)
        return {
            "data": dia.isoformat(),
            "quantidade_reservas": len(reservas),
            "por_tipo": por_tipo,
            "total": round(sum(r.valor_total() for r in reservas), 2),
        }
