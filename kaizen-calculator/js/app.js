"use strict";

/* ===================== Formatting helpers ===================== */

const BRL = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const NUM2 = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function fmtCurrency(v) { return BRL.format(Number.isFinite(v) ? v : 0); }
function fmtCurrencyAno(v) { return `${fmtCurrency(v)} por ano`; }
function fmtNum(v, digits = 2) { return (Number.isFinite(v) ? v : 0).toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits }); }
function fmtPercent(v) { return `${fmtNum(v, 1)}%`; }

function parseCurrencyInput(value) {
  if (!value) return 0;
  const cleaned = String(value).replace(/[^\d,.-]/g, "").replace(/\./g, "").replace(",", ".");
  const n = parseFloat(cleaned);
  return Number.isFinite(n) ? n : 0;
}
function parseNumberInput(value) {
  const n = parseFloat(String(value).replace(",", "."));
  return Number.isFinite(n) ? n : 0;
}
function parsePercentInput(value) {
  if (!value) return 0;
  const cleaned = String(value).replace(/[^\d,.-]/g, "").replace(",", ".");
  const n = parseFloat(cleaned);
  return Number.isFinite(n) ? n : 0;
}

function maskCurrencyKeyup(e) {
  let digits = e.target.value.replace(/\D/g, "");
  if (!digits) { e.target.value = ""; return; }
  digits = digits.replace(/^0+(?=\d)/, "");
  while (digits.length < 3) digits = "0" + digits;
  const cents = digits.slice(-2);
  let intPart = digits.slice(0, -2).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  e.target.value = `${intPart},${cents}`;
}

function maskPercentBlur(e) {
  let v = parsePercentInput(e.target.value);
  v = Math.min(100, Math.max(0, v));
  e.target.value = v ? `${fmtNum(v, 1)}%` : "";
}
function maskPercentFocus(e) {
  const v = parsePercentInput(e.target.value);
  e.target.value = v ? String(v).replace(".", ",") : "";
}

function addMonthsApprox(dateStr, months) {
  const d = new Date(dateStr + "T00:00:00");
  const whole = Math.floor(months);
  const fracDays = Math.round((months - whole) * 30.44);
  d.setMonth(d.getMonth() + whole);
  d.setDate(d.getDate() + fracDays);
  return d;
}

/* ===================== Gain definitions ===================== */

const GAIN_DEFS = {
  g1: {
    code: "G1", name: "Redução do Tempo Operacional", icon: "⏱", color: "blue",
    subtitle: "Economia de mão de obra pela redução do tempo e/ou da frequência de execução de uma atividade.",
    fields: [
      { id: "cmo", label: "Custo da Mão de Obra por Hora (CMO)", type: "currency", placeholder: "0,00", group: "Parâmetros Gerais" },
      { id: "meses", label: "Meses por Ano", type: "number", step: "1", min: 1, max: 12, default: 12, group: "Parâmetros Gerais" },
      { id: "tempoAntes", label: "Tempo Antes (horas)", type: "number", step: "0.001", min: 0, group: "Situação Antes" },
      { id: "freqAntes", label: "Frequência Antes (execuções/mês)", type: "number", step: "1", min: 0, group: "Situação Antes" },
      { id: "tempoDepois", label: "Tempo Depois (horas)", type: "number", step: "0.001", min: 0, group: "Situação Depois" },
      { id: "freqDepois", label: "Frequência Depois (execuções/mês)", type: "number", step: "1", min: 0, group: "Situação Depois" },
    ],
  },
  g2: {
    code: "G2", name: "Aumento de Produtividade", icon: "⚙️", color: "blue",
    subtitle: "Ganho pelo melhor aproveitamento da capacidade produtiva do recurso, via Custo Hora Homem, Máquina ou Processo.",
    fields: [
      {
        id: "costType", label: "Tipo de Custo Considerado", type: "radio", default: "process",
        options: [
          { value: "chh", label: "Custo Hora Homem" },
          { value: "chm", label: "Custo Hora Máquina" },
          { value: "process", label: "Custo Hora do Processo (Homem + Máquina)", recommended: true },
        ],
      },
      { id: "chh", label: "Custo Hora Homem (CHH)", type: "currency", placeholder: "0,00", visibleFor: ["chh", "process"] },
      { id: "chm", label: "Custo Hora Máquina (CHM)", type: "currency", placeholder: "0,00", visibleFor: ["chm", "process"] },
      { id: "prodAntes", label: "Produção Antes (peças/mês)", type: "number", step: "1", min: 0 },
      { id: "prodDepois", label: "Produção Depois (peças/mês)", type: "number", step: "1", min: 0 },
      { id: "horasDisp", label: "Horas Disponíveis do Recurso por Mês", type: "number", step: "0.1", min: 0 },
      { id: "meses", label: "Meses por Ano", type: "number", step: "1", min: 1, max: 12, default: 12 },
    ],
  },
  g3: {
    code: "G3", name: "Redução de Quebra / Refugo", icon: "♻️", color: "green",
    subtitle: "Economia de matéria-prima pela redução do percentual de perdas no processo.",
    fields: [
      { id: "cmp", label: "Custo da Matéria-Prima por Peça (CMP)", type: "currency", placeholder: "0,00" },
      { id: "producaoMensal", label: "Produção Mensal (peças)", type: "number", step: "1", min: 0 },
      { id: "pctAntes", label: "% Quebra Antes", type: "percent", placeholder: "0%" },
      { id: "pctDepois", label: "% Quebra Depois", type: "percent", placeholder: "0%" },
      { id: "meses", label: "Meses por Ano", type: "number", step: "1", min: 1, max: 12, default: 12 },
    ],
  },
  g4: {
    code: "G4", name: "Custo Evitado", icon: "💰", color: "green",
    subtitle: "Economia entre o valor orçado e o efetivamente realizado no investimento e nos custos mensais.",
    fields: [
      { id: "valorOrcado", label: "Valor Orçado (Investimento)", type: "currency", placeholder: "0,00", group: "Investimento" },
      { id: "valorRealizado", label: "Valor Realizado (Investimento)", type: "currency", placeholder: "0,00", group: "Investimento" },
      { id: "valorMensalOrcado", label: "Valor Mensal Orçado", type: "currency", placeholder: "0,00", group: "Custos Mensais" },
      { id: "valorMensalRealizado", label: "Valor Mensal Realizado", type: "currency", placeholder: "0,00", group: "Custos Mensais" },
      { id: "meses", label: "Meses por Ano", type: "number", step: "1", min: 1, max: 12, default: 12, group: "Custos Mensais" },
    ],
  },
};

const GAIN_ORDER = ["g1", "g2", "g3", "g4"];

/* ===================== Application state ===================== */
// state.instances[gid] is an array of Kaizen instances for that gain type:
// { uid, name, inputs, result }. Multiple instances per type are supported.

