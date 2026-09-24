/**
 * PAINEL DE PRODUÇÃO — Quadro de projetos (Google Forms + Google Sheets)
 *
 * Como usar (detalhes no README.md):
 *   1. Crie uma planilha em branco no Google Sheets.
 *   2. Extensões > Apps Script, apague o conteúdo e cole este arquivo. Salve.
 *   3. Recarregue a planilha. Aparecerá o menu "Painel de Produção".
 *   4. Painel de Produção > 1. Configurar (criar formulários).
 *   5. (Opcional) Painel de Produção > 2. Importar projetos do quadro atual.
 */

// ---------------------------------------------------------------------------
// Configuração
// ---------------------------------------------------------------------------

const VERSAO = '3 (com Dashboard)';

const ABA_PLAN = 'Planejamento';
const ABA_APONT = 'Apontamentos';
const ABA_QUADRO = 'Quadro';
const ABA_BASE = 'Base';
const ABA_LINKS = 'Links';
const ABA_DASH = 'Dashboard';
const ABA_DADOS_DASH = 'Dados do dashboard';

const ETAPAS = ['Liberação', 'Beneficiamento', 'Montagem', 'Pintura', 'Embalagem', 'Expedição'];
// Etapas com início e fim. As demais têm uma data só.
const DUPLAS = { Beneficiamento: true, Montagem: true, Pintura: true, Embalagem: true };

// Títulos das perguntas. As colunas das abas de respostas têm esses mesmos nomes.
const TIT_NUM = 'Nº do projeto';
const TIT_NOME = 'Nome do projeto';
const TIT_PROJETO = 'Projeto';
const TIT_ETAPA = 'Etapa';
const TIT_EVENTO = 'Evento';
const TIT_DATA = 'Data';
const TIT_RESP = 'Responsável';
const TIT_OBS = 'Observação';

// Cores do quadro
const COR_GRADE = '#e06666';
const COR_PLAN = '#202124';
const COR_REAL_OK = '#1a56db';
const COR_REAL_ATRASO = '#d93025';
const FUNDO_PENDENTE_ATRASADO = '#fde2e1';
const FUNDO_CABECALHO = '#f8f9fa';
const BRANCO = '#ffffff';

// Dashboard: uma cor fixa por etapa (sempre na mesma ordem) e cores de status.
const CORES_ETAPA = {
  'Liberação': '#2a78d6',
  'Beneficiamento': '#eb6834',
  'Montagem': '#1baf7a',
  'Pintura': '#eda100',
  'Embalagem': '#e87ba4',
  'Expedição': '#008300',
};
const COR_STATUS_OK = '#0ca30c';
const COR_STATUS_CRITICO = '#d03b3b';
const COR_TEXTO = '#0b0b0b';
const COR_TEXTO_2 = '#52514e';
const COR_SUPERFICIE = '#fcfcfb';

// Marcos = colunas de datas do quadro, na ordem.
const MARCOS = (function () {
  const m = [];
  ETAPAS.forEach(function (e) {
    if (DUPLAS[e]) {
      m.push({ etapa: e, evento: 'Início' });
      m.push({ etapa: e, evento: 'Fim' });
    } else {
      m.push({ etapa: e, evento: 'Data' });
    }
  });
  return m;
})();

function tituloMarco_(m) {
  return m.evento === 'Data' ? m.etapa : m.etapa + ' – ' + m.evento.toLowerCase();
}

// ---------------------------------------------------------------------------
// Menu
// ---------------------------------------------------------------------------

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Painel de Produção')
    .addItem('1. Configurar / mostrar links dos formulários', 'configurar')
    .addItem('2. Importar projetos do quadro atual', 'importarQuadroAtual')
    .addSeparator()
    .addItem('Atualizar quadro e dashboard agora', 'atualizarAgora')
    .addSeparator()
    .addItem('Versão do script: ' + VERSAO, 'mostrarVersao')
    .addToUi();
}

function mostrarVersao() {
  SpreadsheetApp.getUi().alert('Versão do script: ' + VERSAO);
}

/** Pelo menu: mostra o erro numa janela, em vez de só um aviso rápido no topo da tela. */
function atualizarAgora() {
  const ui = SpreadsheetApp.getUi();
  try {
    atualizarTudo();
    const dash = SpreadsheetApp.getActive().getSheetByName(ABA_DASH);
    if (dash) SpreadsheetApp.getActive().setActiveSheet(dash);
    SpreadsheetApp.getActive().toast('Quadro e dashboard atualizados.', 'Painel de Produção', 5);
  } catch (e) {
    ui.alert('Erro ao atualizar', String(e && e.stack ? e.message + '\n\n' + e.stack : e) +
      '\n\nTire um print desta mensagem.', ui.ButtonSet.OK);
  }
}

// ---------------------------------------------------------------------------
// Configuração inicial
// ---------------------------------------------------------------------------

function configurar() {
  const ui = SpreadsheetApp.getUi();
  try {
    configurar_(ui);
  } catch (e) {
    ui.alert('Erro na configuração', String(e && e.message ? e.message : e) +
      '\n\nTire um print desta mensagem. Pode rodar o "1. Configurar" de novo: ele continua de onde parou.', ui.ButtonSet.OK);
  }
}

/**
 * Pode ser rodado várias vezes: reaproveita os formulários já ligados à planilha
 * e só refaz o que faltar (gatilhos, aba Links, quadro).
 */
