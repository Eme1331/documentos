// Executar: node vsm-planilha/tests/calculos.test.js
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const ctx = {};
vm.createContext(ctx);
['Calculos.gs', 'Funcoes.gs'].forEach(f =>
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', f), 'utf8'), ctx));

const perto = (a, b, tol = 0.01) => assert.ok(Math.abs(a - b) <= tol, `${a} != ${b}`);

// Exemplo Acme Stamping (Aprendendo a Enxergar): takt 60 s, LT 23,6 dias, VA 188 s.
const r = ctx.calcularVSM(
  { demandaMensal: 18400, diasUteis: 20, turnos: 2, horasTurno: 8, pausasMin: 20, estoqueProdutoAcabado: 4140 },
  [
    { nome: 'Estamparia', tc: 1, disponibilidade: 0.85, operadores: 1, estoqueAntes: 4600, agregaValor: true },
    { nome: 'Solda 1', tc: 39, disponibilidade: 1, operadores: 1, estoqueAntes: 7000, agregaValor: true },
    { nome: 'Solda 2', tc: 46, disponibilidade: 80, operadores: 1, estoqueAntes: 1700, agregaValor: true },
    { nome: 'Montagem 1', tc: 62, disponibilidade: 1, operadores: 1, estoqueAntes: 2450, agregaValor: true },
    { nome: 'Montagem 2', tc: 40, disponibilidade: 1, operadores: 1, estoqueAntes: 1840, agregaValor: true }
  ]);

perto(r.demandaDiaria, 920);
perto(r.tempoDisponivelDia, 55200);
perto(r.takt, 60);
perto(r.leadTimeDias, 23.62);
assert.strictEqual(r.tempoVA, 188);
assert.strictEqual(r.operadoresNecessarios, 4);
assert.strictEqual(r.gargalo, 'Montagem 1');
assert.ok(r.processos[3].acimaDoTakt);
perto(r.processos[2].tcEfetivo, 57.5);
perto(r.pce, 188 / (23.62 * 55200 + 188), 1e-6);

perto(ctx.VSM_TAKT(55200, 920), 60);
perto(ctx.VSM_TEMPO_DISPONIVEL(2, 8, 20), 55200);
perto(ctx.VSM_LEAD_TIME([[4600], [7000], [1700], [2450], [1840], [4140]], 920), 23.62);
assert.strictEqual(ctx.VSM_OPERADORES([[1], [39], [46], [62], [40]], 60), 4);

assert.throws(() => ctx.calcularVSM({ demandaMensal: 0, diasUteis: 20, turnos: 1, horasTurno: 8 }, [{ nome: 'x', tc: 1 }]));

console.log('OK: todos os testes passaram');

// Estudo de caso Thundercats Painéis (família Lion). Puncionadeira e Dobradeira rodam 2 turnos.
const t = ctx.calcularVSM(
  { demandaMensal: 170, diasUteis: 20, turnos: 1, horasTurno: 8.8, pausasMin: 0, estoqueProdutoAcabado: 10 },
  [
    { nome: 'Puncionadeira', tc: 4080, disponibilidade: 0.75, operadores: 1, turnos: 2, estoqueAntes: 35, agregaValor: true },
    { nome: 'Dobradeira', tc: 3812, disponibilidade: 0.62, operadores: 1, turnos: 2, estoqueAntes: 13, agregaValor: true },
    { nome: 'Pré Montagem', tc: 822, operadores: 1, estoqueAntes: 30, agregaValor: true },
    { nome: 'Montagem', tc: 850, operadores: 1, estoqueAntes: 25, agregaValor: true }
  ]);
perto(t.demandaDiaria, 8.5);
perto(t.takt, 3727.06);
perto(t.leadTimeDias, 13.294);
assert.strictEqual(t.tempoProcessamento, 9564);
assert.strictEqual(t.operadoresNecessarios, 3);
assert.strictEqual(t.gargalo, 'Dobradeira');
perto(t.processos[1].capacidadeDia, 10.30);
perto(t.processos[1].carga, 0.825);
assert.ok(t.processos[1].acimaDoTakt && !t.processos[1].naoAtende);

console.log('OK: caso Thundercats');