const state = {
  active: new Set(),
  instances: { g1: [], g2: [], g3: [], g4: [] },
  calculated: false,
};
let instanceCounter = 1;

/* ===================== Calculation engine ===================== */

function readInstanceInputs(gid, uid) {
  const def = GAIN_DEFS[gid];
  const values = {};
  for (const f of def.fields) {
    if (f.type === "radio") {
      const checked = document.querySelector(`input[name="${gid}_${uid}_${f.id}"]:checked`);
      values[f.id] = checked ? checked.value : f.default;
      continue;
    }
    const el = document.getElementById(`${gid}_${uid}_${f.id}`);
    if (!el) { values[f.id] = f.default || 0; continue; }
    if (f.type === "currency") values[f.id] = parseCurrencyInput(el.value);
    else if (f.type === "percent") values[f.id] = parsePercentInput(el.value);
    else values[f.id] = parseNumberInput(el.value);
  }
  return values;
}

function calcG1(v) {
  const horasGastasAntes = v.tempoAntes * v.freqAntes;
  const horasGastasDepois = v.tempoDepois * v.freqDepois;
  const horasEconomizadasMes = horasGastasAntes - horasGastasDepois;
  const economiaMensal = horasEconomizadasMes * v.cmo;
  const economiaAnual = economiaMensal * (v.meses || 12);
  return {
    outputs: { horasGastasAntes, horasGastasDepois, horasEconomizadasMes, economiaMensal, economiaAnual },
    annual: economiaAnual,
    steps: [
      `Horas gastas Antes = Tempo Antes × Frequência Antes = ${fmtNum(v.tempoAntes,3)} h × ${fmtNum(v.freqAntes,0)} = ${fmtNum(horasGastasAntes,2)} h/mês`,
      `Horas gastas Depois = Tempo Depois × Frequência Depois = ${fmtNum(v.tempoDepois,3)} h × ${fmtNum(v.freqDepois,0)} = ${fmtNum(horasGastasDepois,2)} h/mês`,
      `Horas economizadas/mês = Horas Antes − Horas Depois = ${fmtNum(horasGastasAntes,2)} h − ${fmtNum(horasGastasDepois,2)} h = ${fmtNum(horasEconomizadasMes,2)} h/mês`,
      `Economia mensal = Horas economizadas × CMO/h = ${fmtNum(horasEconomizadasMes,2)} h × ${fmtCurrency(v.cmo)} = ${fmtCurrency(economiaMensal)}`,
      `Economia anual = Economia mensal × ${v.meses || 12} meses = ${fmtCurrency(economiaAnual)}`,
    ],
  };
}

function calcG2(v) {
  const steps = [];
  let custoHora, custoHoraLabel;
  if (v.costType === "chh") {
    custoHora = v.chh;
    custoHoraLabel = "Custo Hora Homem (CHH)";
  } else if (v.costType === "chm") {
    custoHora = v.chm;
    custoHoraLabel = "Custo Hora Máquina (CHM)";
  } else {
    custoHora = v.chh + v.chm;
    custoHoraLabel = "Custo Hora do Processo (CHP)";
    steps.push(`Custo Hora do Processo = CHH + CHM = ${fmtCurrency(v.chh)} + ${fmtCurrency(v.chm)} = ${fmtCurrency(custoHora)}`);
  }

  const custoMensalRecurso = custoHora * v.horasDisp;
  const custoPecaAntes = v.prodAntes > 0 ? custoMensalRecurso / v.prodAntes : 0;
  const custoPecaDepois = v.prodDepois > 0 ? custoMensalRecurso / v.prodDepois : 0;
  const economiaPorPeca = custoPecaAntes - custoPecaDepois;
  const economiaMensal = economiaPorPeca * v.prodDepois;
  const economiaAnual = economiaMensal * (v.meses || 12);

  steps.push(
    `Custo mensal do recurso = ${custoHoraLabel} × Horas Disponíveis = ${fmtCurrency(custoHora)} × ${fmtNum(v.horasDisp,1)} h = ${fmtCurrency(custoMensalRecurso)}`,
    `Custo por peça Antes = Custo Mensal ÷ Produção Antes = ${fmtCurrency(custoMensalRecurso)} ÷ ${fmtNum(v.prodAntes,0)} = ${fmtCurrency(custoPecaAntes)}`,
    `Custo por peça Depois = Custo Mensal ÷ Produção Depois = ${fmtCurrency(custoMensalRecurso)} ÷ ${fmtNum(v.prodDepois,0)} = ${fmtCurrency(custoPecaDepois)}`,
    `Economia por peça = Custo Antes − Custo Depois = ${fmtCurrency(custoPecaAntes)} − ${fmtCurrency(custoPecaDepois)} = ${fmtCurrency(economiaPorPeca)}`,
    `Economia mensal = Economia por peça × Produção Depois = ${fmtCurrency(economiaPorPeca)} × ${fmtNum(v.prodDepois,0)} = ${fmtCurrency(economiaMensal)}`,
    `Economia anual = Economia mensal × ${v.meses || 12} meses = ${fmtCurrency(economiaAnual)}`,
  );

  return {
    outputs: { custoHora, custoHoraLabel, custoMensalRecurso, custoPecaAntes, custoPecaDepois, economiaPorPeca, economiaMensal, economiaAnual },
    annual: economiaAnual,
    steps,
  };
}

function calcG3(v) {
  const custoUnitAntes = v.cmp + (v.pctAntes / 100) * v.cmp;
  const custoUnitDepois = v.cmp + (v.pctDepois / 100) * v.cmp;
  const economiaPorPeca = custoUnitAntes - custoUnitDepois;
  const economiaMensal = economiaPorPeca * v.producaoMensal;
  const economiaAnual = economiaMensal * (v.meses || 12);
  return {
    outputs: { custoUnitAntes, custoUnitDepois, economiaPorPeca, economiaMensal, economiaAnual },
    annual: economiaAnual,
    steps: [
      `Custo unitário Antes = CMP + (%Quebra Antes × CMP) = ${fmtCurrency(v.cmp)} + (${fmtPercent(v.pctAntes)} × ${fmtCurrency(v.cmp)}) = ${fmtCurrency(custoUnitAntes)}`,
      `Custo unitário Depois = CMP + (%Quebra Depois × CMP) = ${fmtCurrency(v.cmp)} + (${fmtPercent(v.pctDepois)} × ${fmtCurrency(v.cmp)}) = ${fmtCurrency(custoUnitDepois)}`,
      `Economia por peça = Custo Antes − Custo Depois = ${fmtCurrency(custoUnitAntes)} − ${fmtCurrency(custoUnitDepois)} = ${fmtCurrency(economiaPorPeca)}`,
      `Economia mensal = Economia por peça × Produção Mensal = ${fmtCurrency(economiaPorPeca)} × ${fmtNum(v.producaoMensal,0)} = ${fmtCurrency(economiaMensal)}`,
      `Economia anual = Economia mensal × ${v.meses || 12} meses = ${fmtCurrency(economiaAnual)}`,
    ],
  };
}