function configurar_(ui) {
  const props = PropertiesService.getDocumentProperties();
  const ss = SpreadsheetApp.getActive();

  let formPlan = formDaAba_(ss, ABA_PLAN);
  if (!formPlan) {
    formPlan = criarFormPlanejamento_();
    formPlan.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
    renomearAbaDoForm_(ss, formPlan, ABA_PLAN);
  }
  let formApont = formDaAba_(SpreadsheetApp.getActive(), ABA_APONT);
  if (!formApont) {
    formApont = criarFormApontamento_();
    formApont.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
    renomearAbaDoForm_(ss, formApont, ABA_APONT);
  }
  const itemProjeto = itemPorTitulo_(formApont, TIT_PROJETO);
  const itemEtapa = itemPorTitulo_(formApont, TIT_ETAPA);

  props.setProperties({
    FORM_PLAN_ID: formPlan.getId(),
    FORM_APONT_ID: formApont.getId(),
    ITEM_PROJETO_ID: String(itemProjeto.getId()),
  });

  escreverLinks_(SpreadsheetApp.getActive(), formPlan, formApont, itemEtapa.getId());

  let avisoGatilho = '';
  try {
    ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
    ScriptApp.newTrigger('aoEnviarFormulario').forSpreadsheet(SpreadsheetApp.getActive()).onFormSubmit().create();
    // Atualiza todo dia de manhã para marcar como atrasado o que venceu.
    ScriptApp.newTrigger('atualizarTudo').timeBased().everyDays(1).atHour(6).create();
  } catch (e) {
    avisoGatilho = '\n\nATENÇÃO: não consegui criar a atualização automática (' + e.message + '). ' +
      'Até resolver, use "Atualizar quadro agora" depois de cada lançamento.';
  }

  atualizarTudo();
  removerAbasVazias_(SpreadsheetApp.getActive());
  const links = SpreadsheetApp.getActive().getSheetByName(ABA_LINKS);
  SpreadsheetApp.getActive().setActiveSheet(links);

  ui.alert(
    'Pronto!',
    'Formulários prontos (ficam no seu Google Drive):\n\n' +
      '• Planejamento de Projetos:\n' + formPlan.getPublishedUrl() + '\n\n' +
      '• Apontamento de Produção:\n' + formApont.getPublishedUrl() + '\n\n' +
      'Esses links e os QR Codes por etapa estão na aba "' + ABA_LINKS + '".\n' +
      'Para lançar os projetos que já estão no quadro, use o menu "2. Importar projetos do quadro atual".' +
      avisoGatilho,
    ui.ButtonSet.OK
  );
}

/** Formulário ligado a uma aba de respostas, ou null. */
function formDaAba_(ss, nome) {
  const sh = ss.getSheetByName(nome);
  const url = sh ? sh.getFormUrl() : null;
  return url ? FormApp.openByUrl(url) : null;
}

function itemPorTitulo_(form, titulo) {
  const itens = form.getItems();
  for (let i = 0; i < itens.length; i++) {
    if (itens[i].getTitle().trim() === titulo) return itens[i];
  }
  throw new Error('Não achei a pergunta "' + titulo + '" no formulário "' + form.getTitle() + '".');
}

function criarFormPlanejamento_() {
  const form = FormApp.create('Planejamento de Projetos');
  form.setDescription(
    'Preencha quando o projeto for liberado para a produção. ' +
      'Para alterar o plano de um projeto, envie o formulário de novo com o mesmo número: vale o envio mais recente.'
  );
  form.setConfirmationMessage('Planejamento registrado. O quadro já foi atualizado.');

  form.addTextItem()
    .setTitle(TIT_NUM)
    .setHelpText('Somente números. Ex.: 0181')
    .setRequired(true)
    .setValidation(
      FormApp.createTextValidation().requireTextMatchesPattern('^\\s*\\d+\\s*$').setHelpText('Use só números. Ex.: 0181').build()
    );
  form.addTextItem().setTitle(TIT_NOME).setHelpText('Ex.: Proa do Barco').setRequired(true);

  form.addSectionHeaderItem().setTitle('Datas planejadas');
  MARCOS.forEach(function (m) {
    form.addDateItem().setTitle(tituloMarco_(m));
  });
  return form;
}

function criarFormApontamento_() {
  const form = FormApp.create('Apontamento de Produção');
  form.setDescription(
    'Registre o início ou o fim de uma etapa. ' +
      'Errou? Envie de novo com a data certa: vale o envio mais recente.'
  );
  form.setConfirmationMessage('Apontamento registrado. Obrigado!');

  form.addListItem()
    .setTitle(TIT_PROJETO)
    .setRequired(true)
    .setChoiceValues(['(nenhum projeto em aberto)']);
  form.addListItem().setTitle(TIT_ETAPA).setRequired(true).setChoiceValues(ETAPAS);
  form.addMultipleChoiceItem()
    .setTitle(TIT_EVENTO)
    .setHelpText('Liberação e Expedição têm uma data só: marque "Fim".')
    .setRequired(true)
    .setChoiceValues(['Início', 'Fim']);
  form.addDateItem().setTitle(TIT_DATA).setRequired(true);
  form.addTextItem().setTitle(TIT_RESP);
  form.addParagraphTextItem().setTitle(TIT_OBS);

  return form;
}

/** Acha a aba de respostas criada pelo formulário e dá um nome fixo a ela. */
function renomearAbaDoForm_(ss, form, nome) {
  const id = form.getId();
  for (let tentativa = 0; tentativa < 15; tentativa++) {
    SpreadsheetApp.flush();
    const planilha = SpreadsheetApp.openById(ss.getId());
    const abas = planilha.getSheets();
    for (let i = 0; i < abas.length; i++) {
      const url = abas[i].getFormUrl();
      if (url && url.indexOf(id) >= 0) {
        if (abas[i].getName() === nome) return;
        const existente = planilha.getSheetByName(nome);
        if (existente) existente.setName(nome + ' (antiga ' + Date.now() + ')');
        abas[i].setName(nome);
        return;
      }
    }
    Utilities.sleep(1000);
  }
  throw new Error('Não encontrei a aba de respostas do formulário "' + form.getTitle() + '".');
}

function escreverLinks_(ss, formPlan, formApont, itemEtapaId) {
  const sh = obterAba_(ss, ABA_LINKS);
  sh.clear();
  const linhas = [
    ['Formulário', 'Quem preenche', 'Link para responder', 'QR Code', 'Link para editar o formulário'],
    ['Planejamento de Projetos', 'PCP / quem libera o projeto', formPlan.getPublishedUrl(), '', formPlan.getEditUrl()],
    ['Apontamento de Produção', 'Produção (qualquer etapa)', formApont.getPublishedUrl(), '', formApont.getEditUrl()],
  ];
  // Um link por etapa, com a etapa já marcada: imprima o QR Code e cole no posto.
  const itemEtapa = formApont.getItemById(itemEtapaId).asListItem();
  ETAPAS.forEach(function (etapa) {
    const url = formApont.createResponse().withItemResponse(itemEtapa.createResponse(etapa)).toPrefilledUrl();
    linhas.push(['Apontamento – ' + etapa, 'Posto de ' + etapa, url, '', '']);
  });

  sh.getRange(1, 1, linhas.length, linhas[0].length).setValues(linhas);
  for (let r = 2; r <= linhas.length; r++) {
    sh.getRange(r, 4).setFormula('=IMAGE("https://quickchart.io/qr?size=200&text="&ENCODEURL(C' + r + '))');
  }
  sh.getRange(1, 1, 1, linhas[0].length).setFontWeight('bold').setBackground(FUNDO_CABECALHO);
  sh.setRowHeights(2, linhas.length - 1, 110);
  sh.setColumnWidth(1, 230);
  sh.setColumnWidth(2, 200);
  sh.setColumnWidth(3, 320);
  sh.setColumnWidth(4, 120);
  sh.setColumnWidth(5, 320);
  sh.getRange(2, 1, linhas.length - 1, linhas[0].length).setVerticalAlignment('middle').setWrap(true);
  sh.setFrozenRows(1);
}

