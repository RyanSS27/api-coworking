"""Reserva: composição de um Espaco e um Membro.

A reserva guarda os objetos (não só os ids) e usa os métodos deles:
o espaço valida o horário e calcula o valor; o membro identifica quem reservou.
"""

from datetime import date, datetime

from app.models.espaco import Espaco
from app.models.excecoes import ConflitoError
from app.models.membro import Membro


class Reserva:
    def __init__(
        self,
        espaco: Espaco,
        membro: Membro,
        inicio: datetime,
        fim: datetime,
        id: int | None = None,
    ):
        self._id = id
        self._espaco = espaco
        self._membro = membro
        self._inicio = inicio
        self._fim = fim

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, valor: int) -> None:
        self._id = valor

    @property
    def espaco(self) -> Espaco:
        return self._espaco

    @property
    def membro(self) -> Membro:
        return self._membro

    @property
    def inicio(self) -> datetime:
        return self._inicio

    @property
    def fim(self) -> datetime:
        return self._fim

    # ------------------------------------------------------------------
    # Regras
    # ------------------------------------------------------------------
    def duracao_horas(self) -> float:
        return (self._fim - self._inicio).total_seconds() / 3600

    def valor_total(self) -> float:
        # Polimorfismo: o espaço (qualquer filha) sabe calcular o próprio valor.
        return self._espaco.calcular_valor(self.duracao_horas())

    def conflita_com(self, outra: "Reserva") -> bool:
        """Duas reservas conflitam se são do mesmo espaço e os horários se cruzam."""
        mesmo_espaco = self._espaco.id == outra.espaco.id
        horarios_cruzam = self._inicio < outra.fim and outra.inicio < self._fim
        return mesmo_espaco and horarios_cruzam

    def acontece_em(self, dia: date) -> bool:
        return self._inicio.date() == dia

    def validar(self, agora: datetime, reservas_existentes: list["Reserva"]) -> None:
        """Valida a reserva nova: regras do espaço + sem conflito de horário."""
        self._espaco.validar_reserva(self._inicio, self._fim, agora)
        for outra in reservas_existentes:
            if outra.id != self._id and self.conflita_com(outra):
                raise ConflitoError(
                    f"O espaço '{self._espaco.nome}' já está reservado entre "
                    f"{outra.inicio:%d/%m/%Y %H:%M} e {outra.fim:%H:%M}."
                )

    def para_dict(self) -> dict:
        """Formato salvo no JSON: guarda só os ids de espaço e membro."""
        return {
            "id": self._id,
            "espaco_id": self._espaco.id,
            "membro_id": self._membro.id,
            "inicio": self._inicio.isoformat(),
            "fim": self._fim.isoformat(),
        }

    def para_resposta(self) -> dict:
        """Formato devolvido pela API: com os objetos compostos e o valor."""
        return {
            "id": self._id,
            "espaco": self._espaco.para_dict(),
            "membro": self._membro.para_dict(),
            "inicio": self._inicio.isoformat(),
            "fim": self._fim.isoformat(),
            "duracao_horas": round(self.duracao_horas(), 2),
            "valor_total": self.valor_total(),
        }