function calcG4(v) {
  const economiaInvestimento = v.valorOrcado - v.valorRealizado;
  const economiaMensalRecorrente = v.valorMensalOrcado - v.valorMensalRealizado;
  const economiaAnualRecorrente = economiaMensalRecorrente * (v.meses || 12);
  const custoEvitadoTotal = economiaInvestimento + economiaAnualRecorrente;
  return {
    outputs: { economiaInvestimento, economiaMensalRecorrente, economiaAnualRecorrente, custoEvitadoTotal },
    annual: custoEvitadoTotal,
    steps: [
      `Economia do investimento = Valor Orçado − Valor Realizado = ${fmtCurrency(v.valorOrcado)} − ${fmtCurrency(v.valorRealizado)} = ${fmtCurrency(economiaInvestimento)}`,
      `Economia mensal recorrente = Valor Mensal Orçado − Valor Mensal Realizado = ${fmtCurrency(v.valorMensalOrcado)} − ${fmtCurrency(v.valorMensalRealizado)} = ${fmtCurrency(economiaMensalRecorrente)}`,
      `Economia recorrente anual = Economia mensal × ${v.meses || 12} meses = ${fmtCurrency(economiaAnualRecorrente)}`,
      `Custo evitado total = Economia do investimento + Economia recorrente anual = ${fmtCurrency(economiaInvestimento)} + ${fmtCurrency(economiaAnualRecorrente)} = ${fmtCurrency(custoEvitadoTotal)}`,
    ],
  };
}

const CALCULATORS = { g1: calcG1, g2: calcG2, g3: calcG3, g4: calcG4 };

/* ===================== Rendering: gain type cards ===================== */

function renderGainCards() {
  document.querySelectorAll(".gain-card").forEach((card) => {
    const gid = card.dataset.gain;
    card.classList.toggle("selected", state.active.has(gid));
    const badge = card.querySelector(".gain-count-badge");
    const count = state.instances[gid].length;
    badge.textContent = state.active.has(gid) && count > 1 ? String(count) : "";
  });
  renderForms();
  updateActionbarVisibility();
}

function toggleGain(gid) {
  if (state.active.has(gid)) state.active.delete(gid);
  else state.active.add(gid);
  renderGainCards();
}

function updateActionbarVisibility() {
  document.getElementById("actionbar").style.display = state.active.size ? "flex" : "none";
  if (!state.active.size) {
    document.getElementById("dashboard").style.display = "none";
    state.calculated = false;
  }
}

/* ===================== Rendering: dynamic forms (N instances per gain type) ===================== */

function fieldInputHtml(gid, uid, f) {
  const id = `${gid}_${uid}_${f.id}`;
  if (f.type === "currency") {
    return `<input type="text" inputmode="decimal" id="${id}" placeholder="${f.placeholder || "0,00"}" data-type="currency">`;
  }
  if (f.type === "percent") {
    return `<input type="text" inputmode="decimal" id="${id}" placeholder="${f.placeholder || "0%"}" data-type="percent">`;
  }
  return `<input type="number" id="${id}" step="${f.step || "any"}" min="${f.min ?? ""}" max="${f.max ?? ""}" value="${f.default ?? ""}" data-type="number">`;
}

function radioFieldHtml(gid, uid, f) {
  const opts = f.options.map((opt) => `
    <label class="radio-option">
      <input type="radio" name="${gid}_${uid}_${f.id}" value="${opt.value}" ${opt.value === f.default ? "checked" : ""}>
      <span>${opt.label}${opt.recommended ? ' <span class="badge badge-blue">Recomendado</span>' : ""}</span>
    </label>`).join("");
  return `
    <div class="field field-radio" id="fw_${gid}_${uid}_${f.id}" style="grid-column:1 / -1">
      <label>${f.label}</label>
      <div class="radio-group">${opts}</div>
    </div>`;
}

function isFieldVisible(gid, uid, f) {
  if (!f.visibleFor) return true;
  const def = GAIN_DEFS[gid];
  const radioField = def.fields.find((x) => x.type === "radio");
  const checked = radioField && document.querySelector(`input[name="${gid}_${uid}_${radioField.id}"]:checked`);
  const current = checked ? checked.value : radioField?.default;
  return f.visibleFor.includes(current);
}

function syncFieldVisibility(gid, uid) {
  const def = GAIN_DEFS[gid];
  def.fields.forEach((f) => {
    if (!f.visibleFor) return;
    const wrap = document.getElementById(`fw_${gid}_${uid}_${f.id}`);
    if (!wrap) return;
    const visible = isFieldVisible(gid, uid, f);
    wrap.style.display = visible ? "" : "none";
    if (!visible) {
      wrap.classList.remove("has-error");
      const el = document.getElementById(`${gid}_${uid}_${f.id}`);
      if (el) el.classList.remove("invalid");
    }
  });
}

function refreshInstanceNumbers(gid) {
  const def = GAIN_DEFS[gid];
  const container = document.getElementById(`instances_${gid}`);
  if (!container) return;
  Array.from(container.children).forEach((card, idx) => {
    const numEl = card.querySelector(".instance-number");
    if (numEl) numEl.textContent = `${def.code} · Kaizen #${idx + 1}`;
  });
}

function renderInstanceForm(gid, inst) {
  const def = GAIN_DEFS[gid];
  const container = document.getElementById(`instances_${gid}`);
  const card = document.createElement("div");
  card.className = `instance-card ${gid}`;
  card.id = `block_${gid}_${inst.uid}`;

  const groups = {};
  def.fields.forEach((f) => {
    const g = f.group || "__default";
    (groups[g] = groups[g] || []).push(f);
  });

  let fieldsHtml = "";
  Object.entries(groups).forEach(([groupName, fields]) => {
    if (groupName !== "__default") fieldsHtml += `<h4 style="margin:14px 0 8px;font-size:13px;color:var(--text-muted)">${groupName}</h4>`;
    fieldsHtml += `<div class="grid grid-4">`;
    fields.forEach((f) => {
      if (f.type === "radio") { fieldsHtml += radioFieldHtml(gid, inst.uid, f); return; }
      fieldsHtml += `
        <div class="field" id="fw_${gid}_${inst.uid}_${f.id}">
          <label for="${gid}_${inst.uid}_${f.id}">${f.label}</label>
          ${fieldInputHtml(gid, inst.uid, f)}
          <span class="error-msg">Informe um valor válido.</span>
        </div>`;
    });
    fieldsHtml += `</div>`;
  });

  card.innerHTML = `
    <div class="instance-header">
      <span class="instance-number">${def.code} · Kaizen</span>
      <div class="field">
        <label for="${gid}_${inst.uid}_name">Nome do Kaizen (opcional)</label>
        <input type="text" id="${gid}_${inst.uid}_name" placeholder="Ex.: Troca de ferramenta - Prensa 3">
      </div>
      <button type="button" class="remove-instance-btn" title="Remover este Kaizen">🗑</button>
    </div>
    ${fieldsHtml}
    <div class="gain-results grid grid-4" id="results_${gid}_${inst.uid}"></div>
  `;
  container.appendChild(card);

  def.fields.forEach((f) => {
    if (f.type === "radio") return;
    const el = document.getElementById(`${gid}_${inst.uid}_${f.id}`);
    if (f.type === "currency") el.addEventListener("input", maskCurrencyKeyup);
    if (f.type === "percent") {
      el.addEventListener("focus", maskPercentFocus);
      el.addEventListener("blur", maskPercentBlur);
    }
    if (f.default) el.value = f.type === "currency" ? "" : f.default;
  });

  const radioField = def.fields.find((f) => f.type === "radio");
  if (radioField) {
    document.querySelectorAll(`input[name="${gid}_${inst.uid}_${radioField.id}"]`).forEach((r) => {
      r.addEventListener("change", () => syncFieldVisibility(gid, inst.uid));
    });
    syncFieldVisibility(gid, inst.uid);
  }

  card.querySelector(".remove-instance-btn").addEventListener("click", () => removeInstance(gid, inst.uid));
  refreshInstanceNumbers(gid);
}