function removerAbasVazias_(ss) {
  const manter = [ABA_PLAN, ABA_APONT, ABA_QUADRO, ABA_BASE, ABA_LINKS, ABA_DASH, ABA_DADOS_DASH];
  ss.getSheets().forEach(function (sh) {
    if (manter.indexOf(sh.getName()) < 0 && sh.getLastRow() === 0 && ss.getSheets().length > 1) {
      ss.deleteSheet(sh);
    }
  });
  [ABA_QUADRO, ABA_DASH].forEach(function (nome) {
    const sh = ss.getSheetByName(nome);
    if (sh) {
      ss.setActiveSheet(sh);
      ss.moveActiveSheet(1);
    }
  });
}

// ---------------------------------------------------------------------------
// Atualização (roda a cada envio de formulário, todo dia às 6h e pelo menu)
// ---------------------------------------------------------------------------

function aoEnviarFormulario(e) {
  const lock = LockService.getDocumentLock();
  lock.waitLock(30000);
  try {
    atualizarTudo();
  } finally {
    lock.releaseLock();
  }
}

function atualizarTudo() {
  const ss = SpreadsheetApp.getActive();
  const tz = ss.getSpreadsheetTimeZone();
  const hoje = diaNum_(new Date(), tz);
  const projetos = lerDados_(ss, tz);

  const lista = Object.keys(projetos).map(function (k) {
    const p = projetos[k];
    p.analise = analisar_(p, hoje);
    return p;
  });
  // Em aberto primeiro (pela expedição planejada), concluídos no fim.
  lista.sort(function (a, b) {
    if (a.analise.concluido !== b.analise.concluido) return a.analise.concluido ? 1 : -1;
    const ea = a.plan[MARCOS.length - 1], eb = b.plan[MARCOS.length - 1];
    if (ea !== eb) return (ea === null ? Infinity : ea) - (eb === null ? Infinity : eb);
    return a.num < b.num ? -1 : 1;
  });

  escreverQuadro_(ss, lista, hoje, tz);
  escreverBase_(ss, lista, hoje, tz);
  escreverDashboard_(ss, lista, hoje, tz);
  atualizarListaProjetos_(lista);
}

function lerDados_(ss, tz) {
  const projetos = {};

  const shP = ss.getSheetByName(ABA_PLAN);
  if (shP && shP.getLastRow() > 1) {
    const rng = shP.getDataRange();
    const vals = rng.getValues();
    const disp = rng.getDisplayValues();
    const cab = vals[0].map(function (c) { return String(c).trim(); });
    const cNum = cab.indexOf(TIT_NUM);
    const cNome = cab.indexOf(TIT_NOME);
    const cMarcos = MARCOS.map(function (m) { return cab.indexOf(tituloMarco_(m)); });
    for (let r = 1; r < vals.length; r++) {
      const num = normalizaNum_(disp[r][cNum]);
      if (!num) continue;
      // Envio mais recente substitui o anterior.
      projetos[num] = {
        num: num,
        nome: cNome >= 0 ? String(vals[r][cNome]).trim() : '',
        plan: cMarcos.map(function (c) { return c < 0 ? null : diaNum_(vals[r][c], tz); }),
        real: MARCOS.map(function () { return null; }),
      };
    }
  }

  const shA = ss.getSheetByName(ABA_APONT);
  if (shA && shA.getLastRow() > 1) {
    const rng = shA.getDataRange();
    const vals = rng.getValues();
    const disp = rng.getDisplayValues();
    const cab = vals[0].map(function (c) { return String(c).trim(); });
    const cProj = cab.indexOf(TIT_PROJETO);
    const cEtapa = cab.indexOf(TIT_ETAPA);
    const cEvento = cab.indexOf(TIT_EVENTO);
    const cData = cab.indexOf(TIT_DATA);
    for (let r = 1; r < vals.length; r++) {
      const p = projetos[normalizaNum_(disp[r][cProj])];
      if (!p) continue;
      const i = indiceMarco_(String(vals[r][cEtapa]).trim(), String(vals[r][cEvento]).trim());
      const d = diaNum_(vals[r][cData], tz);
      if (i < 0 || d === null) continue;
      p.real[i] = d; // envio mais recente substitui o anterior
    }
  }
  return projetos;
}

function indiceMarco_(etapa, evento) {
  const inicio = evento.toLowerCase().indexOf('in') === 0;
  for (let i = 0; i < MARCOS.length; i++) {
    const m = MARCOS[i];
    if (m.etapa !== etapa) continue;
    if (!DUPLAS[etapa]) return i;
    if ((m.evento === 'Início') === inicio) return i;
  }
  return -1;
}

/** Situação do projeto: etapa atual, dias de atraso e status. */
function analisar_(p, hoje) {
  const n = MARCOS.length;
  let ultimo = -1;
  for (let i = 0; i < n; i++) if (p.real[i] !== null) ultimo = i;

  const concluido = p.real[n - 1] !== null;
  let atraso = 0;
  let etapaAtual;
  if (concluido) {
    etapaAtual = 'Expedido';
    if (p.plan[n - 1] !== null) atraso = p.real[n - 1] - p.plan[n - 1];
  } else {
    const prox = ultimo + 1;
    etapaAtual = MARCOS[prox].etapa;
    const atrasoPendente = p.plan[prox] !== null && hoje > p.plan[prox] ? hoje - p.plan[prox] : 0;
    const atrasoUltimo = ultimo >= 0 && p.plan[ultimo] !== null ? p.real[ultimo] - p.plan[ultimo] : 0;
    atraso = Math.max(atrasoPendente, atrasoUltimo, 0);
  }

  let status;
  if (concluido) status = atraso > 0 ? 'Concluído com atraso' : 'Concluído no prazo';
  else status = atraso > 0 ? 'Atrasado' : 'No prazo';

  return { concluido: concluido, etapaAtual: etapaAtual, atraso: atraso, status: status };
}

