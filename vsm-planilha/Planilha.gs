/**
 * Integração com o Google Sheets: menu, criação do modelo e escrita dos resultados.
 */

const ABA_PARAMETROS = 'Parâmetros';
const ABA_PROCESSOS = 'Processos';
const ABA_RESULTADOS = 'Resultados';
const ABA_FORMULAS = 'Fórmulas';

// Ordem fixa das linhas da aba Parâmetros (a partir da linha 2).
const PARAMETROS = [
  ['demandaMensal', 'Demanda mensal', 18400, 'peças/mês'],
  ['diasUteis', 'Dias úteis no mês', 20, 'dias'],
  ['turnos', 'Turnos por dia', 2, 'turnos'],
  ['horasTurno', 'Horas por turno', 8, 'h'],
  ['pausasMin', 'Pausas por turno', 20, 'min'],
  ['estoqueProdutoAcabado', 'Estoque de produto acabado', 4140, 'peças']
];

const CABECALHO_PROCESSOS = [
  'Processo', 'Tempo de ciclo TC (s)', 'Setup TR (min)', 'Disponibilidade',
  'Operadores', 'Estoque antes do processo (peças)', 'Agrega valor? (S/N)'
];

// Exemplo clássico "Acme Stamping" (Rother & Shook, Aprendendo a Enxergar).
const PROCESSOS_EXEMPLO = [
  ['Estamparia', 1, 60, 0.85, 1, 4600, 'S'],
  ['Solda 1', 39, 10, 1, 1, 7000, 'S'],
  ['Solda 2', 46, 10, 0.8, 1, 1700, 'S'],
  ['Montagem 1', 62, 0, 1, 1, 2450, 'S'],
  ['Montagem 2', 40, 0, 1, 1, 1840, 'S']
];

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('VSM')
    .addItem('Calcular', 'calcular')
    .addSeparator()
    .addItem('Criar modelo (com exemplo)', 'criarModelo')
    .addItem('Limpar processos', 'limparProcessos')
    .addToUi();
}

function criarModelo() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  if (ss.getSheetByName(ABA_PARAMETROS)) {
    const r = ui.alert('O modelo já existe. Recriar e apagar os dados atuais?', ui.ButtonSet.YES_NO);
    if (r !== ui.Button.YES) return;
  }

  const par = recriarAba(ss, ABA_PARAMETROS);
  par.getRange(1, 1, 1, 3).setValues([['Parâmetro', 'Valor', 'Unidade']]);
  par.getRange(2, 1, PARAMETROS.length, 3)
    .setValues(PARAMETROS.map(function (l) { return [l[1], l[2], l[3]]; }));
  par.getRange(2, 2, PARAMETROS.length, 1).setBackground('#fff8e1');
  formatarCabecalho(par, 3);
  par.autoResizeColumns(1, 3);

  const proc = recriarAba(ss, ABA_PROCESSOS);
  proc.getRange(1, 1, 1, CABECALHO_PROCESSOS.length).setValues([CABECALHO_PROCESSOS]);
  proc.getRange(2, 1, PROCESSOS_EXEMPLO.length, CABECALHO_PROCESSOS.length).setValues(PROCESSOS_EXEMPLO);
  proc.getRange('D2:D100').setNumberFormat('0%');
  proc.getRange('G2:G100').setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(['S', 'N']).build());
  proc.getRange(1, 1).setNote('Liste os processos na ordem do fluxo. O estoque de cada linha é o que fica ANTES daquele processo.');
  formatarCabecalho(proc, CABECALHO_PROCESSOS.length);
  proc.autoResizeColumns(1, CABECALHO_PROCESSOS.length);

  criarAbaFormulas(ss);
  recriarAba(ss, ABA_RESULTADOS);
  ss.setActiveSheet(par);
  calcular();
}

function limparProcessos() {
  const proc = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(ABA_PROCESSOS);
  if (proc && proc.getLastRow() > 1) {
    proc.getRange(2, 1, proc.getLastRow() - 1, CABECALHO_PROCESSOS.length).clearContent();
  }
}

function calcular() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss.getSheetByName(ABA_PARAMETROS) || !ss.getSheetByName(ABA_PROCESSOS)) {
    SpreadsheetApp.getUi().alert('Use primeiro o menu VSM > Criar modelo.');
    return;
  }
  let r;
  try {
    r = calcularVSM(lerParametros(ss), lerProcessos(ss));
  } catch (e) {
    SpreadsheetApp.getUi().alert('Erro no cálculo: ' + e.message);
    return;
  }
  escreverResultados(ss, r);
}

function lerParametros(ss) {
  const valores = ss.getSheetByName(ABA_PARAMETROS).getRange(2, 2, PARAMETROS.length, 1).getValues();
  const p = {};
  PARAMETROS.forEach(function (def, i) { p[def[0]] = Number(valores[i][0]) || 0; });
  return p;
}

function lerProcessos(ss) {
  const aba = ss.getSheetByName(ABA_PROCESSOS);
  if (aba.getLastRow() < 2) return [];
  return aba.getRange(2, 1, aba.getLastRow() - 1, CABECALHO_PROCESSOS.length).getValues()
    .filter(function (l) { return String(l[0]).trim() !== ''; })
    .map(function (l) {
      return {
        nome: String(l[0]).trim(),
        tc: Number(l[1]),
        tr: Number(l[2]) || 0,
        disponibilidade: l[3] === '' ? 1 : Number(l[3]),
        operadores: Number(l[4]) || 0,
        estoqueAntes: Number(l[5]) || 0,
        agregaValor: String(l[6]).trim().toUpperCase() !== 'N'
      };
    });
}