function addInstance(gid) {
  const inst = { uid: `i${instanceCounter++}` };
  state.instances[gid].push(inst);
  renderInstanceForm(gid, inst);
  const badge = document.querySelector(`.gain-count-badge[data-count-for="${gid}"]`);
  if (badge) badge.textContent = state.instances[gid].length > 1 ? String(state.instances[gid].length) : "";
  return inst;
}

function removeInstance(gid, uid) {
  state.instances[gid] = state.instances[gid].filter((i) => i.uid !== uid);
  const el = document.getElementById(`block_${gid}_${uid}`);
  if (el) el.remove();
  refreshInstanceNumbers(gid);
  const badge = document.querySelector(`.gain-count-badge[data-count-for="${gid}"]`);
  if (badge) badge.textContent = state.instances[gid].length > 1 ? String(state.instances[gid].length) : "";
}

function buildGainTypeSection(gid) {
  const def = GAIN_DEFS[gid];
  const section = document.createElement("section");
  section.className = "gain-type-section";
  section.dataset.gain = gid;
  section.innerHTML = `
    <div class="gain-type-header">
      <span class="gain-icon" style="background:${def.color === "blue" ? "#2563EB1a" : "#16A34A1a"};color:${def.color === "blue" ? "#2563EB" : "#16A34A"}">${def.icon}</span>
      <div>
        <h3>${def.code} — ${def.name}</h3>
        <p>${def.subtitle}</p>
      </div>
      <button type="button" class="btn btn-secondary add-instance-btn">+ Adicionar Kaizen ${def.code}</button>
    </div>
    <div class="gain-instances" id="instances_${gid}"></div>
  `;
  section.querySelector(".add-instance-btn").addEventListener("click", () => addInstance(gid));
  return section;
}

function renderForms() {
  const wrap = document.getElementById("formsWrap");
  GAIN_ORDER.forEach((gid) => {
    let section = wrap.querySelector(`section[data-gain="${gid}"]`);
    if (!state.active.has(gid)) {
      if (section) section.style.display = "none";
      return;
    }
    if (!section) {
      section = buildGainTypeSection(gid);
      wrap.appendChild(section);
      // Render any pre-existing instances (e.g. from loading a saved project) only after the
      // section is attached to the live document — renderInstanceForm looks up its container
      // via getElementById, which only finds nodes already in the document tree.
      state.instances[gid].forEach((inst) => renderInstanceForm(gid, inst));
    } else {
      section.style.display = "";
      wrap.appendChild(section);
    }
    if (state.instances[gid].length === 0) addInstance(gid);
  });
}

/* ===================== Validation ===================== */

function validateInstance(gid, uid) {
  const def = GAIN_DEFS[gid];
  let ok = true;
  def.fields.forEach((f) => {
    if (f.type === "radio") return;
    if (!isFieldVisible(gid, uid, f)) return;
    const wrap = document.getElementById(`fw_${gid}_${uid}_${f.id}`);
    const el = document.getElementById(`${gid}_${uid}_${f.id}`);
    let val;
    if (f.type === "currency") val = parseCurrencyInput(el.value);
    else if (f.type === "percent") val = parsePercentInput(el.value);
    else val = parseNumberInput(el.value);

    const invalid = el.value.trim() === "" || Number.isNaN(val) || val < 0;
    wrap.classList.toggle("has-error", invalid);
    el.classList.toggle("invalid", invalid);
    if (invalid) ok = false;
  });

  if (gid === "g2") {
    const prodAntes = parseNumberInput(document.getElementById(`g2_${uid}_prodAntes`).value);
    const prodDepois = parseNumberInput(document.getElementById(`g2_${uid}_prodDepois`).value);
    if (prodAntes <= 0 || prodDepois <= 0) {
      document.getElementById(`fw_g2_${uid}_prodAntes`).classList.add("has-error");
      document.getElementById(`fw_g2_${uid}_prodDepois`).classList.add("has-error");
      ok = false;
    }
  }
  return ok;
}

/* ===================== Calculate & render results ===================== */

