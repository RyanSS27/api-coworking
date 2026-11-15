"""Testes das regras do tema Coworking (um ou mais por regra obrigatória)."""

from datetime import datetime, timedelta

import pytest

from app.controllers.espaco_controller import EspacoController
from app.controllers.membro_controller import MembroController
from app.controllers.reserva_controller import ReservaController
from app.data.repositorio import RepositorioJson
from app.models.espaco import Auditorio, Espaco, Mesa, SalaReuniao, criar_espaco
from app.models.excecoes import ConflitoError, DadoInvalidoError, NaoEncontradoError
from app.models.membro import Membro
from app.models.reserva import Reserva

AGORA = datetime(2026, 12, 1, 8, 0)
AMANHA_9H = datetime(2026, 12, 2, 9, 0)


@pytest.fixture
def membro():
    return Membro("Mariana Maia", "mariana@email.com", id=1)


def hora(h: int, dia: datetime = AMANHA_9H) -> datetime:
    return dia.replace(hour=h, minute=0)


# ---------------------------------------------------------------- classe abstrata
def test_espaco_abstrato_nao_pode_ser_instanciado():
    with pytest.raises(TypeError):
        Espaco("Qualquer", 1)


def test_filhas_herdam_de_espaco():
    for classe in (Mesa, SalaReuniao, Auditorio):
        assert issubclass(classe, Espaco)


# ---------------------------------------------------------------- RN01 preço por hora por tipo
def test_preco_por_hora_por_tipo():
    assert Mesa("Mesa 1").preco_por_hora() == 15.0
    assert SalaReuniao("Sala Ipê", 8).preco_por_hora() == 50.0
    assert Auditorio("Auditório", 100).preco_por_hora() == 200.0


def test_valor_total_polimorfico(membro):
    # Mesmo método, resultado diferente conforme o tipo do espaço.
    espacos_e_valores = [
        (Mesa("Mesa 1", id=1), 30.0),                    # 2h x 15
        (SalaReuniao("Sala Ipê", 8, id=2), 100.0),       # 2h x 50
        (Auditorio("Auditório", 100, id=3), 550.0),      # 2h x 200 + 150 de preparação
    ]
    for espaco, esperado in espacos_e_valores:
        reserva = Reserva(espaco, membro, hora(9), hora(11))
        assert reserva.valor_total() == esperado


# ---------------------------------------------------------------- RN02 sala de reunião de 1 a 4 horas
def test_sala_reuniao_aceita_entre_1_e_4_horas():
    sala = SalaReuniao("Sala Ipê", 8)
    sala.validar_reserva(hora(9), hora(10), AGORA)
    sala.validar_reserva(hora(9), hora(13), AGORA)


@pytest.mark.parametrize("inicio, fim", [
    (AMANHA_9H, AMANHA_9H + timedelta(minutes=30)),
    (AMANHA_9H, AMANHA_9H + timedelta(hours=5)),
])
def test_sala_reuniao_recusa_fora_de_1_a_4_horas(inicio, fim):
    with pytest.raises(DadoInvalidoError):
        SalaReuniao("Sala Ipê", 8).validar_reserva(inicio, fim, AGORA)


# ---------------------------------------------------------------- RN03 auditório com 48h de antecedência
def test_auditorio_recusa_menos_de_48_horas():
    with pytest.raises(DadoInvalidoError):
        Auditorio("Auditório", 100).validar_reserva(hora(9), hora(12), AGORA)


def test_auditorio_aceita_com_48_horas_ou_mais():
    inicio = AGORA + timedelta(hours=48)
    Auditorio("Auditório", 100).validar_reserva(inicio, inicio + timedelta(hours=3), AGORA)


# ---------------------------------------------------------------- RN04 sem conflito de horário
def test_reservas_sobrepostas_no_mesmo_espaco_conflitam(membro):
    sala = SalaReuniao("Sala Ipê", 8, id=1)
    existente = Reserva(sala, membro, hora(9), hora(11), id=1)
    nova = Reserva(sala, membro, hora(10), hora(12))
    with pytest.raises(ConflitoError):
        nova.validar(AGORA, [existente])


def test_reservas_encostadas_nao_conflitam(membro):
    sala = SalaReuniao("Sala Ipê", 8, id=1)
    existente = Reserva(sala, membro, hora(9), hora(11), id=1)
    nova = Reserva(sala, membro, hora(11), hora(12))
    nova.validar(AGORA, [existente])


