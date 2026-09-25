# Planilha de cálculos de VSM (Google Sheets + Apps Script)

Calculadora de Mapeamento de Fluxo de Valor: takt time, lead time, tempo de valor agregado,
PCE, número de operadores, gargalo e gráfico de balanceamento.

## Instalação (5 minutos)

1. Crie uma planilha nova no Google Sheets.
2. Menu **Extensões > Apps Script**.
3. Crie três arquivos de script e cole o conteúdo de `Calculos.gs`, `Planilha.gs` e `Funcoes.gs`.
4. Salve, volte para a planilha e recarregue a página.
5. Menu **VSM > Criar modelo (com exemplo)** (na primeira vez o Google pede autorização).

## Uso

- **Parâmetros**: demanda, dias úteis, turnos, horas, pausas e estoque de produto acabado.
- **Processos**: um processo por linha, na ordem do fluxo. O estoque é o que fica *antes* do processo.
  Use a coluna **Turnos** quando um processo trabalha em mais turnos que a planta
  (o takt continua calculado com os turnos da planta; a carga usa os turnos do processo).
  Na coluna **Disponibilidade** pode entrar o OEE.
- Menu **VSM > Calcular** gera a aba **Resultados** com os indicadores, a tabela por processo e o gráfico.
- A aba **Fórmulas** resume cada cálculo, para estudo.

O exemplo que vem carregado é o caso Acme Stamping (*Aprendendo a Enxergar*): takt 60 s,
lead time 23,6 dias, VA 188 s, 4 operadores, gargalo Montagem 1 (62 s).

## Funções para usar nas células

| Função | Exemplo |
|---|---|
| `VSM_TEMPO_DISPONIVEL(turnos; horas; pausas_min)` | `=VSM_TEMPO_DISPONIVEL(2; 8; 20)` → 55200 |
| `VSM_TAKT(tempo_disp_s; demanda_diaria)` | `=VSM_TAKT(55200; 920)` → 60 |
| `VSM_LEAD_TIME(faixa_estoques; demanda_diaria)` | `=VSM_LEAD_TIME(F2:F7; 920)` → dias |
| `VSM_PCE(va_s; lead_time_dias; tempo_disp_s)` | formate como % |
| `VSM_OPERADORES(faixa_TCs; takt)` | `=VSM_OPERADORES(B2:B6; 60)` → 4 |

## Situação por processo

- **OK**: TC efetivo (TC ÷ OEE) cabe no takt.
- **OK SÓ COM TURNO EXTRA**: passa do takt, mas os turnos extras dão conta da demanda.
- **NÃO ATENDE A DEMANDA**: carga acima de 100%.

## Convenções

- O PCE converte o lead time para segundos usando o **tempo disponível** por dia (não 24 h).
  Se a prova usar outra convenção, confira o enunciado.
- A disponibilidade aceita `85%`, `0,85` ou `85`.

## Testes

```
node tests/calculos.test.js
```
