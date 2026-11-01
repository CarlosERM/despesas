# reserva de sala

Sistema simples de reserva de salas com verificação de conflito de horário.
O projeto começou como um exemplo intencionalmente mal escrito e foi refatorado
com princípios de Clean Code — veja o `RELATORIO.md` para a análise completa.

## regras

- mesma sala no mesmo dia não pode ter horários sobrepostos
- 10:00–11:00 bloqueia 10:30–11:30, mas permite começar às 11:00
- o término deve ser posterior ao início

## como rodar

```
python3 reserva.py
```

## como testar

```
python3 -m unittest
```

## estrutura

| arquivo | responsabilidade |
|---|---|
| `agenda.py` | domínio: `Reserva`, `Agenda`, regras e exceções (sem I/O) |
| `cli.py` | interface de linha de comando (único lugar com input/print) |
| `reserva.py` | ponto de entrada |
| `test_agenda.py` | testes das regras de negócio |
