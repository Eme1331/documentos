# Painel de Produção (Google Forms + Sheets + Looker Studio)

Transforma o quadro branco (Projeto × Liberação → Beneficiamento → Montagem → Pintura → Embalagem → Expedição) em:

- **2 formulários**: um para o **planejamento** e outro para o **apontamento** da produção;
- **1 planilha** que monta o quadro sozinha, com as mesmas cores do quadro físico;
- **1 tabela pronta** para o dashboard no **Looker Studio**.

Você não precisa criar formulário nem fórmula à mão: o script `Codigo.gs` faz tudo.

---

## Como funciona

```
Formulário "Planejamento de Projetos"  ──┐
  (uma vez por projeto: datas previstas) │
                                         ├──► Planilha ──► aba "Quadro"  (réplica do quadro branco)
Formulário "Apontamento de Produção"   ──┘             └─► aba "Base"    ──► Looker Studio (dashboard)
  (a cada início/fim de etapa)
```

| Aba | O que é | Mexer? |
|---|---|---|
| `Planejamento` | Respostas do formulário de planejamento (1 linha por envio) | Não, só pelo formulário |
| `Apontamentos` | Respostas do formulário de apontamento (1 linha por envio) | Não, só pelo formulário |
| `Dashboard` | Indicadores, gráficos e linha do tempo (Gantt), direto no Google Planilhas | Só leitura |
| `Quadro` | O quadro montado automaticamente: linha **Planejado** e linha **Realizado** | Só leitura |
| `Base` | Tabela plana (1 linha por projeto × etapa) para o Looker Studio | Só leitura |
| `Links` | Links e QR Codes dos formulários | Imprimir os QR Codes |
| `Dados do dashboard` | Tabelas que alimentam os gráficos | Não |

**Por que dois formulários?** O planejamento tem sempre as mesmas colunas (10 datas por projeto). Já a produção lança **um evento por vez** ("Montagem do 0181 começou hoje"). Guardar cada evento em uma linha é o que deixa o formulário curto e a planilha simples.

### Regras do quadro

- **Preto** = data planejada.
- **Azul** = realizado no prazo (≤ planejado).
- **Vermelho** = realizado com atraso (> planejado).
- **Fundo rosa** na linha Planejado = a data passou e ainda não há apontamento.
- **Etapa atual** = a etapa seguinte ao último apontamento.
- **Atraso (dias)** = o maior entre o atraso do último apontamento e o atraso da próxima data vencida.
- Liberação e Expedição têm uma data só. As outras etapas têm início e fim.
- **Correções:** envie o formulário de novo. Vale sempre o envio **mais recente**, tanto para replanejar um projeto quanto para corrigir um apontamento.
- A lista de projetos do formulário de apontamento se atualiza sozinha: entra quando o projeto é planejado e sai quando é expedido.

---

## Passo a passo da instalação (≈ 10 minutos)

1. No Google Drive: **Novo → Planilhas Google → Planilha em branco**. Dê um nome, ex.: *Painel de Produção*.
2. Na planilha: **Extensões → Apps Script**.
3. Apague o que estiver no editor, **cole todo o conteúdo de `Codigo.gs`** e clique em **Salvar** (💾).
4. Volte para a planilha e **recarregue a página (F5)**. Vai aparecer o menu **Painel de Produção**.
5. Clique em **Painel de Produção → 1. Configurar / mostrar links dos formulários**.
   - O Google vai pedir autorização. Clique em **Continuar**, escolha sua conta e, se aparecer *"O Google não verificou este app"*, clique em **Avançado → Acessar (não seguro)**. É normal: o script é seu e não foi publicado.
   - Rode o menu de novo depois de autorizar, se for preciso. Ele pode ser rodado quantas vezes quiser: reaproveita os formulários já criados e refaz só o que faltar (inclusive a aba `Links`).
6. (Opcional) **Painel de Produção → 2. Importar projetos do quadro atual**. Lança os projetos 0181, 0241 e 0045 com as datas da foto do quadro.
7. Abra a aba **Dashboard** para ver os indicadores e a aba **Links**:
   - Mande o link do **Planejamento** para quem libera os projetos (PCP).
   - Imprima os **QR Codes por etapa** e cole em cada posto. O link já abre com a etapa marcada, e o operador só escolhe o projeto, Início/Fim e a data.

