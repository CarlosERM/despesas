"""Interface de linha de comando do sistema de reserva de salas.

Única camada que lê entrada e escreve saída; as regras ficam em agenda.py.
"""

from datetime import date, time

from agenda import Agenda, Reserva, ErroReserva, interpretar_dia, interpretar_horario


def executar() -> None:
    agenda = _agenda_de_exemplo()
    while True:
        _mostrar_menu()
        opcao = input("escolha: ")
        if opcao == "1":
            _criar_reserva(agenda)
        elif opcao == "2":
            _listar_reservas(agenda)
        elif opcao == "3":
            break
        else:
            print("opção inválida")


def _agenda_de_exemplo() -> Agenda:
    agenda = Agenda()
    agenda.registrar(Reserva("sala1", date(2026, 11, 1), time(10), time(11)))
    return agenda


def _mostrar_menu() -> None:
    print("")
    print("=== reserva de sala ===")
    print("1 - reservar")
    print("2 - listar")
    print("3 - sair")


def _criar_reserva(agenda: Agenda) -> None:
    try:
        agenda.registrar(_ler_reserva())
    except ErroReserva as erro:
        print(erro)
        return
    print("ok, reservado")


def _ler_reserva() -> Reserva:
    sala = input("sala: ")
    dia = interpretar_dia(input("dia (AAAA-MM-DD): "))
    inicio = interpretar_horario(input("inicio (HH:MM): "))
    fim = interpretar_horario(input("fim (HH:MM): "))
    return Reserva(sala, dia, inicio, fim)


def _listar_reservas(agenda: Agenda) -> None:
    reservas = agenda.listar()
    if not reservas:
        print("nada")
        return
    for reserva in reservas:
        print(f"{reserva.sala} {reserva.dia} {reserva.inicio:%H:%M} - {reserva.fim:%H:%M}")