function calculateAll() {
  let allValid = true;
  state.active.forEach((gid) => {
    state.instances[gid].forEach((inst) => { if (!validateInstance(gid, inst.uid)) allValid = false; });
  });
  if (!allValid) return;

  state.active.forEach((gid) => {
    state.instances[gid].forEach((inst) => {
      const v = readInstanceInputs(gid, inst.uid);
      const result = CALCULATORS[gid](v);
      inst.inputs = v;
      inst.result = result;
      const nameEl = document.getElementById(`${gid}_${inst.uid}_name`);
      inst.name = nameEl ? nameEl.value.trim() : "";
      renderInstanceMiniResults(gid, inst);
    });
  });

  state.calculated = true;
  renderDashboard();
  document.getElementById("dashboard").style.display = "flex";
  document.getElementById("dashboard").scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderInstanceMiniResults(gid, inst) {
  const box = document.getElementById(`results_${gid}_${inst.uid}`);
  if (!box) return;
  const result = inst.result;
  const map = {
    g1: [
      ["Horas Economizadas/mês", `${fmtNum(result.outputs.horasEconomizadasMes)} h`],
      ["Economia Mensal", fmtCurrency(result.outputs.economiaMensal)],
      ["Economia Anual", fmtCurrency(result.outputs.economiaAnual)],
    ],
    g2: [
      ["Custo Hora Considerado", `${fmtCurrency(result.outputs.custoHora)} (${result.outputs.custoHoraLabel})`],
      ["Custo/peça Antes", fmtCurrency(result.outputs.custoPecaAntes)],
      ["Custo/peça Depois", fmtCurrency(result.outputs.custoPecaDepois)],
      ["Economia por Peça", fmtCurrency(result.outputs.economiaPorPeca)],
      ["Economia Mensal", fmtCurrency(result.outputs.economiaMensal)],
      ["Economia Anual", fmtCurrency(result.outputs.economiaAnual)],
    ],
    g3: [
      ["Custo da Quebra Antes", fmtCurrency(result.outputs.custoUnitAntes)],
      ["Custo da Quebra Depois", fmtCurrency(result.outputs.custoUnitDepois)],
      ["Economia Anual", fmtCurrency(result.outputs.economiaAnual)],
    ],
    g4: [
      ["Economia do Investimento", fmtCurrency(result.outputs.economiaInvestimento)],
      ["Economia Recorrente Anual", fmtCurrency(result.outputs.economiaAnualRecorrente)],
      ["Custo Evitado Total", fmtCurrency(result.outputs.custoEvitadoTotal)],
    ],
  }[gid];

  box.innerHTML = map.map(([k, v]) => `<div class="mini-stat"><span class="k">${k}</span><span class="v">${v}</span></div>`).join("");
  box.classList.add("show");
}

/* ===================== Dashboard ===================== */

let pieChartInstance = null;
let barChartInstance = null;
let reportPieChartInstance = null;
let reportBarChartInstance = null;

function sumGidAnnual(gid) {
  if (!state.active.has(gid)) return 0;
  return state.instances[gid].reduce((s, inst) => s + (inst.result?.annual || 0), 0);
}
function countGidResults(gid) {
  if (!state.active.has(gid)) return 0;
  return state.instances[gid].filter((i) => i.result).length;
}
function getConsultingValue() {
  return parseCurrencyInput(document.getElementById("projConsulting").value);
}

function renderDashboard() {
  const kpiRow = document.getElementById("kpiRow");
  kpiRow.innerHTML = "";

  const totalAnual = GAIN_ORDER.reduce((sum, g) => sum + sumGidAnnual(g), 0);

  GAIN_ORDER.forEach((gid) => {
    const def = GAIN_DEFS[gid];
    const count = countGidResults(gid);
    const has = count > 0;
    const annual = sumGidAnnual(gid);
    const share = totalAnual > 0 ? (annual / totalAnual) * 100 : 0;
    const card = document.createElement("div");
    card.className = `card ${gid}`;
    card.innerHTML = `
      <span class="kpi-label">${def.icon} ${def.code} — ${def.name}</span>
      <span class="kpi-value">${has ? fmtCurrency(annual) : "—"}</span>
      <span class="kpi-sub">${has ? `${fmtPercent(share)} do total &middot; por ano${count > 1 ? ` &middot; <span class="kpi-count">${count} kaizens</span>` : ""}` : "Não calculado"}</span>
      <div class="kpi-bar"><span style="width:${share}%;background:${def.color === "blue" ? "var(--blue)" : "var(--green)"}"></span></div>
    `;
    kpiRow.appendChild(card);
  });

  document.getElementById("totalAnual").textContent = fmtCurrencyAno(totalAnual);
  document.getElementById("totalMensal").textContent = fmtCurrencyAno(totalAnual / 12).replace("por ano", "por mês (média)");

  renderRoiPayback(totalAnual);
  renderCharts();
  renderReportCharts();
  renderReport(totalAnual);
}

function renderRoiPayback(totalAnual) {
  const roiEl = document.getElementById("roiValue");
  const paybackEl = document.getElementById("paybackValue");
  const investimento = getConsultingValue();

  if (investimento > 0) {
    const ganhoMedioMensal = totalAnual / 12;
    const roi = (totalAnual / investimento) * 100;
    const paybackMeses = ganhoMedioMensal > 0 ? investimento / ganhoMedioMensal : Infinity;
    roiEl.textContent = `ROI ${fmtNum(roi, 1)}%`;
    let text = Number.isFinite(paybackMeses) ? `Payback em ${fmtNum(paybackMeses, 1)} meses` : "Payback indeterminado (sem ganho anual ainda)";
    const startDateStr = document.getElementById("projDate").value;
    if (startDateStr && Number.isFinite(paybackMeses)) {
      const returnDate = addMonthsApprox(startDateStr, paybackMeses);
      text += ` · retorno previsto em ${returnDate.toLocaleDateString("pt-BR")}`;
    }
    paybackEl.textContent = text;
  } else {
    roiEl.textContent = "—";
    paybackEl.textContent = "Informe o Valor da Consultoria em Dados do Projeto para calcular ROI e Payback";
  }
}

function chartColors() {
  return {
    g1: "#2563EB", g2: "#60A5FA", g3: "#16A34A", g4: "#4ADE80",
    text: getComputedStyle(document.documentElement).getPropertyValue("--text").trim() || "#0F172A",
    grid: getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#E2E8F0",
  };
}

function buildChartSeries(colorMap) {
  const labels = [];
  const data = [];
  const bg = [];
  GAIN_ORDER.forEach((gid) => {
    if (state.active.has(gid) && countGidResults(gid) > 0) {
      labels.push(`${GAIN_DEFS[gid].code} — ${GAIN_DEFS[gid].name}`);
      data.push(Math.max(0, sumGidAnnual(gid)));
      bg.push(colorMap[gid]);
    }
  });
  return { labels, data, bg };
}

function renderCharts() {
  const colors = chartColors();
  const { labels, data, bg } = buildChartSeries(colors);

  const pieCtx = document.getElementById("pieChart").getContext("2d");
  if (pieChartInstance) pieChartInstance.destroy();
  pieChartInstance = new Chart(pieCtx, {
    type: "pie",
    data: { labels, datasets: [{ data, backgroundColor: bg, borderColor: getComputedStyle(document.documentElement).getPropertyValue("--surface"), borderWidth: 2 }] },
    options: {
      plugins: {
        legend: { position: "bottom", labels: { color: colors.text, boxWidth: 14, font: { size: 11.5 } } },
        tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${fmtCurrency(ctx.parsed)}` } },
      },
    },
  });

  const barCtx = document.getElementById("barChart").getContext("2d");
  if (barChartInstance) barChartInstance.destroy();
  barChartInstance = new Chart(barCtx, {
    type: "bar",
    data: { labels, datasets: [{ label: "Ganho Anual (R$)", data, backgroundColor: bg, borderRadius: 6 }] },
    options: {
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => fmtCurrency(ctx.parsed.y) } } },
      scales: {
        x: { ticks: { color: colors.text, font: { size: 11 } }, grid: { display: false } },
        y: { ticks: { color: colors.text, callback: (v) => fmtCurrency(v) }, grid: { color: colors.grid } },
      },
    },
  });
}

// Fixed light-theme colors so the report/PDF/print output always looks correct on white paper,
// regardless of the on-screen dark/light theme.
function renderReportCharts() {
  const fixedColors = { g1: "#2563EB", g2: "#60A5FA", g3: "#16A34A", g4: "#4ADE80" };
  const { labels, data, bg } = buildChartSeries(fixedColors);

  const pieCtx = document.getElementById("reportPieChart").getContext("2d");
  if (reportPieChartInstance) reportPieChartInstance.destroy();
  reportPieChartInstance = new Chart(pieCtx, {
    type: "pie",
    data: { labels, datasets: [{ data, backgroundColor: bg, borderColor: "#ffffff", borderWidth: 2 }] },
    options: {
      responsive: false, animation: false,
      plugins: { legend: { position: "bottom", labels: { color: "#0F172A", boxWidth: 12, font: { size: 10.5 } } } },
    },
  });

  const barCtx = document.getElementById("reportBarChart").getContext("2d");
  if (reportBarChartInstance) reportBarChartInstance.destroy();
  reportBarChartInstance = new Chart(barCtx, {
    type: "bar",
    data: { labels, datasets: [{ label: "Ganho Anual (R$)", data, backgroundColor: bg, borderRadius: 6 }] },
    options: {
      responsive: false, animation: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#0F172A", font: { size: 10 } }, grid: { display: false } },
        y: { ticks: { color: "#0F172A", callback: (v) => fmtCurrency(v), font: { size: 10 } }, grid: { color: "#E2E8F0" } },
      },
    },
  });
}

/* ===================== Executive report ===================== */

function renderReport(totalAnual) {
  const name = document.getElementById("projName").value || "(sem nome definido)";
  const company = document.getElementById("projCompany").value || "(empresa não informada)";
  const responsible = document.getElementById("projResponsible").value || "(responsável não informado)";
  const startDateStr = document.getElementById("projDate").value;
  const endDateStr = document.getElementById("projEndDate").value;
  const consulting = getConsultingValue();

  const startDate = startDateStr ? new Date(startDateStr + "T00:00:00") : null;
  const endDate = endDateStr ? new Date(endDateStr + "T00:00:00") : null;
  let durationText = "";
  if (startDate && endDate && endDate >= startDate) {
    const months = (endDate.getFullYear() - startDate.getFullYear()) * 12 + (endDate.getMonth() - startDate.getMonth());
    durationText = ` &middot; Duração: ${months} ${months === 1 ? "mês" : "meses"}`;
  }

  document.getElementById("reportMeta").innerHTML = `
    <strong>${name}</strong><br>
    ${company}<br>
    Responsável: ${responsible}<br>
    Início: ${startDate ? startDate.toLocaleDateString("pt-BR") : "—"}${endDate ? ` &middot; Fim: ${endDate.toLocaleDateString("pt-BR")}` : ""}${durationText}<br>
    ${consulting > 0 ? `Valor da Consultoria: ${fmtCurrency(consulting)}` : ""}
  `;

  const activeGids = GAIN_ORDER.filter((g) => state.active.has(g) && countGidResults(g) > 0);
  const selectedNames = activeGids.map((g) => `${GAIN_DEFS[g].code} — ${GAIN_DEFS[g].name} (${countGidResults(g)} ${countGidResults(g) === 1 ? "kaizen" : "kaizens"})`);
  document.getElementById("reportGainsSelected").textContent = selectedNames.join(" · ") || "Nenhum ganho calculado.";

  const memoryWrap = document.getElementById("reportMemory");
  memoryWrap.innerHTML = "<h3>Memória de Cálculo</h3>" + activeGids.map((gid) => {
    const def = GAIN_DEFS[gid];
    return state.instances[gid].filter((i) => i.result).map((inst, idx) => {
      const label = inst.name ? `${def.code} · Kaizen #${idx + 1} — ${inst.name}` : `${def.code} · Kaizen #${idx + 1}`;
      return `
        <div class="memory-block">
          <h4>${def.icon} ${label}</h4>
          <ol>${inst.result.steps.map((s) => `<li>${s}</li>`).join("")}</ol>
          <div class="result-line">Resultado: ${fmtCurrencyAno(inst.result.annual)}</div>
        </div>`;
    }).join("");
  }).join("");

  const rows = [];
  activeGids.forEach((gid) => {
    const def = GAIN_DEFS[gid];
    const insts = state.instances[gid].filter((i) => i.result);
    insts.forEach((inst, idx) => {
      const share = totalAnual > 0 ? (inst.result.annual / totalAnual) * 100 : 0;
      const label = inst.name ? `${def.code} · Kaizen #${idx + 1} — ${inst.name}` : `${def.code} · Kaizen #${idx + 1}`;
      rows.push(`<tr><td>${label}</td><td>${fmtCurrency(inst.result.annual)}</td><td>${fmtPercent(share)}</td></tr>`);
    });
    if (insts.length > 1) {
      const subtotal = insts.reduce((s, i) => s + i.result.annual, 0);
      const share = totalAnual > 0 ? (subtotal / totalAnual) * 100 : 0;
      rows.push(`<tr class="subtotal-row"><td>Subtotal ${def.code}</td><td>${fmtCurrency(subtotal)}</td><td>${fmtPercent(share)}</td></tr>`);
    }
  });

  const roiRows = consulting > 0
    ? `<tr><td>Valor da Consultoria (Investimento)</td><td colspan="2">${fmtCurrency(consulting)}</td></tr>
       <tr><td>ROI</td><td colspan="2">${fmtNum((totalAnual / consulting) * 100, 1)}%</td></tr>
       <tr><td>Payback</td><td colspan="2">${totalAnual > 0 ? fmtNum(consulting / (totalAnual / 12), 1) + " meses" : "indeterminado"}</td></tr>`
    : "";

  document.getElementById("reportTotalsTable").innerHTML = `
    <thead><tr><th>Kaizen</th><th>Valor Anual</th><th>Participação</th></tr></thead>
    <tbody>
      ${rows.join("")}
      <tr style="font-weight:800"><td>Ganho Anual Total</td><td colspan="2">${fmtCurrency(totalAnual)}</td></tr>
      <tr><td>Ganho Médio Mensal</td><td colspan="2">${fmtCurrency(totalAnual / 12)}</td></tr>
      ${roiRows}
    </tbody>
  `;

  const flatInstances = [];
  activeGids.forEach((gid) => state.instances[gid].filter((i) => i.result).forEach((inst) => flatInstances.push({ gid, inst })));
  const top = flatInstances.sort((a, b) => b.inst.result.annual - a.inst.result.annual)[0];
  const conclusion = top
    ? `O projeto Kaizen "${name}" apresenta um ganho financeiro anual total estimado em ${fmtCurrency(totalAnual)}, equivalente a uma média mensal de ${fmtCurrency(totalAnual / 12)}, distribuído em ${flatInstances.length} ${flatInstances.length === 1 ? "iniciativa Kaizen" : "iniciativas Kaizen"}. ` +
      `A de maior impacto é ${GAIN_DEFS[top.gid].code}${top.inst.name ? ` — ${top.inst.name}` : ""}, responsável por ${fmtPercent(totalAnual > 0 ? (top.inst.result.annual / totalAnual) * 100 : 0)} do resultado total. ` +
      (consulting > 0
        ? `Considerando o valor da consultoria de ${fmtCurrency(consulting)}, o projeto apresenta ROI de ${fmtNum((totalAnual / consulting) * 100, 1)}% ao ano${totalAnual > 0 ? `, com payback estimado em ${fmtNum(consulting / (totalAnual / 12), 1)} meses` : ""}. `
        : "") +
      `Recomenda-se validar os dados de entrada com a equipe operacional e acompanhar a realização efetiva dos ganhos nos próximos ciclos de PPCP.`
    : "Nenhum ganho foi calculado ainda.";
  document.getElementById("reportConclusion").textContent = conclusion;
}

/* ===================== Theme ===================== */

function initTheme() {
  const saved = localStorage.getItem("kaizen_theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  updateThemeButton();
}
function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("kaizen_theme", next);
  updateThemeButton();
  if (state.calculated) renderCharts();
}
function updateThemeButton() {
  const current = document.documentElement.getAttribute("data-theme") ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document.getElementById("themeToggle").textContent = current === "dark" ? "☀️ Tema" : "🌙 Tema";
}

/* ===================== Clear ===================== */

function clearAll() {
  if (!confirm("Deseja limpar todos os campos e resultados?")) return;
  document.getElementById("projName").value = "";
  document.getElementById("projCompany").value = "";
  document.getElementById("projResponsible").value = "";
  document.getElementById("projConsulting").value = "";
  document.getElementById("projDate").value = "";
  document.getElementById("projEndDate").value = "";
  state.active.clear();
  state.instances = { g1: [], g2: [], g3: [], g4: [] };
  state.calculated = false;
  document.getElementById("formsWrap").innerHTML = "";
  document.getElementById("dashboard").style.display = "none";
  renderGainCards();
}

/* ===================== History (localStorage) ===================== */

const HISTORY_KEY = "kaizen_projects_history";

function getHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; } catch { return []; }
}
function setHistory(list) { localStorage.setItem(HISTORY_KEY, JSON.stringify(list)); }

