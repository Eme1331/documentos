/**
 * Funções personalizadas para usar direto nas células, ex.: =VSM_TAKT(55200; 920)
 */

/**
 * Takt time em segundos.
 * @param {number} tempoDisponivelSeg Tempo disponível por dia (s).
 * @param {number} demandaDiaria Demanda diária (peças).
 * @customfunction
 */
function VSM_TAKT(tempoDisponivelSeg, demandaDiaria) {
  return tempoDisponivelSeg / demandaDiaria;
}

/**
 * Tempo disponível por dia em segundos.
 * @param {number} turnos Turnos por dia.
 * @param {number} horasTurno Horas por turno.
 * @param {number} pausasMin Pausas por turno (min).
 * @customfunction
 */
function VSM_TEMPO_DISPONIVEL(turnos, horasTurno, pausasMin) {
  return turnos * (horasTurno * 3600 - (pausasMin || 0) * 60);
}

/**
 * Lead time em dias a partir de uma faixa de estoques (peças).
 * @param {number[][]} estoques Faixa com os estoques.
 * @param {number} demandaDiaria Demanda diária (peças).
 * @customfunction
 */
function VSM_LEAD_TIME(estoques, demandaDiaria) {
  const lista = Array.isArray(estoques) ? [].concat.apply([], estoques) : [estoques];
  return lista.reduce(function (s, e) { return s + (Number(e) || 0); }, 0) / demandaDiaria;
}

/**
 * Eficiência do ciclo (fração; formate como %).
 * @param {number} tempoVASeg Tempo de valor agregado (s).
 * @param {number} leadTimeDias Lead time (dias).
 * @param {number} tempoDisponivelSeg Tempo disponível por dia (s).
 * @customfunction
 */
function VSM_PCE(tempoVASeg, leadTimeDias, tempoDisponivelSeg) {
  return tempoVASeg / (leadTimeDias * tempoDisponivelSeg + tempoVASeg);
}

/**
 * Número de operadores necessários (arredondado para cima).
 * @param {number[][]} temposCiclo Faixa com os TCs (s).
 * @param {number} takt Takt time (s).
 * @customfunction
 */
function VSM_OPERADORES(temposCiclo, takt) {
  const lista = Array.isArray(temposCiclo) ? [].concat.apply([], temposCiclo) : [temposCiclo];
  const soma = lista.reduce(function (s, t) { return s + (Number(t) || 0); }, 0);
  return Math.ceil(soma / takt - 1e-9);
}
