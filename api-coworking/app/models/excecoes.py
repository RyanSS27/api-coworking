"""Exceções de negócio do Coworking.

Cada exceção carrega o código HTTP que a camada de rotas deve devolver.
Assim nenhuma regra de negócio termina em erro 500.
"""


class ErroNegocio(Exception):
    """Classe base de todos os erros de regra de negócio."""

    status_code = 400

    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class NaoEncontradoError(ErroNegocio):
    """O registro procurado não existe (HTTP 404)."""

    status_code = 404


class ConflitoError(ErroNegocio):
    """A operação conflita com algo que já existe (HTTP 409)."""

    status_code = 409


class DadoInvalidoError(ErroNegocio):
    """O dado chegou no formato certo, mas quebra uma regra (HTTP 422)."""

    status_code = 422
