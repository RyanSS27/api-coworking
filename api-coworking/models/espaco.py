"""Hierarquia de espaços do coworking.

Espaco (abstrata) -> Mesa, SalaReuniao, Auditorio

Cada filha define o próprio preço por hora e a própria regra de reserva.
Quem usa um Espaco chama sempre os mesmos métodos (polimorfismo),
sem precisar saber qual é o tipo.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from app.models.excecoes import DadoInvalidoError


class Espaco(ABC):
    """Topo da hierarquia. Não pode ser instanciada."""

    TIPO = ""
    CAPACIDADE_MAXIMA = 1

    def __init__(self, nome: str, capacidade: int, id: int | None = None):
        self._id = id
        self.nome = nome              # passa pelo setter (valida)
        self.capacidade = capacidade  # passa pelo setter (valida)

    # ------------------------------------------------------------------
    # Encapsulamento: atributos protegidos com @property e setter que valida
    # ------------------------------------------------------------------
    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, valor: int) -> None:
        self._id = valor

    @property
    def tipo(self) -> str:
        return self.TIPO

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise DadoInvalidoError("O nome do espaço não pode ficar vazio.")
        self._nome = valor.strip()

    @property
    def capacidade(self) -> int:
        return self._capacidade

    @capacidade.setter
    def capacidade(self, valor: int) -> None:
        if valor < 1 or valor > self.CAPACIDADE_MAXIMA:
            raise DadoInvalidoError(
                f"Capacidade de {self.TIPO} deve ficar entre 1 e "
                f"{self.CAPACIDADE_MAXIMA} pessoas."
            )
        self._capacidade = valor

    # ------------------------------------------------------------------
    # Métodos abstratos: cada filha resolve do seu jeito
    # ------------------------------------------------------------------
    @abstractmethod
    def preco_por_hora(self) -> float:
        """Preço cobrado por hora de uso do espaço."""

    @abstractmethod
    def validar_regra_do_tipo(self, inicio: datetime, fim: datetime, agora: datetime) -> None:
        """Regra de reserva específica do tipo de espaço."""

    # ------------------------------------------------------------------
    # Métodos concretos, usados igualmente por todas as filhas
    # ------------------------------------------------------------------
    def calcular_valor(self, horas: float) -> float:
        """Valor de uma reserva com a quantidade de horas informada."""
        return round(self.preco_por_hora() * horas, 2)

    def validar_reserva(self, inicio: datetime, fim: datetime, agora: datetime) -> None:
        """Regras comuns a qualquer espaço + a regra do tipo."""
        if fim <= inicio:
            raise DadoInvalidoError("O fim da reserva deve ser depois do início.")
        if inicio < agora:
            raise DadoInvalidoError("Não é possível reservar um horário que já passou.")
        if inicio.date() != fim.date():
            raise DadoInvalidoError("A reserva deve começar e terminar no mesmo dia.")
        self.validar_regra_do_tipo(inicio, fim, agora)

    def pertence_ao_tipo(self, tipo: str) -> bool:
        """Usado só para filtrar listagens (?tipo=), nunca para decidir cálculo."""
        return self.TIPO == tipo

    def para_dict(self) -> dict:
        return {
            "id": self._id,
            "tipo": self.tipo,
            "nome": self._nome,
            "capacidade": self._capacidade,
            "preco_por_hora": self.preco_por_hora(),
        }


class Mesa(Espaco):
    """Mesa individual de trabalho (posição fixa)."""

    TIPO = "mesa"
    PRECO_HORA = 15.0
    CAPACIDADE_MAXIMA = 1
    MINIMO_HORAS = 1

    def __init__(self, nome: str, capacidade: int = 1, id: int | None = None):
        super().__init__(nome, capacidade, id)

    def preco_por_hora(self) -> float:
        return self.PRECO_HORA

    def validar_regra_do_tipo(self, inicio: datetime, fim: datetime, agora: datetime) -> None:
        if fim - inicio < timedelta(hours=self.MINIMO_HORAS):
            raise DadoInvalidoError(
                f"Mesa deve ser reservada por pelo menos {self.MINIMO_HORAS} hora."
            )


class SalaReuniao(Espaco):
    """Sala fechada para reuniões; reserva de 1 a 4 horas."""

    TIPO = "sala_reuniao"
    PRECO_HORA = 50.0
    CAPACIDADE_MAXIMA = 12
    MINIMO_HORAS = 1
    MAXIMO_HORAS = 4

    def __init__(self, nome: str, capacidade: int, id: int | None = None):
        super().__init__(nome, capacidade, id)

    def preco_por_hora(self) -> float:
        return self.PRECO_HORA

    def validar_regra_do_tipo(self, inicio: datetime, fim: datetime, agora: datetime) -> None:
        duracao = fim - inicio
        if duracao < timedelta(hours=self.MINIMO_HORAS) or duracao > timedelta(hours=self.MAXIMO_HORAS):
            raise DadoInvalidoError(
                f"Sala de reunião só pode ser reservada de {self.MINIMO_HORAS} a "
                f"{self.MAXIMO_HORAS} horas."
            )


class Auditorio(Espaco):
    """Auditório para eventos; exige 48 h de antecedência e cobra preparação."""

    TIPO = "auditorio"
    PRECO_HORA = 200.0
    TAXA_PREPARACAO = 150.0
    CAPACIDADE_MAXIMA = 150
    ANTECEDENCIA_HORAS = 48

    def __init__(self, nome: str, capacidade: int, id: int | None = None):
        super().__init__(nome, capacidade, id)

    def preco_por_hora(self) -> float:
        return self.PRECO_HORA

    def validar_regra_do_tipo(self, inicio: datetime, fim: datetime, agora: datetime) -> None:
        if inicio - agora < timedelta(hours=self.ANTECEDENCIA_HORAS):
            raise DadoInvalidoError(
                f"Auditório só pode ser reservado com {self.ANTECEDENCIA_HORAS} horas "
                "de antecedência."
            )

    def calcular_valor(self, horas: float) -> float:
        # Sobrescreve o cálculo da mãe: soma a taxa fixa de preparação.
        return round(super().calcular_valor(horas) + self.TAXA_PREPARACAO, 2)


# Fábrica: escolhe a classe pelo texto do tipo usando um dicionário,
# sem if/elif sobre o tipo.
TIPOS_DE_ESPACO: dict[str, type[Espaco]] = {
    Mesa.TIPO: Mesa,
    SalaReuniao.TIPO: SalaReuniao,
    Auditorio.TIPO: Auditorio,
}


def criar_espaco(tipo: str, nome: str, capacidade: int, id: int | None = None) -> Espaco:
    classe = TIPOS_DE_ESPACO.get(tipo)
    if classe is None:
        raise DadoInvalidoError(
            f"Tipo de espaço inválido: '{tipo}'. Use: {', '.join(TIPOS_DE_ESPACO)}."
        )
    return classe(nome=nome, capacidade=capacidade, id=id)


def espaco_de_dict(dados: dict) -> Espaco:
    return criar_espaco(dados["tipo"], dados["nome"], dados["capacidade"], dados.get("id"))
