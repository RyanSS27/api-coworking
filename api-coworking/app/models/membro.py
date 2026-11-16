"""Membro do coworking (quem faz a reserva)."""

from app.models.excecoes import DadoInvalidoError


class Membro:
    def __init__(self, nome: str, email: str, id: int | None = None):
        self._id = id
        self.nome = nome
        self.email = email

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, valor: int) -> None:
        self._id = valor

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valor: str) -> None:
        if not valor or len(valor.strip()) < 3:
            raise DadoInvalidoError("O nome do membro deve ter pelo menos 3 letras.")
        self._nome = valor.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        valor = (valor or "").strip().lower()
        if "@" not in valor or "." not in valor.split("@")[-1]:
            raise DadoInvalidoError("E-mail do membro inválido.")
        self._email = valor

    def para_dict(self) -> dict:
        return {"id": self._id, "nome": self._nome, "email": self._email}

    @classmethod
    def de_dict(cls, dados: dict) -> "Membro":
        return cls(nome=dados["nome"], email=dados["email"], id=dados.get("id"))