function situacaoMarco_(plan, real, hoje) {
  if (real !== null) {
    if (plan === null) return { texto: 'Realizado', atraso: '' };
    return { texto: real > plan ? 'Realizado com atraso' : 'Realizado no prazo', atraso: real - plan };
  }
  if (plan !== null && hoje > plan) return { texto: 'Pendente atrasado', atraso: hoje - plan };
  return { texto: 'Pendente', atraso: '' };
}

// ---------------------------------------------------------------------------
// Aba "Quadro": réplica do quadro físico
// ---------------------------------------------------------------------------

function escreverQuadro_(ss, lista, hoje, tz) {
  const sh = obterAba_(ss, ABA_QUADRO);
  const nMarcos = MARCOS.length;
  const cPrim = 3; // coluna do primeiro marco
  const cEtapaAtual = cPrim + nMarcos;
  const nCols = cEtapaAtual + 2; // etapa atual, atraso, status

  sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns()).breakApart();
  sh.clear();
  sh.setConditionalFormatRules([]);

  const ativos = lista.filter(function (p) { return !p.analise.concluido; });
  const atrasados = ativos.filter(function (p) { return p.analise.atraso > 0; });
  sh.getRange(1, 1).setValue('QUADRO DE PRODUÇÃO').setFontSize(16).setFontWeight('bold');
  sh.getRange(1, cPrim).setValue(
    'Em aberto: ' + ativos.length + '   ·   Atrasados: ' + atrasados.length +
      '   ·   Expedidos: ' + (lista.length - ativos.length) +
      '   ·   Atualizado em ' + Utilities.formatDate(new Date(), tz, 'dd/MM/yyyy HH:mm')
  ).setFontColor('#5f6368');

  // Cabeçalho (linhas 2 e 3)
  sh.getRange(2, 1, 2, 1).merge().setValue('PROJETO');
  sh.getRange(2, 2, 2, 1).merge().setValue('');
  let col = cPrim;
  ETAPAS.forEach(function (e) {
    const larg = DUPLAS[e] ? 2 : 1;
    sh.getRange(2, col, 1, larg).merge().setValue(e.toUpperCase());
    if (DUPLAS[e]) sh.getRange(3, col, 1, 2).setValues([['Início', 'Fim']]);
    else sh.getRange(3, col).setValue('Data');
    col += larg;
  });
  sh.getRange(2, cEtapaAtual, 2, 1).merge().setValue('ETAPA ATUAL');
  sh.getRange(2, cEtapaAtual + 1, 2, 1).merge().setValue('ATRASO (dias)');
  sh.getRange(2, cEtapaAtual + 2, 2, 1).merge().setValue('STATUS');
  sh.getRange(2, 1, 2, nCols)
    .setFontWeight('bold').setBackground(FUNDO_CABECALHO)
    .setHorizontalAlignment('center').setVerticalAlignment('middle');
  sh.getRange(3, 1, 1, nCols).setFontWeight('normal').setFontColor('#5f6368');

  if (lista.length === 0) {
    sh.getRange(4, 1).setValue('Nenhum projeto cadastrado ainda. Preencha o formulário "Planejamento de Projetos".');
    formatarGradeQuadro_(sh, 3, nCols);
    return;
  }

  const valores = [], cores = [], fundos = [], pesos = [];
  lista.forEach(function (p) {
    const a = p.analise;
    const lp = [p.num + '\n' + p.nome, 'Planejado'];
    const lr = ['', 'Realizado'];
    const cp = [COR_PLAN, '#5f6368'], cr = [COR_PLAN, '#5f6368'];
    const fp = [BRANCO, BRANCO], fr = [BRANCO, BRANCO];
    const wp = ['bold', 'normal'], wr = ['normal', 'normal'];

    for (let i = 0; i < nMarcos; i++) {
      const plan = p.plan[i], real = p.real[i];
      lp.push(plan === null ? '' : diaParaData_(plan, tz));
      cp.push(COR_PLAN);
      wp.push('normal');
      fp.push(real === null && plan !== null && hoje > plan ? FUNDO_PENDENTE_ATRASADO : BRANCO);

      lr.push(real === null ? '' : diaParaData_(real, tz));
      const atrasado = real !== null && plan !== null && real > plan;
      cr.push(atrasado ? COR_REAL_ATRASO : COR_REAL_OK);
      wr.push('bold');
      fr.push(BRANCO);
    }

    const corStatus = a.atraso > 0 ? COR_REAL_ATRASO : a.concluido ? '#5f6368' : '#188038';
    const fundoStatus = a.atraso > 0 ? FUNDO_PENDENTE_ATRASADO : a.concluido ? '#f1f3f4' : '#e6f4ea';
    lp.push(a.etapaAtual, a.atraso, a.status);
    lr.push('', '', '');
    cp.push(COR_PLAN, corStatus, corStatus);
    cr.push(COR_PLAN, corStatus, corStatus);
    wp.push('bold', 'bold', 'bold');
    wr.push('normal', 'normal', 'normal');
    fp.push(BRANCO, fundoStatus, fundoStatus);
    fr.push(BRANCO, fundoStatus, fundoStatus);

    valores.push(lp, lr);
    cores.push(cp, cr);
    fundos.push(fp, fr);
    pesos.push(wp, wr);
  });

  const linIni = 4;
  const rng = sh.getRange(linIni, 1, valores.length, nCols);
  rng.setValues(valores).setFontColors(cores).setBackgrounds(fundos).setFontWeights(pesos);
  rng.setHorizontalAlignment('center').setVerticalAlignment('middle');
  sh.getRange(linIni, cPrim, valores.length, nMarcos).setNumberFormat('dd/MM');
  sh.getRange(linIni, 1, valores.length, 1).setWrap(true).setHorizontalAlignment('left');

  for (let k = 0; k < lista.length; k++) {
    const r = linIni + k * 2;
    [1, cEtapaAtual, cEtapaAtual + 1, cEtapaAtual + 2].forEach(function (c) {
      sh.getRange(r, c, 2, 1).merge();
    });
  }
  formatarGradeQuadro_(sh, linIni + valores.length - 1, nCols);
}

