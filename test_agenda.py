import unittest
from datetime import date, time

from agenda import (
    Agenda,
    ConflitoDeReservaError,
    HorarioInvalidoError,
    Reserva,
    ReservaInvalidaError,
    interpretar_dia,
    interpretar_horario,
)

DIA = date(2026, 11, 1)


def nova_reserva(inicio: time, fim: time, sala: str = "sala1", dia: date = DIA) -> Reserva:
    return Reserva(sala=sala, dia=dia, inicio=inicio, fim=fim)


class TestConflitoDeHorarios(unittest.TestCase):
    def setUp(self):
        self.agenda = Agenda()
        self.agenda.registrar(nova_reserva(time(10), time(11)))

    def test_horario_sobreposto_conflita(self):
        with self.assertRaises(ConflitoDeReservaError):
            self.agenda.registrar(nova_reserva(time(10, 30), time(11, 30)))

    def test_reserva_que_comeca_no_fim_da_anterior_nao_conflita(self):
        self.agenda.registrar(nova_reserva(time(11), time(12)))

    def test_reserva_que_termina_no_inicio_da_anterior_nao_conflita(self):
        self.agenda.registrar(nova_reserva(time(9), time(10)))

    def test_salas_diferentes_nao_conflitam(self):
        self.agenda.registrar(nova_reserva(time(10, 30), time(11, 30), sala="sala2"))

    def test_dias_diferentes_nao_conflitam(self):
        self.agenda.registrar(nova_reserva(time(10, 30), time(11, 30), dia=date(2026, 11, 2)))

    def test_reservas_registradas_aparecem_na_lista(self):
        self.agenda.registrar(nova_reserva(time(11), time(12)))
        self.assertEqual(len(self.agenda.listar()), 2)


class TestValidacaoDeReserva(unittest.TestCase):
    def test_fim_igual_ao_inicio_e_invalido(self):
        with self.assertRaises(ReservaInvalidaError):
            nova_reserva(time(10), time(10))

    def test_fim_antes_do_inicio_e_invalido(self):
        with self.assertRaises(ReservaInvalidaError):
            nova_reserva(time(12), time(11))


class TestInterpretacaoDeEntradas(unittest.TestCase):
    def test_horario_valido(self):
        self.assertEqual(interpretar_horario("09:30"), time(9, 30))

    def test_horario_sem_zero_a_esquerda_e_invalido(self):
        with self.assertRaises(HorarioInvalidoError):
            interpretar_horario("9:30")

    def test_dia_valido(self):
        self.assertEqual(interpretar_dia("2026-11-01"), date(2026, 11, 1))

    def test_dia_fora_do_formato_e_invalido(self):
        with self.assertRaises(HorarioInvalidoError):
            interpretar_dia("2026-11-1")


if __name__ == "__main__":
    unittest.main()