function saveProject() {
  if (!state.calculated) { alert("Calcule os resultados antes de salvar o projeto."); return; }
  const project = {
    id: `proj_${Date.now()}`,
    name: document.getElementById("projName").value || "Projeto Kaizen sem nome",
    company: document.getElementById("projCompany").value,
    responsible: document.getElementById("projResponsible").value,
    date: document.getElementById("projDate").value || new Date().toISOString().slice(0, 10),
    endDate: document.getElementById("projEndDate").value || "",
    consulting: getConsultingValue(),
    savedAt: new Date().toISOString(),
    active: Array.from(state.active),
    instances: {},
  };
  GAIN_ORDER.forEach((gid) => {
    project.instances[gid] = state.instances[gid].filter((i) => i.result).map((inst) => ({
      uid: inst.uid,
      name: inst.name || "",
      inputs: inst.inputs,
      result: inst.result,
    }));
  });
  const list = getHistory();
  list.unshift(project);
  setHistory(list);
  renderHistoryList();
  alert("Projeto salvo no histórico local.");
}

function renderHistoryList() {
  const list = getHistory();
  const wrap = document.getElementById("historyList");
  if (!list.length) {
    wrap.innerHTML = `<div class="history-empty">Nenhum projeto salvo ainda.</div>`;
    return;
  }
  wrap.innerHTML = list.map((p) => {
    const total = GAIN_ORDER.reduce((s, gid) => s + (p.instances[gid] || []).reduce((s2, i) => s2 + (i.result?.annual || 0), 0), 0);
    const kaizenCount = GAIN_ORDER.reduce((s, gid) => s + (p.instances[gid] || []).length, 0);
    return `
      <div class="history-item">
        <div class="hi-name">${p.name}</div>
        <div class="hi-meta">${p.company || "—"} &middot; ${new Date(p.date + "T00:00:00").toLocaleDateString("pt-BR")} &middot; ${kaizenCount} ${kaizenCount === 1 ? "kaizen" : "kaizens"}<br>
          Ganho anual total: ${fmtCurrency(total)}</div>
        <div class="hi-actions">
          <button class="btn btn-secondary" data-load="${p.id}">Carregar</button>
          <button class="btn btn-danger" data-del="${p.id}">Excluir</button>
        </div>
      </div>`;
  }).join("");

  wrap.querySelectorAll("[data-load]").forEach((btn) => btn.addEventListener("click", () => loadProject(btn.dataset.load)));
  wrap.querySelectorAll("[data-del]").forEach((btn) => btn.addEventListener("click", () => deleteProject(btn.dataset.del)));
}

