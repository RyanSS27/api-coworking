"""Persistência em arquivo.

Repositorio é o contrato (abstrato); RepositorioJson guarda os dados em
app/data/*.json. Os controllers só conhecem o contrato.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path

PASTA_DADOS = Path(__file__).resolve().parent


class Repositorio(ABC):
    @abstractmethod
    def listar(self) -> list[dict]: ...

    @abstractmethod
    def buscar_por_id(self, id: int) -> dict | None: ...

    @abstractmethod
    def adicionar(self, dados: dict) -> dict: ...

    @abstractmethod
    def atualizar(self, id: int, dados: dict) -> dict | None: ...

    @abstractmethod
    def remover(self, id: int) -> bool: ...


class RepositorioJson(Repositorio):
    def __init__(self, nome_arquivo: str, pasta: Path | str = PASTA_DADOS):
        self._caminho = Path(pasta) / nome_arquivo
        self._caminho.parent.mkdir(parents=True, exist_ok=True)
        if not self._caminho.exists():
            self._gravar([])

    # ----------------------------- leitura e escrita do arquivo
    def _ler(self) -> list[dict]:
        texto = self._caminho.read_text(encoding="utf-8").strip()
        return json.loads(texto) if texto else []

    def _gravar(self, registros: list[dict]) -> None:
        self._caminho.write_text(
            json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _proximo_id(self, registros: list[dict]) -> int:
        return max((r["id"] for r in registros), default=0) + 1

    # ----------------------------- contrato
    def listar(self) -> list[dict]:
        return self._ler()

    def buscar_por_id(self, id: int) -> dict | None:
        return next((r for r in self._ler() if r["id"] == id), None)

    def adicionar(self, dados: dict) -> dict:
        registros = self._ler()
        novo = {**dados, "id": self._proximo_id(registros)}
        registros.append(novo)
        self._gravar(registros)
        return novo

    def atualizar(self, id: int, dados: dict) -> dict | None:
        registros = self._ler()
        for indice, registro in enumerate(registros):
            if registro["id"] == id:
                registros[indice] = {**dados, "id": id}
                self._gravar(registros)
                return registros[indice]
        return None

    def remover(self, id: int) -> bool:
        registros = self._ler()
        restantes = [r for r in registros if r["id"] != id]
        if len(restantes) == len(registros):
            return False
        self._gravar(restantes)
        return True