function escreverResultados(ss, r) {
  const aba = recriarAba(ss, ABA_RESULTADOS);

  const indicadores = [
    ['Indicador', 'Valor', 'Unidade'],
    ['Demanda diária', r.demandaDiaria, 'peças/dia'],
    ['Tempo disponível por dia', r.tempoDisponivelDia, 's/dia'],
    ['Takt time', r.takt, 's/peça'],
    ['Lead time de produção', r.leadTimeDias, 'dias'],
    ['Tempo de processamento (Σ TC)', r.tempoProcessamento, 's'],
    ['Tempo de valor agregado', r.tempoVA, 's'],
    ['Eficiência do ciclo (PCE)', r.pce, '%'],
    ['Operadores teóricos (Σ TC ÷ Takt)', r.operadoresTeoricos, 'operadores'],
    ['Operadores necessários (arredondado)', r.operadoresNecessarios, 'operadores'],
    ['Operadores atuais', r.operadoresAtuais, 'operadores'],
    ['Gargalo (maior TC)', r.gargalo + ' (' + r.gargaloTC + ' s)', '']
  ];
  aba.getRange(1, 1, indicadores.length, 3).setValues(indicadores);
  aba.getRange(2, 2, indicadores.length - 2, 1).setNumberFormat('#,##0.00');
  aba.getRange(8, 2).setNumberFormat('0.000%');
  formatarCabecalho(aba, 3);

  const inicio = indicadores.length + 2;
  const tabela = [['Processo', 'TC (s)', 'Takt (s)', 'TC efetivo (s)', 'Carga vs. Takt',
    'Espera antes (dias)', 'Capacidade (peças/dia)', 'Situação']];
  r.processos.forEach(function (l) {
    tabela.push([l.nome, l.tc, r.takt, l.tcEfetivo, l.cargaTakt, l.esperaDias, l.capacidadeDia,
      l.acimaDoTakt ? 'ACIMA DO TAKT' : 'OK']);
  });
  tabela.push(['Produto acabado', '', '', '', '', r.esperaPA, '', '']);
  aba.getRange(inicio, 1, tabela.length, tabela[0].length).setValues(tabela);
  aba.getRange(inicio, 1, 1, tabela[0].length)
    .setFontWeight('bold').setBackground('#1a73e8').setFontColor('#ffffff');
  aba.getRange(inicio + 1, 2, tabela.length - 1, 6).setNumberFormat('#,##0.00');
  aba.getRange(inicio + 1, 5, tabela.length - 1, 1).setNumberFormat('0%');
  r.processos.forEach(function (l, i) {
    aba.getRange(inicio + 1 + i, 8).setBackground(l.acimaDoTakt ? '#f4cccc' : '#d9ead3');
  });
  aba.autoResizeColumns(1, tabela[0].length);

  // Gráfico de balanceamento: TC por processo (barras) x Takt (linha).
  const n = r.processos.length;
  const grafico = aba.newChart()
    .asComboChart()
    .addRange(aba.getRange(inicio, 1, n + 1, 3))
    .setOption('title', 'Balanceamento: Tempo de ciclo x Takt time')
    .setOption('seriesType', 'bars')
    .setOption('series', { 1: { type: 'line', color: '#d93025' } })
    .setOption('vAxis', { title: 'segundos' })
    .setPosition(1, 5, 0, 0)
    .build();
  aba.insertChart(grafico);

  ss.setActiveSheet(aba);
}

function criarAbaFormulas(ss) {
  const aba = recriarAba(ss, ABA_FORMULAS);
  const linhas = [
    ['Indicador', 'Fórmula', 'Observação'],
    ['Demanda diária', 'Demanda mensal ÷ Dias úteis', ''],
    ['Tempo disponível', 'Turnos × (Horas do turno × 3600 − Pausas × 60)', 'Em segundos por dia'],
    ['Takt time', 'Tempo disponível ÷ Demanda diária', 'Ritmo que o cliente exige'],
    ['Espera no estoque', 'Estoque (peças) ÷ Demanda diária', 'Em dias'],
    ['Lead time', 'Σ esperas nos estoques (inclui produto acabado)', 'Em dias; os TCs são desprezíveis frente às esperas'],
    ['Tempo de valor agregado', 'Σ TC dos processos que agregam valor', 'Em segundos'],
    ['PCE', 'Tempo VA ÷ Lead time', 'Lead time convertido em segundos de tempo disponível'],
    ['Operadores', 'Σ TC ÷ Takt', 'Arredondar para cima'],
    ['TC efetivo', 'TC ÷ Disponibilidade', 'Mostra o impacto das paradas'],
    ['Capacidade', 'Tempo disponível × Disponibilidade ÷ TC', 'Peças por dia'],
    ['Gargalo', 'Processo com maior TC', 'Se TC > Takt, não atende a demanda']
  ];
  aba.getRange(1, 1, linhas.length, 3).setValues(linhas);
  formatarCabecalho(aba, 3);
  aba.autoResizeColumns(1, 3);
}

function recriarAba(ss, nome) {
  const existente = ss.getSheetByName(nome);
  if (existente) {
    existente.clear();
    existente.getCharts().forEach(function (c) { existente.removeChart(c); });
    return existente;
  }
  return ss.insertSheet(nome);
}

function formatarCabecalho(aba, colunas) {
  aba.getRange(1, 1, 1, colunas).setFontWeight('bold').setBackground('#1a73e8').setFontColor('#ffffff');
  aba.setFrozenRows(1);
}