function loadProject(id) {
  const p = getHistory().find((x) => x.id === id);
  if (!p) return;
  document.getElementById("projName").value = p.name;
  document.getElementById("projCompany").value = p.company;
  document.getElementById("projResponsible").value = p.responsible;
  document.getElementById("projDate").value = p.date;
  document.getElementById("projEndDate").value = p.endDate || "";
  document.getElementById("projConsulting").value = p.consulting ? NUM2.format(p.consulting).replace(/[^\d,.-]/g, "") : "";

  state.active = new Set(p.active);
  state.instances = { g1: [], g2: [], g3: [], g4: [] };
  GAIN_ORDER.forEach((gid) => {
    state.instances[gid] = (p.instances[gid] || []).map((i) => ({ uid: i.uid }));
  });
  document.getElementById("formsWrap").innerHTML = "";
  renderGainCards();

  GAIN_ORDER.forEach((gid) => {
    (p.instances[gid] || []).forEach((saved, idx) => {
      const inst = state.instances[gid][idx];
      inst.inputs = saved.inputs;
      inst.result = saved.result;
      inst.name = saved.name || "";
      const nameEl = document.getElementById(`${gid}_${inst.uid}_name`);
      if (nameEl) nameEl.value = inst.name;
      const def = GAIN_DEFS[gid];
      def.fields.forEach((f) => {
        if (f.type === "radio") {
          const val = saved.inputs?.[f.id] || f.default;
          const radio = document.querySelector(`input[name="${gid}_${inst.uid}_${f.id}"][value="${val}"]`);
          if (radio) radio.checked = true;
          return;
        }
        const el = document.getElementById(`${gid}_${inst.uid}_${f.id}`);
        if (!el) return;
        const val = saved.inputs?.[f.id];
        if (f.type === "currency") el.value = val ? NUM2.format(val).replace(/[^\d,.-]/g, "") : "";
        else if (f.type === "percent") el.value = val ? `${fmtNum(val, 1)}%` : "";
        else el.value = val ?? f.default ?? "";
      });
      syncFieldVisibility(gid, inst.uid);
      renderInstanceMiniResults(gid, inst);
    });
  });

  state.calculated = true;
  renderDashboard();
  document.getElementById("dashboard").style.display = "flex";
  closeHistoryPanel();
}