> Os formulários ficam no seu Google Drive e podem ser editados à vontade (textos, cores, logo). **Não mude o título das perguntas**: é por ele que a planilha reconhece cada coluna.

A atualização é automática a cada resposta e também **todo dia às 6h** (para marcar como atrasado o que venceu). Se quiser forçar: **Painel de Produção → Atualizar quadro agora**.

---

## Dashboard no próprio Google Planilhas

A aba **`Dashboard`** é gerada pelo script e se atualiza a cada formulário enviado. Nada precisa ser montado à mão.

- **Indicadores:** em aberto · ⚠ atrasados · ✓ no prazo (% em dia) · expedidos · maior atraso (e qual projeto).
- **Gráficos:**
  - projetos em aberto por etapa atual (onde está a fila);
  - duração média por etapa, previsto × real (mostra o gargalo; aparece quando as etapas começam a terminar);
  - atraso por projeto em aberto, do maior para o menor.
- **Linha do tempo (Gantt):** para cada projeto, uma linha *Previsto* (cor clara) e outra *Real* (cor forte). Cada etapa tem sempre a mesma cor e a letra inicial marca onde ela começa. A coluna vermelha é **hoje**. Uma etapa começada e não terminada vai até hoje, então dá para ver na hora quem está parado.

**Para usar numa TV:** abra a aba `Dashboard` e use **Ver → Tela cheia**. Para compartilhar só leitura: **Compartilhar → Qualquer pessoa com o link → Leitor**.

## (Opcional) Dashboard no Looker Studio

1. Acesse <https://lookerstudio.google.com> → **Criar → Relatório**.
2. Conector **Planilhas Google** → escolha a planilha → aba **`Base`** → **Adicionar**.
3. Confira os tipos dos campos em **Recurso → Gerenciar fontes de dados**: `Planejado` e `Realizado` como **Data**; `Atraso (dias)` e `Atraso do projeto (dias)` como **Número**.

Sugestão de páginas e gráficos:

| Gráfico | Dimensão | Métrica / filtro |
|---|---|---|
| Cartão de resumo: projetos em aberto | — | `Contagem distinta de Projeto`, filtro `Status do projeto` = No prazo ou Atrasado |
| Cartão de resumo: projetos atrasados | — | `Contagem distinta de Projeto`, filtro `Status do projeto` = Atrasado |
| Barras: projetos por etapa atual | `Etapa atual do projeto` | `Contagem distinta de Projeto` |
| Barras: atraso médio por etapa (gargalo) | `Etapa` | `Média de Atraso (dias)`, filtro `Situação` começa com "Realizado" |
| Tabela: situação dos projetos | `Projeto`, `Etapa atual do projeto`, `Status do projeto` | `Máx. de Atraso do projeto (dias)` |
| Tabela dinâmica: réplica do quadro | Linhas: `Projeto`; Colunas: `Ordem`, `Etapa`, `Evento` | `Planejado`, `Realizado` |
| Controle (filtro) | `Projeto`, `Status do projeto` | — |

Use cor condicional nas tabelas (`Situação` = "Realizado com atraso" / "Pendente atrasado" em vermelho). Para mostrar numa TV da fábrica, use **Compartilhar → Programar** ou deixe o relatório aberto no modo **Visualizar**. Os dados do Looker Studio se atualizam a cada 15 minutos, ou na hora com **Atualizar dados**.

---

## Dúvidas comuns

- **Apareceu "181" em vez de "0181".** Sem problema: o script completa os zeros à esquerda.
- **Lancei a data errada.** Envie o apontamento de novo com a data certa.
- **O plano mudou.** Envie o Planejamento de novo com o mesmo número de projeto.
- **Quero outra etapa ou mudar nomes.** Edite as constantes `ETAPAS` e `DUPLAS` no início do script **antes** de rodar o "Configurar".
- **Quero reinstalar do zero.** Crie uma planilha nova e repita o passo a passo. A configuração fica gravada em cada planilha.
