"""Schemas Pydantic: validam só o FORMATO da entrada.

As regras de negócio (capacidade máxima, duração, antecedência, conflito)
ficam nos models.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TipoEspaco = Literal["mesa", "sala_reuniao", "auditorio"]


class EspacoEntrada(BaseModel):
    tipo: TipoEspaco
    nome: str = Field(min_length=1, max_length=80, examples=["Sala Ipê"])
    capacidade: int = Field(examples=[8])


class EspacoAlteracao(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
    capacidade: int


class EspacoSaida(BaseModel):
    id: int
    tipo: str
    nome: str
    capacidade: int
    preco_por_hora: float


class MembroEntrada(BaseModel):
    nome: str = Field(min_length=1, max_length=100, examples=["Mariana Maia"])
    email: str = Field(min_length=3, max_length=120, examples=["mariana@email.com"])


class MembroSaida(BaseModel):
    id: int
    nome: str
    email: str


class ReservaEntrada(BaseModel):
    espaco_id: int
    membro_id: int
    inicio: datetime = Field(examples=["2026-12-10T09:00:00"])
    fim: datetime = Field(examples=["2026-12-10T11:00:00"])


class ReservaSaida(BaseModel):
    id: int
    espaco: EspacoSaida
    membro: MembroSaida
    inicio: datetime
    fim: datetime
    duracao_horas: float
    valor_total: float


class FaturamentoSaida(BaseModel):
    data: str
    quantidade_reservas: int
    por_tipo: dict[str, float]
    total: float
