/**
 * Cálculos de Mapeamento de Fluxo de Valor (VSM).
 * Funções puras: não acessam a planilha, então podem ser testadas fora do Google.
 */

/**
 * Converte disponibilidade para fração: aceita 0,85 ou 85.
 */
function normalizarPercentual(valor) {
  const n = Number(valor);
  return n > 1 ? n / 100 : n;
}

/**
 * Calcula todos os indicadores do VSM.
 *
 * @param {Object} p Parâmetros: demandaMensal, diasUteis, turnos, horasTurno,
 *   pausasMin, estoqueProdutoAcabado.
 * @param {Array<Object>} processos Lista com: nome, tc (s), tr (min),
 *   disponibilidade, operadores, estoqueAntes (peças), agregaValor (bool).
 */
function calcularVSM(p, processos) {
  const obrigatorios = ['demandaMensal', 'diasUteis', 'turnos', 'horasTurno'];
  obrigatorios.forEach(function (k) {
    if (!(Number(p[k]) > 0)) throw new Error('Parâmetro inválido: ' + k + ' deve ser maior que zero.');
  });
  if (!processos.length) throw new Error('Cadastre pelo menos um processo.');

  const demandaDiaria = p.demandaMensal / p.diasUteis;
  const tempoDisponivelDia = p.turnos * (p.horasTurno * 3600 - (p.pausasMin || 0) * 60);
  if (!(tempoDisponivelDia > 0)) throw new Error('Pausas maiores que o turno: tempo disponível ficou zero ou negativo.');
  const takt = tempoDisponivelDia / demandaDiaria;

  let somaTC = 0;
  let tempoVA = 0;
  let operadoresAtuais = 0;
  let gargalo = null;

  const linhas = processos.map(function (proc) {
    if (!(proc.tc > 0)) throw new Error('Tempo de ciclo inválido no processo "' + proc.nome + '".');
    const disp = proc.disponibilidade ? normalizarPercentual(proc.disponibilidade) : 1;
    const esperaDias = (proc.estoqueAntes || 0) / demandaDiaria;
    somaTC += proc.tc;
    if (proc.agregaValor) tempoVA += proc.tc;
    operadoresAtuais += proc.operadores || 0;
    if (!gargalo || proc.tc > gargalo.tc) gargalo = proc;
    return {
      nome: proc.nome,
      tc: proc.tc,
      tcEfetivo: proc.tc / disp,
      esperaDias: esperaDias,
      cargaTakt: proc.tc / takt,
      capacidadeDia: (tempoDisponivelDia * disp) / proc.tc,
      acimaDoTakt: proc.tc > takt
    };
  });

  const esperaPA = (p.estoqueProdutoAcabado || 0) / demandaDiaria;
  const leadTimeDias = linhas.reduce(function (s, l) { return s + l.esperaDias; }, 0) + esperaPA;
  const leadTimeSeg = leadTimeDias * tempoDisponivelDia + somaTC;
  const operadoresTeoricos = somaTC / takt;

  return {
    demandaDiaria: demandaDiaria,
    tempoDisponivelDia: tempoDisponivelDia,
    takt: takt,
    esperaPA: esperaPA,
    leadTimeDias: leadTimeDias,
    tempoProcessamento: somaTC,
    tempoVA: tempoVA,
    pce: tempoVA / leadTimeSeg,
    operadoresTeoricos: operadoresTeoricos,
    operadoresNecessarios: Math.ceil(operadoresTeoricos - 1e-9),
    operadoresAtuais: operadoresAtuais,
    gargalo: gargalo.nome,
    gargaloTC: gargalo.tc,
    processos: linhas
  };
}