function formatarGradeQuadro_(sh, ultimaLinha, nCols) {
  sh.getRange(2, 1, ultimaLinha - 1, nCols)
    .setBorder(true, true, true, true, true, true, COR_GRADE, SpreadsheetApp.BorderStyle.SOLID);
  sh.setFrozenRows(3);
  sh.setFrozenColumns(2);
  sh.setColumnWidth(1, 170);
  sh.setColumnWidth(2, 80);
  for (let c = 3; c < 3 + MARCOS.length; c++) sh.setColumnWidth(c, 62);
  sh.setColumnWidth(3 + MARCOS.length, 130);
  sh.setColumnWidth(4 + MARCOS.length, 90);
  sh.setColumnWidth(5 + MARCOS.length, 160);
}

// ---------------------------------------------------------------------------
// Aba "Base": tabela plana para o Looker Studio (uma linha por marco)
// ---------------------------------------------------------------------------

function escreverBase_(ss, lista, hoje, tz) {
  const sh = obterAba_(ss, ABA_BASE);
  sh.clear();
  const linhas = [[
    'Projeto', 'Nº', 'Nome', 'Ordem', 'Etapa', 'Evento', 'Planejado', 'Realizado',
    'Atraso (dias)', 'Situação', 'Etapa atual do projeto', 'Atraso do projeto (dias)', 'Status do projeto',
  ]];
  lista.forEach(function (p) {
    MARCOS.forEach(function (m, i) {
      const s = situacaoMarco_(p.plan[i], p.real[i], hoje);
      linhas.push([
        p.num + ' – ' + p.nome, p.num, p.nome, i + 1, m.etapa, m.evento,
        p.plan[i] === null ? '' : diaParaData_(p.plan[i], tz),
        p.real[i] === null ? '' : diaParaData_(p.real[i], tz),
        s.atraso, s.texto, p.analise.etapaAtual, p.analise.atraso, p.analise.status,
      ]);
    });
  });
  sh.getRange(1, 2, linhas.length, 1).setNumberFormat('@'); // mantém o zero à esquerda (0181)
  sh.getRange(1, 1, linhas.length, linhas[0].length).setValues(linhas);
  sh.getRange(2, 7, Math.max(linhas.length - 1, 1), 2).setNumberFormat('dd/MM/yyyy');
  sh.getRange(1, 1, 1, linhas[0].length).setFontWeight('bold').setBackground(FUNDO_CABECALHO);
  sh.setFrozenRows(1);
}

// ---------------------------------------------------------------------------
// Aba "Dashboard": indicadores, gráficos e linha do tempo (Gantt)
// ---------------------------------------------------------------------------

const DASH_COL_DIAS = 9;     // coluna onde começa a linha do tempo (I)
const DASH_LARG_COL = 24;    // largura de todas as colunas (px)
const DASH_LIN_GRAF = 9;     // linha onde ficam os gráficos
const DASH_LIN_GANTT = 24;   // linha do título da linha do tempo
const DASH_MAX_DIAS = 140;

function escreverDashboard_(ss, lista, hoje, tz) {
  const dados = escreverDadosDashboard_(ss, lista);
  const sh = ss.getSheetByName(ABA_DASH) || ss.insertSheet(ABA_DASH, 0);
  if (sh.getMaxColumns() < 60) sh.insertColumnsAfter(sh.getMaxColumns(), 60 - sh.getMaxColumns());

  sh.getCharts().forEach(function (c) { sh.removeChart(c); });
  sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns()).breakApart();
  sh.clear();
  sh.setHiddenGridlines(true);
  sh.setColumnWidth(1, 16);
  sh.setColumnWidths(2, sh.getMaxColumns() - 1, DASH_LARG_COL);
  sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns())
    .setBackground(COR_SUPERFICIE).setFontColor(COR_TEXTO).setFontFamily('Arial');

  sh.getRange(1, 2).setValue('DASHBOARD DE PRODUÇÃO').setFontSize(18).setFontWeight('bold');
  sh.getRange(2, 2).setValue('Atualizado em ' + Utilities.formatDate(new Date(), tz, 'dd/MM/yyyy HH:mm') +
    '  ·  atualiza sozinho a cada formulário enviado').setFontColor(COR_TEXTO_2);

  escreverIndicadores_(sh, lista);
  inserirGraficos_(sh, dados);
  escreverGantt_(sh, lista, hoje, tz);
  sh.setFrozenRows(2);
}

/** Tabelas que alimentam os gráficos (aba "Dados do dashboard"). */
function escreverDadosDashboard_(ss, lista) {
  const sh = ss.getSheetByName(ABA_DADOS_DASH) || ss.insertSheet(ABA_DADOS_DASH, ss.getNumSheets());
  sh.clear();
  const ativos = lista.filter(function (p) { return !p.analise.concluido; });

  // A: projetos em aberto por etapa atual
  const porEtapa = [['Etapa atual', 'Projetos']];
  ETAPAS.forEach(function (e) {
    porEtapa.push([e, ativos.filter(function (p) { return p.analise.etapaAtual === e; }).length]);
  });
  sh.getRange(1, 1, porEtapa.length, 2).setValues(porEtapa);

  // D: duração média (dias) prevista × real, só de etapas já concluídas
  const duracao = [['Etapa', 'Previsto', 'Real']];
  let temDuracao = false;
  ETAPAS.filter(function (e) { return DUPLAS[e]; }).forEach(function (e) {
    const iIni = indiceMarco_(e, 'Início'), iFim = indiceMarco_(e, 'Fim');
    let somaPlan = 0, somaReal = 0, n = 0;
    lista.forEach(function (p) {
      if (p.real[iIni] === null || p.real[iFim] === null || p.plan[iIni] === null || p.plan[iFim] === null) return;
      somaPlan += p.plan[iFim] - p.plan[iIni] + 1;
      somaReal += p.real[iFim] - p.real[iIni] + 1;
      n++;
    });
    if (n) temDuracao = true;
    duracao.push([e, n ? Math.round(somaPlan / n * 10) / 10 : 0, n ? Math.round(somaReal / n * 10) / 10 : 0]);
  });
  sh.getRange(1, 4, duracao.length, 3).setValues(duracao);

  // H: atraso por projeto em aberto (maior primeiro)
  const atrasos = [['Projeto', 'Atraso (dias)']];
  ativos.slice()
    .sort(function (a, b) { return b.analise.atraso - a.analise.atraso; })
    .forEach(function (p) { atrasos.push([p.num + ' ' + p.nome, p.analise.atraso]); });
  sh.getRange(1, 8, atrasos.length, 2).setValues(atrasos);

  sh.getRange(1, 1, 1, 9).setFontWeight('bold');
  sh.getRange(1, 1).setNote('Aba gerada automaticamente para os gráficos do Dashboard. Não edite.');
  return {
    sh: sh,
    porEtapa: sh.getRange(1, 1, porEtapa.length, 2),
    duracao: sh.getRange(1, 4, duracao.length, 3),
    temDuracao: temDuracao,
    atrasos: sh.getRange(1, 8, atrasos.length, 2),
    nAtrasos: atrasos.length - 1,
  };
}