function deleteProject(id) {
  setHistory(getHistory().filter((p) => p.id !== id));
  renderHistoryList();
}

function openHistoryPanel() {
  renderHistoryList();
  document.getElementById("historyPanel").classList.add("open");
  document.getElementById("overlay").classList.add("show");
}
function closeHistoryPanel() {
  document.getElementById("historyPanel").classList.remove("open");
  document.getElementById("overlay").classList.remove("show");
}

/* ===================== Export: PDF / Excel / Print ===================== */

async function exportPdf() {
  if (!state.calculated) { alert("Calcule os resultados antes de exportar."); return; }
  const { jsPDF } = window.jspdf;
  const reportEl = document.getElementById("reportArea");
  const canvas = await html2canvas(reportEl, { scale: 1.5, backgroundColor: "#ffffff" });
  const imgData = canvas.toDataURL("image/jpeg", 0.92);

  const pdf = new jsPDF("p", "mm", "a4");
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const imgWidth = pageWidth - 20;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = 10;
  pdf.addImage(imgData, "JPEG", 10, position, imgWidth, imgHeight);
  heightLeft -= (pageHeight - 20);

  while (heightLeft > 0) {
    position = heightLeft - imgHeight + 10;
    pdf.addPage();
    pdf.addImage(imgData, "JPEG", 10, position, imgWidth, imgHeight);
    heightLeft -= (pageHeight - 20);
  }

  const projName = document.getElementById("projName").value || "kaizen";
  pdf.save(`Relatorio_KAIZEN_${projName.replace(/\s+/g, "_")}.pdf`);
}

function exportExcel() {
  if (!state.calculated) { alert("Calcule os resultados antes de exportar."); return; }
  const wb = XLSX.utils.book_new();

  const totalAnual = GAIN_ORDER.reduce((sum, g) => sum + sumGidAnnual(g), 0);
  const consulting = getConsultingValue();

  const resumo = [
    ["Relatório Executivo Kaizen"],
    ["Projeto", document.getElementById("projName").value],
    ["Empresa", document.getElementById("projCompany").value],
    ["Responsável", document.getElementById("projResponsible").value],
    ["Data Início", document.getElementById("projDate").value],
    ["Data Fim", document.getElementById("projEndDate").value],
    ["Valor da Consultoria", consulting],
    [],
    ["Kaizen", "Tipo", "Valor Anual (R$)", "Participação (%)"],
  ];

  GAIN_ORDER.forEach((gid) => {
    if (!state.active.has(gid)) return;
    const def = GAIN_DEFS[gid];
    state.instances[gid].filter((i) => i.result).forEach((inst, idx) => {
      resumo.push([
        inst.name || `Kaizen #${idx + 1}`,
        `${def.code} — ${def.name}`,
        Number(inst.result.annual.toFixed(2)),
        totalAnual > 0 ? Number(((inst.result.annual / totalAnual) * 100).toFixed(2)) : 0,
      ]);
    });
  });

  resumo.push([]);
  resumo.push(["Ganho Anual Total", "", Number(totalAnual.toFixed(2))]);
  resumo.push(["Ganho Médio Mensal", "", Number((totalAnual / 12).toFixed(2))]);
  if (consulting > 0) {
    resumo.push(["ROI (%)", "", Number(((totalAnual / consulting) * 100).toFixed(2))]);
    if (totalAnual > 0) resumo.push(["Payback (meses)", "", Number((consulting / (totalAnual / 12)).toFixed(2))]);
  }
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(resumo), "Resumo");

  GAIN_ORDER.forEach((gid) => {
    if (!state.active.has(gid)) return;
    const insts = state.instances[gid].filter((i) => i.result);
    if (!insts.length) return;
    const def = GAIN_DEFS[gid];
    const sheet = [[`${def.code} — ${def.name}`], []];
    insts.forEach((inst, idx) => {
      sheet.push([`Kaizen #${idx + 1}${inst.name ? " — " + inst.name : ""}`]);
      sheet.push(["Entradas"]);
      Object.entries(inst.inputs).forEach(([k, v]) => sheet.push([k, v]));
      sheet.push([]);
      sheet.push(["Memória de Cálculo"]);
      inst.result.steps.forEach((s) => sheet.push([s]));
      sheet.push(["Resultado Anual (R$)", Number(inst.result.annual.toFixed(2))]);
      sheet.push([]);
    });
    XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(sheet), def.code);
  });

  const projName = document.getElementById("projName").value || "kaizen";
  XLSX.writeFile(wb, `Resultados_KAIZEN_${projName.replace(/\s+/g, "_")}.xlsx`);
}

/* ===================== Event wiring ===================== */

function init() {
  initTheme();
  document.getElementById("projDate").value = new Date().toISOString().slice(0, 10);

  document.querySelectorAll(".gain-card").forEach((card) => {
    card.addEventListener("click", () => toggleGain(card.dataset.gain));
  });
  document.getElementById("selectAllGains").addEventListener("click", () => {
    GAIN_ORDER.forEach((g) => state.active.add(g));
    renderGainCards();
  });
  document.getElementById("clearSelection").addEventListener("click", () => {
    state.active.clear();
    renderGainCards();
  });

  document.getElementById("calcBtn").addEventListener("click", calculateAll);
  document.getElementById("clearBtn").addEventListener("click", clearAll);
  document.getElementById("saveBtn").addEventListener("click", saveProject);
  document.getElementById("exportPdfBtn").addEventListener("click", exportPdf);
  document.getElementById("exportXlsBtn").addEventListener("click", exportExcel);
  document.getElementById("printBtn").addEventListener("click", () => window.print());

  document.getElementById("themeToggle").addEventListener("click", toggleTheme);
  document.getElementById("historyToggle").addEventListener("click", openHistoryPanel);
  document.getElementById("closeHistory").addEventListener("click", closeHistoryPanel);
  document.getElementById("overlay").addEventListener("click", closeHistoryPanel);

  document.getElementById("projConsulting").addEventListener("input", maskCurrencyKeyup);

  ["projName", "projCompany", "projResponsible", "projDate", "projEndDate", "projConsulting"].forEach((id) => {
    document.getElementById(id).addEventListener("input", () => {
      if (state.calculated) renderReport(GAIN_ORDER.reduce((s, g) => s + sumGidAnnual(g), 0));
    });
  });

  renderGainCards();
}

document.addEventListener("DOMContentLoaded", init);
