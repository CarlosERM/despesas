"""Domínio do sistema de reserva de salas.

Camada pura de regras de negócio: sem entrada, saída ou qualquer
detalhe de interface com o usuário.
"""

from dataclasses import dataclass
from datetime import date, datetime, time


class ErroReserva(ValueError):
    """Erro base para violações das regras de reserva."""


class HorarioInvalidoError(ErroReserva):
    """Horário ou dia fora do formato esperado."""


class ReservaInvalidaError(ErroReserva):
    """Reserva cujo término não é posterior ao início."""


class ConflitoDeReservaError(ErroReserva):
    """A sala já está reservada em horário sobreposto no mesmo dia."""

    def __init__(self, reserva: "Reserva", conflito: "Reserva") -> None:
        super().__init__(
            f"conflito: a sala {conflito.sala} já está ocupada das "
            f"{conflito.inicio:%H:%M} às {conflito.fim:%H:%M} de {conflito.dia}"
        )
        self.reserva = reserva
        self.conflito = conflito


def interpretar_horario(texto: str) -> time:
    return _interpretar(texto, "%H:%M", "horário", "HH:MM").time()


def interpretar_dia(texto: str) -> date:
    return _interpretar(texto, "%Y-%m-%d", "dia", "AAAA-MM-DD").date()


def _interpretar(texto: str, formato: str, nome: str, exemplo: str):
    try:
        interpretado = datetime.strptime(texto, formato)
    except ValueError as erro:
        raise HorarioInvalidoError(
            f"{nome} inválido: {texto!r} (use {exemplo})"
        ) from erro
    if interpretado.strftime(formato) != texto:
        raise HorarioInvalidoError(
            f"{nome} inválido: {texto!r} (use {exemplo})"
        )
    return interpretado


@dataclass(frozen=True)
class Reserva:
    sala: str
    dia: date
    inicio: time
    fim: time

    def __post_init__(self) -> None:
        if self.fim <= self.inicio:
            raise ReservaInvalidaError(
                f"o término ({self.fim:%H:%M}) deve ser posterior "
                f"ao início ({self.inicio:%H:%M})"
            )

    def conflita_com(self, outra: "Reserva") -> bool:
        return (
            self.sala == outra.sala
            and self.dia == outra.dia
            and self.inicio < outra.fim
            and outra.inicio < self.fim
        )


class Agenda:
    """Catálogo de reservas com verificação de conflitos."""

    def __init__(self) -> None:
        self._reservas = []

    def registrar(self, reserva: Reserva) -> None:
        for existente in self._reservas:
            if reserva.conflita_com(existente):
                raise ConflitoDeReservaError(reserva, existente)
        self._reservas.append(reserva)

    def listar(self) -> list[Reserva]:
        return list(self._reservas)