function escreverIndicadores_(sh, lista) {
  const ativos = lista.filter(function (p) { return !p.analise.concluido; });
  const atrasados = ativos.filter(function (p) { return p.analise.atraso > 0; });
  const expedidos = lista.length - ativos.length;
  const pior = atrasados.slice().sort(function (a, b) { return b.analise.atraso - a.analise.atraso; })[0];
  const pct = ativos.length ? Math.round((ativos.length - atrasados.length) / ativos.length * 100) : 0;

  const cards = [
    { rotulo: 'Em aberto', valor: ativos.length, legenda: 'projetos em produção', cor: COR_TEXTO },
    { rotulo: '⚠ Atrasados', valor: atrasados.length, legenda: 'de ' + ativos.length + ' em aberto',
      cor: atrasados.length ? COR_STATUS_CRITICO : COR_TEXTO },
    { rotulo: '✓ No prazo', valor: ativos.length - atrasados.length, legenda: pct + '% em dia',
      cor: ativos.length - atrasados.length ? COR_STATUS_OK : COR_TEXTO },
    { rotulo: 'Expedidos', valor: expedidos, legenda: 'projetos concluídos', cor: COR_TEXTO },
    { rotulo: 'Maior atraso', valor: pior ? pior.analise.atraso + ' d' : '0 d',
      legenda: pior ? pior.num + ' – ' + pior.nome : 'nenhum atraso', cor: pior ? COR_STATUS_CRITICO : COR_TEXTO },
  ];
  const larg = 6, linha = 4;
  cards.forEach(function (c, k) {
    const col = 2 + k * (larg + 1);
    sh.getRange(linha, col, 1, larg).merge().setValue(c.rotulo)
      .setFontColor(COR_TEXTO_2).setFontSize(10).setFontWeight('bold');
    sh.getRange(linha + 1, col, 2, larg).merge().setValue(c.valor)
      .setFontColor(c.cor).setFontSize(26).setFontWeight('bold').setVerticalAlignment('middle')
      .setHorizontalAlignment('left');
    sh.getRange(linha + 3, col, 1, larg).merge().setValue(c.legenda)
      .setFontColor(COR_TEXTO_2).setFontSize(9);
    sh.getRange(linha, col, 4, larg).setBackground(BRANCO)
      .setBorder(true, true, true, true, false, false, '#e0e0dc', SpreadsheetApp.BorderStyle.SOLID);
  });
}

function inserirGraficos_(sh, dados) {
  const larg = 400, alt = 250;
  const eixo = { textStyle: { color: COR_TEXTO_2, fontSize: 10 }, gridlines: { color: '#ececea' },
    baselineColor: '#c3c2b7', minValue: 0, format: '0' };
  const titulo = { color: COR_TEXTO, fontSize: 12, bold: true };

  sh.insertChart(sh.newChart().asColumnChart()
    .addRange(dados.porEtapa).setNumHeaders(1)
    .setPosition(DASH_LIN_GRAF, 2, 0, 0)
    .setOption('title', 'Projetos em aberto por etapa atual')
    .setOption('titleTextStyle', titulo)
    .setOption('legend', { position: 'none' })
    .setOption('colors', [CORES_ETAPA['Liberação']])
    .setOption('vAxis', eixo)
    .setOption('series', { 0: { dataLabel: 'value' } })
    .setOption('width', larg).setOption('height', alt)
    .build());

  sh.insertChart(sh.newChart().asColumnChart()
    .addRange(dados.duracao).setNumHeaders(1)
    .setPosition(DASH_LIN_GRAF, 2 + 17, 0, 0)
    .setOption('title', dados.temDuracao
      ? 'Duração média por etapa (dias): previsto × real'
      : 'Duração média por etapa (aparece quando alguma etapa terminar)')
    .setOption('titleTextStyle', titulo)
    .setOption('legend', { position: 'top', textStyle: { color: COR_TEXTO_2 } })
    .setOption('colors', ['#9ec5f4', '#1c5cab'])
    .setOption('vAxis', eixo)
    .setOption('series', { 0: { dataLabel: 'value' }, 1: { dataLabel: 'value' } })
    .setOption('width', larg).setOption('height', alt)
    .build());

  if (dados.nAtrasos > 0) {
    sh.insertChart(sh.newChart().asBarChart()
      .addRange(dados.atrasos).setNumHeaders(1)
      .setPosition(DASH_LIN_GRAF, 2 + 34, 0, 0)
      .setOption('title', 'Atraso por projeto em aberto (dias)')
      .setOption('titleTextStyle', titulo)
      .setOption('legend', { position: 'none' })
      .setOption('colors', [COR_STATUS_CRITICO])
      .setOption('hAxis', eixo)
      .setOption('series', { 0: { dataLabel: 'value' } })
      .setOption('width', larg).setOption('height', alt)
      .build());
  } else {
    sh.getRange(DASH_LIN_GRAF + 1, 2 + 34).setValue('Nenhum projeto em aberto.').setFontColor(COR_TEXTO_2);
  }
}

