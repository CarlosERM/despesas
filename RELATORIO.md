# Relatório: como o Clean Code afetou a qualidade do código

## 1. Contexto

O projeto (reserva de salas com verificação de conflitos de horário) foi criado
de propósito com más práticas, para então ser refatorado seguindo os princípios
de *Clean Code* de Robert C. Martin. O comportamento do programa foi preservado;
mudou apenas a qualidade do código.

**Antes:** 1 arquivo (`reserva.py`), 79 linhas.
**Depois:** `agenda.py` (domínio) + `cli.py` (interface) + `reserva.py` (entrada) + `test_agenda.py`.

## 2. Problemas identificados e princípios aplicados

| # | Problema no código original | Princípio violado | Solução na refatoração |
|---|------------------------------|-------------------|------------------------|
| 1 | Variáveis globais (`lista`, `lista2`, `x`) mutadas por qualquer função | Funções não devem mudar estado global (§2) | Estado vive na classe `Agenda`; funções recebem e retornam valores explícitos |
| 2 | `funcao1()` com 52 linhas: menu, leitura, validação, conflito e impressão misturados | Uma função deve fazer uma coisa só, num único nível de abstração (§2) | Funções pequenas (máx. 13 linhas): `_ler_reserva`, `_criar_reserva`, `Agenda.registrar`, `Reserva.conflita_com`… |
| 3 | Nomes `a`, `b`, `h1`, `ok`, `confere`, `funcao1` | Nomes devem revelar intenção (§1) | `reserva`, `inicio`, `fim`, `conflita_com()`, `interpretar_horario()` |
| 4 | Horários comparados como string (`"9:30" < "10:00"` é `True`!) e validados com o número mágico `len(h) != 5` | Abstração de dados (§5); sem números mágicos | Parse real com `datetime.strptime` + verificação de round-trip; comparações usam `datetime.time` |
| 5 | `try/except: pass` engolindo erros; flag `ok = 0/1` como código de retorno | Exceções em vez de códigos de retorno (§6) | `HorarioInvalidoError`, `ReservaInvalidaError`, `ConflitoDeReservaError`; a CLI captura na borda e mostra mensagens úteis |
| 6 | Função morta (`confere`), `import os` sem uso, código comentado, comentário redundante | Não comente código ruim — reescreva; sem ruído (§3) | Tudo removido; o código se explica sozinho |
| 7 | `print()` dentro da lógica de negócio | Separação domínio × apresentação (§5, SRP §8) | `agenda.py` é puro (sem I/O); único lugar que lê/escreve é `cli.py` |
| 8 | Zero testes — impossível mudar com segurança | Três leis do TDD / FIRST (§7) | 12 testes com `unittest` (stdlib), cobrindo todas as regras de negócio |

## 3. Antes vs. depois

**Antes** — regra de conflito escondida dentro da função gigante, sobre tuplas
anônimas e strings:

```python
ok = 1
for r in lista:
    if r[0] == s and r[1] == d:
        if r[2] < h2 and h1 < r[3]:
            ok = 0
# for r in lista:
#     if confere(r, (s, d, h1, h2)):
#         ok = 0
if ok == 0:
    print("conflito!")
```

**Depois** — a regra vira uma afirmação legível no domínio, e o erro carrega a explicação:

```python
@dataclass(frozen=True)
class Reserva:
    def conflita_com(self, outra):
        return (self.sala == outra.sala and self.dia == outra.dia
                and self.inicio < outra.fim and outra.inicio < self.fim)

class Agenda:
    def registrar(self, reserva):
        for existente in self._reservas:
            if reserva.conflita_com(existente):
                raise ConflitoDeReservaError(reserva, existente)
        self._reservas.append(reserva)
```

O usuário agora recebe `conflito: a sala sala1 já está ocupada das 10:00 às 11:00 de 2026-11-01`
em vez de um seco `conflito!`.

## 4. Métricas

| Métrica | Antes | Depois |
|---|---|---|
| Arquivos de produção | 1 (tudo misturado) | 3 com responsabilidades separadas |
| Maior função | **52 linhas** (`funcao1`) | **13 linhas** (`executar`) |
| Variáveis globais | 3 | 0 |
| Números mágicos | `len(h) != 5`, flags `0/1` | 0 (formatos nomeados: `%H:%M`, `%Y-%m-%d`) |
| Tratamento de erros | `except:` vazio + flags | 3 exceções específicas com mensagens contextuais |
| Código morto | função `confere`, `import os`, blocos comentados | 0 |
| Testes automatizados | **0** | **12** (`python3 -m unittest`) — todos passando |
| Regras de negócio cobertas por teste | nenhuma | todas: sobreposição, encostar na borda (11h), fim > início, salas/dias diferentes, formato HH:MM e AAAA-MM-DD |

## 5. Como a qualidade foi afetada

- **Legibilidade:** o código lê como um texto ("registrar → conflita_com →
  ConflitoDeReservaError") em vez de exigir decifrar índices de tupla (`r[2] < h2`).
- **Manutenibilidade (rigidez/fragilidade, §9):** mudar a regra de conflito é uma
  linha em `conflita_com`, sem medo de quebrar o menu — domínio e interface estão separados.
- **Testabilidade:** antes era impossível testar (`funcao1` consome `input()` para sempre);
  agora as regras são funções puras com 12 testes que rodam em 0,002 s.
- **Robustez:** a comparação por string aceitava entradas absurdas; o parse real
  rejeita `"9:30"` e `"2026-11-1"`, comportamento garantido por teste.
- **Reusabilidade (mobilidade, §9):** `agenda.py` pode ser plugado em uma API HTTP
  ou banco de dados sem tocar em nenhuma linha, pois não conhece o terminal.

## 6. Conclusão

O programa de antes *funcionava*; o de depois *funciona e comunica*. O Clean Code
não adicionou comportamento — subtraiu complexidade acidental: 3 globais viraram
1 objeto, a função de 52 linhas virou 9 funções pequenas, e a confiança que antes
só existia "na mão do autor" agora existe em forma de testes.
