# UNIDADE 3 – Teste Estrutural de Software (Fluxo de Dados – Def–Use)

## 1) Código testado
```python
def processar(nums):
    """
    Processa uma lista de inteiros até encontrar 0 (sentinela) ou o fim.
    Calcula soma dos positivos, contagem de positivos/negativos, máximo,
    média dos positivos e um fatorial truncado em 5! baseado na contagem de positivos.
    Retorna também o índice onde o laço parou.
    """
    total = 0            # D(t0)
    qtd_pos = 0          # D(cp0)
    qtd_neg = 0          # D(cn0)
    max_val = None       # D(m0)
    i = 0                # D(i0)

    # Laço 1: percorre até achar 0 (sentinela) ou o fim
    while i < len(nums):                     # U(i) (p-uso)
        x = nums[i]                          # D(x0)
        if x == 0:                           # U(x) (p-uso)
            break
        if x > 0:                            # U(x) (p-uso)
            total += x                       # U(total), U(x) (c-uso) -> D(t+)
            qtd_pos += 1                     # U(cp), D(cp+)
            if max_val is None or x > max_val:   # U(max_val) (p-uso), U(x) (p-uso)
                max_val = x                  # D(m+)
        else:
            qtd_neg += 1                     # U(cn), D(cn+)
        i += 1                               # U(i), D(i+)

    # Laço 2: fatorial truncado em 5!
    fat = 1
    for k in range(1, min(qtd_pos, 5) + 1):  # U(qtd_pos) (p-uso)
        fat *= k

    media = total / qtd_pos if qtd_pos > 0 else 0  # U(total) (c-uso), U(qtd_pos) (p-uso)
    return {
        "total": total,
        "qtd_pos": qtd_pos,
        "qtd_neg": qtd_neg,
        "max": max_val,
        "media": media,
        "fat": fat,
        "stopped_at": i,
    }
```

## 2) Conjuntos de elementos requeridos (Def–Use)
### Mapeamento Def–Use (DU) considerado

- **i**
  - DU1: D(i0) → U(i) em `while i < len(nums)`
  - DU2: D(i+) → U(i) na iteração seguinte do `while`

- **x**
  - DU3: D(x0) → U(x) em `x == 0` (p-uso)
  - DU4: D(x0) → U(x) em `x > 0` (p-uso)
  - DU5: D(x0) → U(x) em `total += x` (c-uso)

- **total**
  - DU6: D(t0=0) → U(total) no cálculo da `media` quando `qtd_pos == 0`
  - DU7: D(t0) → U(total) na primeira ocorrência de `total += x`
  - DU8: D(t+) (última do laço) → U(total) no cálculo da `media` (`qtd_pos > 0`)

- **qtd_pos**
  - DU9:  D(cp0=0) → U(qtd_pos) no predicado `qtd_pos > 0` (ramo falso)
  - DU10: D(cp0=0) → U(qtd_pos) em `min(qtd_pos,5)` (laço 2 não executa)
  - DU11: D(cp+)   → U(qtd_pos) em `min(qtd_pos,5)` (laço 2 executa)
  - DU12: D(cp+)   → U(qtd_pos) no predicado `qtd_pos > 0` (ramo verdadeiro)

- **qtd_neg**
  - DU13: D(cn0=0) → uso no retorno
  - DU14: D(cn+)   → uso no retorno

- **max_val**
  - DU15: D(m0=None) → U(max_val) em `max_val is None`
  - DU16: D(m+) → U(max_val) em `x > max_val`
  - DU17: D(m+) → uso no retorno

**Total de elementos (DU) considerados:** 17

## 3) Casos de Teste (plano)
Formato: **CT – Elemento (DU) – Entrada – Esperado – Caminho – Resultado**

**CT1** – DU1, DU6, DU9, DU10, DU13 – Entrada `[]` – Esperado `{"total":0,"qtd_pos":0,"qtd_neg":0,"max":None,"media":0,"fat":1,"stopped_at":0}` – Caminho: `while` não entra; laço 2 não executa; `qtd_pos>0` falso – Resultado: OK.

**CT2** – DU1, DU2, DU3, DU4, DU5, DU7, DU8, DU11, DU12, DU15, DU16, DU13, DU17 – Entrada `[3,2,1]` – Esperado `{"total":6,"qtd_pos":3,"qtd_neg":0,"max":3,"media":2.0,"fat":6,"stopped_at":3}` – Caminho: todos positivos; `max_val` inicializado no primeiro; laço 2 executa (1..3); `qtd_pos>0` verdadeiro – Resultado: OK.

**CT3** – DU1, DU2, DU3(T), DU9, DU10, DU13, DU14 – Entrada `[-5,-2,0]` – Esperado `{"total":0,"qtd_pos":0,"qtd_neg":2,"max":None,"media":0,"fat":1,"stopped_at":2}` – Caminho: negativos até `0` (break); laço 2 não executa; `qtd_pos>0` falso – Resultado: OK.

**CT4** – DU1, DU2, DU3(F), DU4, DU5, DU7, DU8, DU11, DU12, DU14, DU15, DU16(T), DU17 – Entrada `[-1,4,-2,6]` – Esperado `{"total":10,"qtd_pos":2,"qtd_neg":2,"max":6,"media":5.0,"fat":2,"stopped_at":4}` – Caminho: alterna negativos/positivos; atualização de máximo verdadeira no 6; laço 2 executa (1..2) – Resultado: OK.

**CT5** – DU1, DU3(T), DU6, DU9, DU10, DU13 – Entrada `[0]` – Esperado `{"total":0,"qtd_pos":0,"qtd_neg":0,"max":None,"media":0,"fat":1,"stopped_at":0}` – Caminho: break imediato; laço 2 não executa; `qtd_pos>0` falso – Resultado: OK.

**CT6** – DU2, DU4, DU5, DU7, DU8, DU11, DU12, DU15, DU16, DU17 – Entrada `[1,2,3,4,5,6]` – Esperado `{"total":21,"qtd_pos":6,"qtd_neg":0,"max":6,"media":3.5,"fat":120,"stopped_at":6}` – Caminho: todos positivos; laço 2 truncado em 5! – Resultado: OK.

## 4) Cobertura
- **DUs mapeados:** 17
- **Cobertos:** 17
- **Cobertura:** **100%**

## 5) Observações
- O mapeamento DU foi definido para fins didáticos e corresponde aos pontos críticos do fluxo de dados do programa.
- Em contexto industrial, recomenda-se instrumentação e/ou ferramentas para validar dinamicamente a cobertura de DUs.