def test_mesmo_horario_em_espacos_diferentes_nao_conflita(membro):
    existente = Reserva(SalaReuniao("Sala A", 8, id=1), membro, hora(9), hora(11), id=1)
    nova = Reserva(SalaReuniao("Sala B", 8, id=2), membro, hora(9), hora(11))
    nova.validar(AGORA, [existente])


# ---------------------------------------------------------------- regras gerais e encapsulamento
def test_fim_antes_do_inicio_e_invalido():
    with pytest.raises(DadoInvalidoError):
        Mesa("Mesa 1").validar_reserva(hora(11), hora(9), AGORA)


def test_nao_reserva_horario_passado():
    with pytest.raises(DadoInvalidoError):
        Mesa("Mesa 1").validar_reserva(AGORA - timedelta(hours=2), AGORA, AGORA)


def test_capacidade_acima_do_maximo_do_tipo_e_invalida():
    with pytest.raises(DadoInvalidoError):
        SalaReuniao("Sala Ipê", 20)
    with pytest.raises(DadoInvalidoError):
        Mesa("Mesa 1", capacidade=2)


def test_setter_de_nome_valida():
    mesa = Mesa("Mesa 1")
    with pytest.raises(DadoInvalidoError):
        mesa.nome = "   "


def test_email_do_membro_invalido():
    with pytest.raises(DadoInvalidoError):
        Membro("Mariana Maia", "email-sem-arroba")


def test_tipo_de_espaco_desconhecido():
    with pytest.raises(DadoInvalidoError):
        criar_espaco("cabine", "Cabine 1", 1)


# ---------------------------------------------------------------- controllers + persistência JSON
@pytest.fixture
def controllers(tmp_path):
    repo_espacos = RepositorioJson("espacos.json", tmp_path)
    repo_membros = RepositorioJson("membros.json", tmp_path)
    repo_reservas = RepositorioJson("reservas.json", tmp_path)
    espacos = EspacoController(repo_espacos, repo_reservas)
    membros = MembroController(repo_membros)
    reservas = ReservaController(repo_reservas, espacos, membros)
    return espacos, membros, reservas


def test_espaco_inexistente_gera_nao_encontrado(controllers):
    espacos, _, _ = controllers
    with pytest.raises(NaoEncontradoError):
        espacos.buscar(99)


def test_nome_de_espaco_duplicado_gera_conflito(controllers):
    espacos, _, _ = controllers
    espacos.criar("mesa", "Mesa 1", 1)
    with pytest.raises(ConflitoError):
        espacos.criar("mesa", "mesa 1", 1)


def test_dados_continuam_no_arquivo(tmp_path, controllers):
    espacos, _, _ = controllers
    espacos.criar("sala_reuniao", "Sala Ipê", 8)
    # Um repositório novo, lendo o mesmo arquivo (como depois de reiniciar o servidor)
    novo = EspacoController(RepositorioJson("espacos.json", tmp_path), RepositorioJson("reservas.json", tmp_path))
    assert [e.nome for e in novo.listar()] == ["Sala Ipê"]


def test_faturamento_do_dia_soma_todos_os_tipos(controllers):
    espacos, membros, reservas = controllers
    mesa = espacos.criar("mesa", "Mesa 1", 1)
    sala = espacos.criar("sala_reuniao", "Sala Ipê", 8)
    auditorio = espacos.criar("auditorio", "Auditório", 100)
    m = membros.criar("Mariana Maia", "mariana@email.com")

    dia = datetime(2026, 12, 10)
    reservas.criar(mesa.id, m.id, hora(9, dia), hora(13, dia), agora=AGORA)        # 60
    reservas.criar(sala.id, m.id, hora(14, dia), hora(16, dia), agora=AGORA)       # 100
    reservas.criar(auditorio.id, m.id, hora(18, dia), hora(20, dia), agora=AGORA)  # 550

    resultado = reservas.faturamento_do_dia(dia.date())
    assert resultado["quantidade_reservas"] == 3
    assert resultado["total"] == 710.0
    assert resultado["por_tipo"] == {"mesa": 60.0, "sala_reuniao": 100.0, "auditorio": 550.0}


def test_espaco_com_reserva_nao_pode_ser_removido(controllers):
    espacos, membros, reservas = controllers
    sala = espacos.criar("sala_reuniao", "Sala Ipê", 8)
    m = membros.criar("Mariana Maia", "mariana@email.com")
    reservas.criar(sala.id, m.id, hora(9), hora(10), agora=AGORA)
    with pytest.raises(ConflitoError):
        espacos.remover(sala.id)