/** Linha do tempo: por projeto, uma linha "Previsto" e uma "Real", cada dia colorido pela etapa. */
function escreverGantt_(sh, lista, hoje, tz) {
  const r0 = DASH_LIN_GANTT;
  sh.getRange(r0, 2).setValue('LINHA DO TEMPO').setFontSize(13).setFontWeight('bold');
  sh.getRange(r0, 10).setValue('Previsto = cor clara · Real = cor forte · coluna vermelha = hoje · letra = início da etapa')
    .setFontColor(COR_TEXTO_2).setFontSize(9);

  // Legenda (cor + nome, nunca só cor)
  let col = 2;
  ETAPAS.forEach(function (e) {
    sh.getRange(r0 + 1, col).setBackground(CORES_ETAPA[e]).setValue(e.charAt(0))
      .setFontColor(corTextoSobre_(CORES_ETAPA[e])).setHorizontalAlignment('center').setFontWeight('bold');
    sh.getRange(r0 + 1, col + 1).setValue(e).setFontSize(9).setFontColor(COR_TEXTO_2);
    col += 6;
  });

  const ativos = lista.filter(function (p) { return !p.analise.concluido; });
  const mostrar = ativos.length ? ativos : lista;
  if (!mostrar.length) {
    sh.getRange(r0 + 3, 2).setValue('Nenhum projeto cadastrado ainda.').setFontColor(COR_TEXTO_2);
    return;
  }

  // Período exibido
  let ini = hoje, fim = hoje;
  mostrar.forEach(function (p) {
    p.plan.concat(p.real).forEach(function (d) {
      if (d === null) return;
      if (d < ini) ini = d;
      if (d > fim) fim = d;
    });
  });
  ini -= 2; fim += 3;
  if (fim - ini + 1 > DASH_MAX_DIAS) {
    ini = Math.max(ini, hoje - 45);
    fim = ini + DASH_MAX_DIAS - 1;
  }
  const nDias = fim - ini + 1;
  const precisa = DASH_COL_DIAS + nDias;
  if (sh.getMaxColumns() < precisa) {
    const antes = sh.getMaxColumns();
    sh.insertColumnsAfter(antes, precisa - antes);
    sh.setColumnWidths(antes + 1, precisa - antes, DASH_LARG_COL);
  }

  // Cabeçalho de datas: dd/MM nas segundas-feiras, número do dia em todas as colunas
  const linSemana = r0 + 3, linDia = r0 + 4;
  const semana = [], dia = [];
  for (let d = ini; d <= fim; d++) {
    const data = diaParaData_(d, tz);
    const segunda = Utilities.formatDate(data, tz, 'u') === '1';
    semana.push(d === hoje ? 'HOJE' : segunda ? Utilities.formatDate(data, tz, 'dd/MM') : '');
    dia.push(Utilities.formatDate(data, tz, 'dd'));
  }
  sh.getRange(linSemana, DASH_COL_DIAS, 1, nDias).setValues([semana])
    .setFontSize(9).setFontColor(COR_TEXTO_2).setFontWeight('bold');
  sh.getRange(linDia, DASH_COL_DIAS, 1, nDias).setValues([dia])
    .setFontSize(8).setFontColor(COR_TEXTO_2).setHorizontalAlignment('center');
  sh.getRange(linSemana, DASH_COL_DIAS + (hoje - ini)).setFontColor(COR_STATUS_CRITICO);
  sh.getRange(linSemana, 2).setValue('Projeto').setFontWeight('bold').setFontColor(COR_TEXTO_2);

  // Barras
  const linIni = linDia + 1;
  const valores = [], fundos = [], cores = [];
  mostrar.forEach(function (p) {
    [['plan', true], ['real', false]].forEach(function (t) {
      const v = [], f = [], c = [];
      for (let k = 0; k < nDias; k++) { v.push(''); f.push(BRANCO); c.push(COR_TEXTO); }
      segmentos_(p[t[0]], t[0] === 'real' ? hoje : null).forEach(function (s) {
        const base = CORES_ETAPA[s.etapa];
        const cor = t[1] ? clarear_(base, 0.6) : base;
        const a = Math.max(s.ini, ini), b = Math.min(s.fim, fim);
        for (let d = a; d <= b; d++) f[d - ini] = cor;
        if (s.ini >= ini && s.ini <= fim) {
          v[s.ini - ini] = s.etapa.charAt(0);
          c[s.ini - ini] = corTextoSobre_(cor);
        }
      });
      valores.push(v); fundos.push(f); cores.push(c);
    });
  });
  const grade = sh.getRange(linIni, DASH_COL_DIAS, valores.length, nDias);
  grade.setValues(valores).setBackgrounds(fundos).setFontColors(cores)
    .setFontSize(8).setFontWeight('bold').setHorizontalAlignment('center').setVerticalAlignment('middle');
  grade.setBorder(null, null, true, null, null, true, '#ececea', SpreadsheetApp.BorderStyle.SOLID);

  // Rótulos das linhas
  mostrar.forEach(function (p, k) {
    const r = linIni + k * 2;
    sh.getRange(r, 2, 2, 5).merge().setValue(p.num + '\n' + p.nome)
      .setFontWeight('bold').setFontSize(9).setWrap(true).setVerticalAlignment('middle')
      .setFontColor(p.analise.atraso > 0 ? COR_STATUS_CRITICO : COR_TEXTO);
    sh.getRange(r, 7, 1, 2).merge().setValue('Previsto').setFontSize(8).setFontColor(COR_TEXTO_2);
    sh.getRange(r + 1, 7, 1, 2).merge().setValue('Real').setFontSize(8).setFontColor(COR_TEXTO_2);
    sh.getRange(r, 2, 2, DASH_COL_DIAS - 2 + nDias)
      .setBorder(null, null, true, null, null, null, '#c3c2b7', SpreadsheetApp.BorderStyle.SOLID);
  });

  // Hoje
  sh.getRange(linSemana, DASH_COL_DIAS + (hoje - ini), valores.length + 2, 1)
    .setBorder(null, true, null, true, null, null, COR_STATUS_CRITICO, SpreadsheetApp.BorderStyle.SOLID_MEDIUM);
}

/** Trechos [ini, fim] de cada etapa. No "real", etapa começada e não terminada vai até hoje. */
function segmentos_(datas, hoje) {
  const seg = [];
  ETAPAS.forEach(function (e) {
    if (!DUPLAS[e]) {
      const d = datas[indiceMarco_(e, 'Fim')];
      if (d !== null) seg.push({ etapa: e, ini: d, fim: d });
      return;
    }
    const a = datas[indiceMarco_(e, 'Início')], b = datas[indiceMarco_(e, 'Fim')];
    if (a !== null && b !== null) seg.push({ etapa: e, ini: Math.min(a, b), fim: Math.max(a, b) });
    else if (a !== null) seg.push({ etapa: e, ini: a, fim: hoje !== null ? Math.max(a, hoje) : a });
    else if (b !== null) seg.push({ etapa: e, ini: b, fim: b });
  });
  return seg;
}

function clarear_(hex, t) {
  const n = parseInt(hex.slice(1), 16);
  const canal = function (v) { return Math.round(v + (255 - v) * t).toString(16).padStart(2, '0'); };
  return '#' + canal((n >> 16) & 255) + canal((n >> 8) & 255) + canal(n & 255);
}

