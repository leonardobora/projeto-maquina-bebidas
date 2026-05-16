# Projeto da Disciplina — Máquina de Venda de Bebidas

**Disciplina:** Introdução à Linguagem Python (Turma U) · PUCPR · Pós Lato Sensu IA & CD
**Canvas:** [Projeto da Disciplina · assignment 325433](https://pucpr.instructure.com/courses/67212/assignments/325433) · vale 10 pontos
**Prazo:** 24/05/2026 23:59 BRT (8 dias)
**Enunciado original:** [`../projeto-final-enunciados/Projeto-Maquina-de-Bebidas.pdf`](../projeto-final-enunciados/Projeto-Maquina-de-Bebidas.pdf)

> ⚠️ O PDF do enunciado está marcado como **"Atividade opcional"**. Confirmar com o professor se isso se aplica ao trabalho final (peso 10) ou se é texto legado do template. Se opcional de fato, a disciplina pode ter sido encerrada sem nota dependente deste entregável.

---

## Conceito escolhido

**Máquina de bebidas via terminal, com interface em ASCII art.**
Tela que redesenha a vending machine a cada frame: visor com mensagens, botões numerados, slot de pagamento, slot de troco. Estado da máquina sempre visível.

---

## Requisitos do enunciado (PDF)

### Obrigatórios

1. Loop interativo — cliente compra inserindo notas/moedas em reais.
2. Catálogo inicial fixo:

   | ID | Produto    | Valor   | Estoque |
   |----|------------|---------|---------|
   | 1  | Coca-cola  | R$ 3,75 | 2       |
   | 2  | Pepsi      | R$ 3,67 | 5       |
   | 3  | Monster    | R$ 9,96 | 1       |
   | 4  | Café       | R$ 1,25 | 100     |
   | 5  | Redbull    | R$ 13,99| 2       |

3. Validar código escolhido (existe? tem estoque?).
4. Validar pagamento (`>= valor`); pedir novamente se insuficiente.
5. Calcular troco com **menor volume de cédulas/moedas** (algoritmo guloso).
   - Exemplo do enunciado: produto R$ 3,67 · pago R$ 10,00 · troco R$ 6,33 → 1×R$5 + 1×R$1 + 1×20¢ + 1×10¢ + 3×1¢.
6. Após entregar troco, decrementar estoque.

### Desafios opcionais (item 7)

- **7a.** Modo administrador: CRUD de produtos em runtime.
- **7b.** Estoque finito de notas/moedas — se não dá pra montar o troco, **cancela a compra**.

---

## Arquitetura proposta

```
projeto-maquina-bebidas/
├── README.md              # este arquivo
├── maquina.py             # entry point: loop principal + render
├── catalogo.py            # produtos (dataclass + estado inicial)
├── caixa.py               # estoque de notas/moedas + algoritmo de troco
├── admin.py               # modo administrador (desafio 7a)
├── ui/
│   ├── ascii_art.py       # arte da máquina (frames)
│   └── render.py          # composição visor + estado
├── tests/
│   ├── test_troco.py      # casos do enunciado + edge cases
│   └── test_catalogo.py
└── DECLARACAO-IA.md       # bloco-padrão exigido pela CONSUN 274/2024
```

### Decisões técnicas a confirmar

- **Centavos como `int`** (não `float`) — evita erro de ponto flutuante no troco. R$ 3,75 → 375 internamente.
- **Dataclasses** para `Produto` e `Cedula`.
- **Sem dependências externas** — só stdlib (`os`, `sys`, `time`).
- **Limpar tela entre frames** com `os.system("cls")` (Windows). Considerar fallback Linux/Mac mesmo rodando só no Windows.
- **Testes com `unittest`** stdlib — sem pytest pra manter zero-deps.

---

## ASCII art — esboço do layout

```
╔══════════════════════════════════════╗
║   ┌──────────────────────────────┐   ║
║   │ ESCOLHA UMA BEBIDA           │   ║  ← visor
║   └──────────────────────────────┘   ║
║                                      ║
║   [1] Coca-cola      R$ 3,75   x2    ║
║   [2] Pepsi          R$ 3,67   x5    ║
║   [3] Monster        R$ 9,96   x1    ║
║   [4] Café           R$ 1,25   x100  ║
║   [5] Redbull        R$ 13,99  x2    ║
║                                      ║
║   ┌──────────────────────────────┐   ║
║   │           PUSH               │   ║
║   └──────────────────────────────┘   ║
║                                      ║
║   💰 [inserir]    🪙 [troco]         ║
╚══════════════════════════════════════╝
```

Frames adicionais previstos: "inserindo dinheiro", "calculando troco", "compra cancelada — sem troco disponível", "modo admin".

---

## Plano de execução

- [ ] Confirmar com Leo se "opcional" muda a prioridade
- [ ] `catalogo.py` + testes de seed
- [ ] `caixa.py` + algoritmo guloso + testes (inclui caso do enunciado)
- [ ] `ui/ascii_art.py` — frame principal + visor
- [ ] `maquina.py` — loop integrando tudo
- [ ] `admin.py` (desafio 7a) — se sobrar tempo
- [ ] Estoque de notas/moedas (desafio 7b)
- [ ] `DECLARACAO-IA.md` antes do PDF final
- [ ] Gerar PDF do README via Pandoc + Chrome headless ([WORKFLOW.md](../../../WORKFLOW.md))

---

## Política PUCPR de IA

Resolução CONSUN 274/2024: uso de IA deve ser **declarado**, não escondido. Bloco-padrão será adicionado em `DECLARACAO-IA.md` antes da submissão.