function corTextoSobre_(hex) {
  const n = parseInt(hex.slice(1), 16);
  const lum = (0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255;
  return lum > 0.6 ? COR_TEXTO : BRANCO;
}

// ---------------------------------------------------------------------------
// Lista de projetos do formulário de apontamento
// ---------------------------------------------------------------------------

function atualizarListaProjetos_(lista) {
  const props = PropertiesService.getDocumentProperties();
  const formId = props.getProperty('FORM_APONT_ID');
  const itemId = props.getProperty('ITEM_PROJETO_ID');
  if (!formId || !itemId) return;
  let opcoes = lista
    .filter(function (p) { return !p.analise.concluido; })
    .map(function (p) { return p.num + ' – ' + p.nome; })
    .sort();
  if (opcoes.length === 0) opcoes = ['(nenhum projeto em aberto)'];
  const item = FormApp.openById(formId).getItemById(Number(itemId)).asListItem();
  const atuais = item.getChoices().map(function (c) { return c.getValue(); });
  if (atuais.join('|') !== opcoes.join('|')) item.setChoiceValues(opcoes);
}

// ---------------------------------------------------------------------------
// Importação dos projetos que já estão no quadro físico (foto de 09/2026)
// ---------------------------------------------------------------------------

const QUADRO_ATUAL = [
  {
    num: '0181', nome: 'Proa do Barco',
    // Liberação, Benef. ini/fim, Montagem ini/fim, Pintura ini/fim, Embalagem ini/fim, Expedição
    plan: ['02/09', '03/09', '04/09', '08/09', '18/09', '21/09', '23/09', '24/09', '24/09', '25/09'],
    real: ['18/09', '18/09', '18/09', '21/09', '', '', '', '', '', ''],
  },
  {
    num: '0241', nome: 'Lab Play',
    plan: ['02/09', '03/09', '04/09', '08/09', '15/09', '16/09', '18/09', '21/09', '21/09', '22/09'],
    real: ['11/09', '14/09', '15/09', '16/09', '', '', '', '', '', ''],
  },
  {
    num: '0045', nome: 'WallB',
    plan: ['17/08', '18/08', '19/08', '20/08', '17/09', '18/09', '24/09', '25/09', '30/09', '01/10'],
    real: ['24/08', '18/08', '24/08', '', '', '', '', '', '', ''],
  },
];
const ANO_QUADRO_ATUAL = 2026;

function importarQuadroAtual() {
  const ui = SpreadsheetApp.getUi();
  const ss = SpreadsheetApp.getActive();
  const shP = ss.getSheetByName(ABA_PLAN);
  const shA = ss.getSheetByName(ABA_APONT);
  if (!shP || !shA) {
    ui.alert('Rode primeiro "1. Configurar (criar formulários)".');
    return;
  }
  const resp = ui.alert(
    'Importar projetos do quadro',
    'Serão lançados os projetos 0181, 0241 e 0045 com as datas do quadro físico. Continuar?',
    ui.ButtonSet.YES_NO
  );
  if (resp !== ui.Button.YES) return;

  const tz = ss.getSpreadsheetTimeZone();
  const data = function (ddmm) {
    return ddmm ? Utilities.parseDate(ddmm + '/' + ANO_QUADRO_ATUAL, tz, 'dd/MM/yyyy') : '';
  };
  const agora = new Date();

  const cabP = shP.getRange(1, 1, 1, shP.getLastColumn()).getValues()[0].map(function (c) { return String(c).trim(); });
  const linhasP = QUADRO_ATUAL.map(function (p) {
    const linha = cabP.map(function () { return ''; });
    linha[0] = agora;
    linha[cabP.indexOf(TIT_NUM)] = "'" + p.num;
    linha[cabP.indexOf(TIT_NOME)] = p.nome;
    MARCOS.forEach(function (m, i) {
      const c = cabP.indexOf(tituloMarco_(m));
      if (c >= 0) linha[c] = data(p.plan[i]);
    });
    return linha;
  });
  shP.getRange(shP.getLastRow() + 1, 1, linhasP.length, cabP.length).setValues(linhasP);

  const cabA = shA.getRange(1, 1, 1, shA.getLastColumn()).getValues()[0].map(function (c) { return String(c).trim(); });
  const linhasA = [];
  QUADRO_ATUAL.forEach(function (p) {
    MARCOS.forEach(function (m, i) {
      if (!p.real[i]) return;
      const linha = cabA.map(function () { return ''; });
      linha[0] = agora;
      linha[cabA.indexOf(TIT_PROJETO)] = p.num + ' – ' + p.nome;
      linha[cabA.indexOf(TIT_ETAPA)] = m.etapa;
      linha[cabA.indexOf(TIT_EVENTO)] = m.evento === 'Início' ? 'Início' : 'Fim';
      linha[cabA.indexOf(TIT_DATA)] = data(p.real[i]);
      const cResp = cabA.indexOf(TIT_RESP);
      if (cResp >= 0) linha[cResp] = 'Importado do quadro';
      linhasA.push(linha);
    });
  });
  shA.getRange(shA.getLastRow() + 1, 1, linhasA.length, cabA.length).setValues(linhasA);

  atualizarTudo();
  ss.setActiveSheet(ss.getSheetByName(ABA_QUADRO));
  ui.alert('Projetos importados. Confira a aba "' + ABA_QUADRO + '".');
}

// ---------------------------------------------------------------------------
// Utilitários
// ---------------------------------------------------------------------------

function obterAba_(ss, nome) {
  return ss.getSheetByName(nome) || ss.insertSheet(nome);
}

/** "181", "0181", "0181 – Proa do Barco" -> "0181" */
function normalizaNum_(s) {
  const m = String(s || '').match(/^\s*'?(\d+)/);
  if (!m) return '';
  let n = m[1];
  while (n.length < 4) n = '0' + n;
  return n;
}

/** Data -> número de dias (ignora horário), no fuso da planilha. */
function diaNum_(v, tz) {
  if (!(v instanceof Date) || isNaN(v.getTime())) return null;
  const p = Utilities.formatDate(v, tz, 'yyyy-MM-dd').split('-').map(Number);
  return Math.round(Date.UTC(p[0], p[1] - 1, p[2]) / 86400000);
}

function diaParaData_(n, tz) {
  const iso = Utilities.formatDate(new Date(n * 86400000), 'UTC', 'yyyy-MM-dd');
  return Utilities.parseDate(iso, tz, 'yyyy-MM-dd');
}
