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

/* ===================== Gain definitions ===================== */

const GAIN_DEFS = {
  g1: {
    code: "G1", name: "Redução do Tempo Operacional", icon: "⏱", color: "blue",
    subtitle: "Economia de mão de obra pela redução do tempo de execução de uma atividade.",
    fields: [
      { id: "cmo", label: "Custo da Mão de Obra por Hora (CMO)", type: "currency", placeholder: "0,00" },
      { id: "tempoAntes", label: "Tempo Antes (horas)", type: "number", step: "0.001", min: 0 },
      { id: "tempoDepois", label: "Tempo Depois (horas)", type: "number", step: "0.001", min: 0 },
      { id: "freq", label: "Frequência Mensal da Atividade", type: "number", step: "1", min: 0 },
      { id: "meses", label: "Meses por Ano", type: "number", step: "1", min: 1, max: 12, default: 12 },
    ],
  },
  g2: {
    code: "G2", name: "Aumento de Produtividade da Máquina", icon: "⚙️", color: "blue",
    subtitle: "Ganho pelo melhor aproveitamento da capacidade produtiva do equipamento, via Custo Hora Máquina (CHM).",
    fields: [
      { id: "chm", label: "Custo Hora Máquina (CHM)", type: "currency", placeholder: "0,00" },
      { id: "prodAntes", label: "Produção Antes (peças/mês)", type: "number", step: "1", min: 0 },
      { id: "prodDepois", label: "Produção Depois (peças/mês)", type: "number", step: "1", min: 0 },
      { id: "horasDisp", label: "Horas Disponíveis da Máquina por Mês", type: "number", step: "0.1", min: 0 },
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

const state = {
  selected: new Set(),
  results: {},   // gainId -> {outputs, annual, steps, inputs}
  calculated: false,
};

/* ===================== Calculation engine ===================== */

function readGainInputs(gainId) {
  const def = GAIN_DEFS[gainId];
  const values = {};
  for (const f of def.fields) {
    const el = document.getElementById(`${gainId}_${f.id}`);
    if (!el) { values[f.id] = f.default || 0; continue; }
    if (f.type === "currency") values[f.id] = parseCurrencyInput(el.value);
    else if (f.type === "percent") values[f.id] = parsePercentInput(el.value);
    else values[f.id] = parseNumberInput(el.value);
  }
  return values;
}

function calcG1(v) {
  const tempoEconomizado = v.tempoAntes - v.tempoDepois;
  const horasEconomizadasMes = tempoEconomizado * v.freq;
  const economiaMensal = horasEconomizadasMes * v.cmo;
  const economiaAnual = economiaMensal * (v.meses || 12);
  return {
    outputs: { tempoEconomizado, horasEconomizadasMes, economiaMensal, economiaAnual },
    annual: economiaAnual,
    steps: [
      `Tempo economizado por execução = Tempo Antes − Tempo Depois = ${fmtNum(v.tempoAntes,3)} h − ${fmtNum(v.tempoDepois,3)} h = ${fmtNum(tempoEconomizado,3)} h`,
      `Horas economizadas/mês = Tempo economizado × Frequência Mensal = ${fmtNum(tempoEconomizado,3)} h × ${fmtNum(v.freq,0)} = ${fmtNum(horasEconomizadasMes,2)} h/mês`,
      `Economia mensal = Horas economizadas × CMO/h = ${fmtNum(horasEconomizadasMes,2)} h × ${fmtCurrency(v.cmo)} = ${fmtCurrency(economiaMensal)}`,
      `Economia anual = Economia mensal × ${v.meses || 12} meses = ${fmtCurrency(economiaAnual)}`,
    ],
  };
}

function calcG2(v) {
  const custoMensalMaquina = v.chm * v.horasDisp;
  const custoPecaAntes = v.prodAntes > 0 ? custoMensalMaquina / v.prodAntes : 0;
  const custoPecaDepois = v.prodDepois > 0 ? custoMensalMaquina / v.prodDepois : 0;
  const economiaPorPeca = custoPecaAntes - custoPecaDepois;
  const economiaMensal = economiaPorPeca * v.prodDepois;
  const economiaAnual = economiaMensal * (v.meses || 12);
  return {
    outputs: { custoMensalMaquina, custoPecaAntes, custoPecaDepois, economiaPorPeca, economiaMensal, economiaAnual },
    annual: economiaAnual,
    steps: [
      `Custo mensal da máquina = CHM × Horas Disponíveis = ${fmtCurrency(v.chm)} × ${fmtNum(v.horasDisp,1)} h = ${fmtCurrency(custoMensalMaquina)}`,
      `Custo por peça Antes = Custo Mensal ÷ Produção Antes = ${fmtCurrency(custoMensalMaquina)} ÷ ${fmtNum(v.prodAntes,0)} = ${fmtCurrency(custoPecaAntes)}`,
      `Custo por peça Depois = Custo Mensal ÷ Produção Depois = ${fmtCurrency(custoMensalMaquina)} ÷ ${fmtNum(v.prodDepois,0)} = ${fmtCurrency(custoPecaDepois)}`,
      `Economia por peça = Custo Antes − Custo Depois = ${fmtCurrency(custoPecaAntes)} − ${fmtCurrency(custoPecaDepois)} = ${fmtCurrency(economiaPorPeca)}`,
      `Economia mensal = Economia por peça × Produção Depois = ${fmtCurrency(economiaPorPeca)} × ${fmtNum(v.prodDepois,0)} = ${fmtCurrency(economiaMensal)}`,
      `Economia anual = Economia mensal × ${v.meses || 12} meses = ${fmtCurrency(economiaAnual)}`,
    ],
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

/* ===================== Rendering: gain cards ===================== */

function renderGainCards() {
  document.querySelectorAll(".gain-card").forEach((card) => {
    const gid = card.dataset.gain;
    card.classList.toggle("selected", state.selected.has(gid));
  });
  renderForms();
  updateActionbarVisibility();
}

function toggleGain(gid) {
  if (state.selected.has(gid)) state.selected.delete(gid);
  else state.selected.add(gid);
  renderGainCards();
}

function updateActionbarVisibility() {
  document.getElementById("actionbar").style.display = state.selected.size ? "flex" : "none";
  if (!state.selected.size) {
    document.getElementById("dashboard").style.display = "none";
    state.calculated = false;
  }
}

/* ===================== Rendering: dynamic forms ===================== */

function fieldInputHtml(gainId, f) {
  const id = `${gainId}_${f.id}`;
  if (f.type === "currency") {
    return `<input type="text" inputmode="decimal" id="${id}" placeholder="${f.placeholder || "0,00"}" data-type="currency">`;
  }
  if (f.type === "percent") {
    return `<input type="text" inputmode="decimal" id="${id}" placeholder="${f.placeholder || "0%"}" data-type="percent">`;
  }
  return `<input type="number" id="${id}" step="${f.step || "any"}" min="${f.min ?? ""}" max="${f.max ?? ""}" value="${f.default ?? ""}" data-type="number">`;
}

function renderForms() {
  const wrap = document.getElementById("formsWrap");
  wrap.innerHTML = "";

  GAIN_ORDER.filter((g) => state.selected.has(g)).forEach((gid) => {
    const def = GAIN_DEFS[gid];
    const section = document.createElement("section");
    section.className = "card gain-form " + gid;

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
        fieldsHtml += `
          <div class="field" id="fw_${gid}_${f.id}">
            <label for="${gid}_${f.id}">${f.label}</label>
            ${fieldInputHtml(gid, f)}
            <span class="error-msg">Informe um valor válido.</span>
          </div>`;
      });
      fieldsHtml += `</div>`;
    });

    section.innerHTML = `
      <div class="gain-form-header">
        <span class="gain-icon" style="background:${def.color === "blue" ? "#2563EB1a" : "#16A34A1a"};color:${def.color === "blue" ? "#2563EB" : "#16A34A"}">${def.icon}</span>
        <div>
          <h3>${def.code} — ${def.name}</h3>
          <p>${def.subtitle}</p>
        </div>
      </div>
      ${fieldsHtml}
      <div class="gain-results grid grid-4" id="results_${gid}"></div>
    `;
    wrap.appendChild(section);

    def.fields.forEach((f) => {
      const el = document.getElementById(`${gid}_${f.id}`);
      if (f.type === "currency") el.addEventListener("input", maskCurrencyKeyup);
      if (f.type === "percent") {
        el.addEventListener("focus", maskPercentFocus);
        el.addEventListener("blur", maskPercentBlur);
      }
      if (f.default) el.value = f.type === "currency" ? "" : f.default;
    });
  });
}

/* ===================== Validation ===================== */

function validateGain(gainId) {
  const def = GAIN_DEFS[gainId];
  let ok = true;
  def.fields.forEach((f) => {
    const wrap = document.getElementById(`fw_${gainId}_${f.id}`);
    const el = document.getElementById(`${gainId}_${f.id}`);
    let val;
    if (f.type === "currency") val = parseCurrencyInput(el.value);
    else if (f.type === "percent") val = parsePercentInput(el.value);
    else val = parseNumberInput(el.value);

    const isRequired = true;
    const invalid = isRequired && (el.value.trim() === "" || Number.isNaN(val) || val < 0);
    wrap.classList.toggle("has-error", invalid);
    el.classList.toggle("invalid", invalid);
    if (invalid) ok = false;
  });

  // Gain-specific guards against divide-by-zero
  if (gainId === "g2") {
    const prodAntes = parseNumberInput(document.getElementById("g2_prodAntes").value);
    const prodDepois = parseNumberInput(document.getElementById("g2_prodDepois").value);
    if (prodAntes <= 0 || prodDepois <= 0) {
      document.getElementById("fw_g2_prodAntes").classList.add("has-error");
      document.getElementById("fw_g2_prodDepois").classList.add("has-error");
      ok = false;
    }
  }
  return ok;
}

/* ===================== Calculate & render results ===================== */

function calculateAll() {
  let allValid = true;
  state.selected.forEach((gid) => { if (!validateGain(gid)) allValid = false; });
  if (!allValid) return;

  state.results = {};
  state.selected.forEach((gid) => {
    const inputs = readGainInputs(gid);
    const result = CALCULATORS[gid](inputs);
    state.results[gid] = { ...result, inputs };
    renderGainMiniResults(gid, result);
  });

  state.calculated = true;
  renderDashboard();
  document.getElementById("dashboard").style.display = "flex";
  document.getElementById("dashboard").scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderGainMiniResults(gid, result) {
  const box = document.getElementById(`results_${gid}`);
  const map = {
    g1: [
      ["Horas Economizadas/mês", `${fmtNum(result.outputs.horasEconomizadasMes)} h`],
      ["Economia Mensal", fmtCurrency(result.outputs.economiaMensal)],
      ["Economia Anual", fmtCurrency(result.outputs.economiaAnual)],
    ],
    g2: [
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

function renderDashboard() {
  const kpiRow = document.getElementById("kpiRow");
  kpiRow.innerHTML = "";

  const totalAnual = GAIN_ORDER.reduce((sum, g) => sum + (state.results[g]?.annual || 0), 0);

  GAIN_ORDER.forEach((gid) => {
    const def = GAIN_DEFS[gid];
    const has = !!state.results[gid];
    const annual = has ? state.results[gid].annual : 0;
    const share = totalAnual > 0 ? (annual / totalAnual) * 100 : 0;
    const card = document.createElement("div");
    card.className = `card ${gid}`;
    card.innerHTML = `
      <span class="kpi-label">${def.icon} ${def.code} — ${def.name}</span>
      <span class="kpi-value">${has ? fmtCurrency(annual) : "—"}</span>
      <span class="kpi-sub">${has ? `${fmtPercent(share)} do total &middot; por ano` : "Não calculado"}</span>
      <div class="kpi-bar"><span style="width:${share}%;background:${def.color === "blue" ? "var(--blue)" : "var(--green)"}"></span></div>
    `;
    kpiRow.appendChild(card);
  });

  document.getElementById("totalAnual").textContent = fmtCurrencyAno(totalAnual);
  document.getElementById("totalMensal").textContent = fmtCurrencyAno(totalAnual / 12).replace("por ano", "por mês (média)");

  renderRoiPayback(totalAnual);
  renderCharts();
  renderReport(totalAnual);
}

function renderRoiPayback(totalAnual) {
  const roiEl = document.getElementById("roiValue");
  const paybackEl = document.getElementById("paybackValue");
  const g4 = state.results.g4;
  const investimento = g4 ? g4.inputs.valorRealizado : 0;

  if (g4 && investimento > 0) {
    const roi = (totalAnual / investimento) * 100;
    const paybackMeses = totalAnual > 0 ? investimento / (totalAnual / 12) : Infinity;
    roiEl.textContent = `ROI ${fmtNum(roi, 1)}%`;
    paybackEl.textContent = Number.isFinite(paybackMeses) ? `Payback em ${fmtNum(paybackMeses, 1)} meses` : "Payback indeterminado";
  } else {
    roiEl.textContent = "—";
    paybackEl.textContent = "Informe G4 (Investimento Realizado) para calcular ROI e Payback";
  }
}

function chartColors() {
  return {
    g1: "#2563EB", g2: "#60A5FA", g3: "#16A34A", g4: "#4ADE80",
    text: getComputedStyle(document.documentElement).getPropertyValue("--text").trim() || "#0F172A",
    grid: getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#E2E8F0",
  };
}

function renderCharts() {
  const colors = chartColors();
  const labels = [];
  const data = [];
  const bg = [];
  GAIN_ORDER.forEach((gid) => {
    if (state.results[gid]) {
      labels.push(`${GAIN_DEFS[gid].code} — ${GAIN_DEFS[gid].name}`);
      data.push(Math.max(0, state.results[gid].annual));
      bg.push(colors[gid]);
    }
  });

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

/* ===================== Executive report ===================== */

function renderReport(totalAnual) {
  const name = document.getElementById("projName").value || "(sem nome definido)";
  const company = document.getElementById("projCompany").value || "(empresa não informada)";
  const responsible = document.getElementById("projResponsible").value || "(responsável não informado)";
  const date = document.getElementById("projDate").value || new Date().toISOString().slice(0, 10);

  document.getElementById("reportMeta").innerHTML = `
    <strong>${name}</strong><br>
    ${company}<br>
    Responsável: ${responsible}<br>
    Data: ${new Date(date + "T00:00:00").toLocaleDateString("pt-BR")}
  `;

  const selectedNames = GAIN_ORDER.filter((g) => state.results[g]).map((g) => `${GAIN_DEFS[g].code} — ${GAIN_DEFS[g].name}`);
  document.getElementById("reportGainsSelected").textContent = selectedNames.join(" · ") || "Nenhum ganho calculado.";

  const memoryWrap = document.getElementById("reportMemory");
  memoryWrap.innerHTML = "<h3>Memória de Cálculo</h3>" + GAIN_ORDER.filter((g) => state.results[g]).map((gid) => {
    const def = GAIN_DEFS[gid];
    const r = state.results[gid];
    return `
      <div class="memory-block">
        <h4>${def.icon} ${def.code} — ${def.name}</h4>
        <ol>${r.steps.map((s) => `<li>${s}</li>`).join("")}</ol>
        <div class="result-line">Resultado: ${fmtCurrencyAno(r.annual)}</div>
      </div>`;
  }).join("");

  const table = document.getElementById("reportTotalsTable");
  const rows = GAIN_ORDER.filter((g) => state.results[g]).map((gid) => {
    const share = totalAnual > 0 ? (state.results[gid].annual / totalAnual) * 100 : 0;
    return `<tr><td>${GAIN_DEFS[gid].code} — ${GAIN_DEFS[gid].name}</td><td>${fmtCurrency(state.results[gid].annual)}</td><td>${fmtPercent(share)}</td></tr>`;
  }).join("");
  const g4 = state.results.g4;
  const investimento = g4 ? g4.inputs.valorRealizado : 0;
  const roiRow = g4 && investimento > 0 ? `<tr><td>ROI</td><td colspan="2">${fmtNum((totalAnual / investimento) * 100, 1)}%</td></tr>
    <tr><td>Payback</td><td colspan="2">${fmtNum(investimento / (totalAnual / 12), 1)} meses</td></tr>` : "";

  table.innerHTML = `
    <thead><tr><th>Ganho</th><th>Valor Anual</th><th>Participação</th></tr></thead>
    <tbody>
      ${rows}
      <tr style="font-weight:800"><td>Ganho Anual Total</td><td colspan="2">${fmtCurrency(totalAnual)}</td></tr>
      <tr><td>Ganho Médio Mensal</td><td colspan="2">${fmtCurrency(totalAnual / 12)}</td></tr>
      ${roiRow}
    </tbody>
  `;

  const topGain = GAIN_ORDER.filter((g) => state.results[g]).sort((a, b) => state.results[b].annual - state.results[a].annual)[0];
  const conclusion = topGain
    ? `O projeto Kaizen "${name}" apresenta um ganho financeiro anual total estimado em ${fmtCurrency(totalAnual)}, equivalente a uma média mensal de ${fmtCurrency(totalAnual / 12)}. ` +
      `O ganho de maior impacto é ${GAIN_DEFS[topGain].code} — ${GAIN_DEFS[topGain].name}, responsável por ${fmtPercent(totalAnual > 0 ? (state.results[topGain].annual / totalAnual) * 100 : 0)} do resultado total. ` +
      (g4 && investimento > 0
        ? `Considerando o investimento realizado de ${fmtCurrency(investimento)}, o projeto apresenta ROI de ${fmtNum((totalAnual / investimento) * 100, 1)}% ao ano, com payback estimado em ${fmtNum(investimento / (totalAnual / 12), 1)} meses. `
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
  document.getElementById("projDate").value = "";
  state.selected.clear();
  state.results = {};
  state.calculated = false;
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
    savedAt: new Date().toISOString(),
    selected: Array.from(state.selected),
    results: state.results,
  };
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
    const total = Object.values(p.results).reduce((s, r) => s + (r.annual || 0), 0);
    return `
      <div class="history-item">
        <div class="hi-name">${p.name}</div>
        <div class="hi-meta">${p.company || "—"} &middot; ${new Date(p.date + "T00:00:00").toLocaleDateString("pt-BR")}<br>
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

  state.selected = new Set(p.selected);
  renderGainCards();

  p.selected.forEach((gid) => {
    const def = GAIN_DEFS[gid];
    const inputs = p.results[gid]?.inputs || {};
    def.fields.forEach((f) => {
      const el = document.getElementById(`${gid}_${f.id}`);
      if (!el) return;
      const val = inputs[f.id];
      if (f.type === "currency") el.value = val ? NUM2.format(val).replace(/[^\d,.-]/g, "") : "";
      else if (f.type === "percent") el.value = val ? `${fmtNum(val, 1)}%` : "";
      else el.value = val ?? f.default ?? "";
    });
  });

  state.results = p.results;
  state.calculated = true;
  Object.entries(p.results).forEach(([gid, r]) => renderGainMiniResults(gid, r));
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

  const totalAnual = GAIN_ORDER.reduce((sum, g) => sum + (state.results[g]?.annual || 0), 0);
  const resumo = [
    ["Relatório Executivo Kaizen"],
    ["Projeto", document.getElementById("projName").value],
    ["Empresa", document.getElementById("projCompany").value],
    ["Responsável", document.getElementById("projResponsible").value],
    ["Data", document.getElementById("projDate").value],
    [],
    ["Ganho", "Valor Anual (R$)", "Participação (%)"],
    ...GAIN_ORDER.filter((g) => state.results[g]).map((g) => [
      `${GAIN_DEFS[g].code} — ${GAIN_DEFS[g].name}`,
      Number(state.results[g].annual.toFixed(2)),
      totalAnual > 0 ? Number(((state.results[g].annual / totalAnual) * 100).toFixed(2)) : 0,
    ]),
    [],
    ["Ganho Anual Total", Number(totalAnual.toFixed(2))],
    ["Ganho Médio Mensal", Number((totalAnual / 12).toFixed(2))],
  ];
  const g4 = state.results.g4;
  if (g4 && g4.inputs.valorRealizado > 0) {
    resumo.push(["ROI (%)", Number(((totalAnual / g4.inputs.valorRealizado) * 100).toFixed(2))]);
    resumo.push(["Payback (meses)", Number((g4.inputs.valorRealizado / (totalAnual / 12)).toFixed(2))]);
  }
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(resumo), "Resumo");

  GAIN_ORDER.filter((g) => state.results[g]).forEach((gid) => {
    const r = state.results[gid];
    const sheet = [
      [`${GAIN_DEFS[gid].code} — ${GAIN_DEFS[gid].name}`],
      [],
      ["Entradas"],
      ...Object.entries(r.inputs).map(([k, v]) => [k, v]),
      [],
      ["Memória de Cálculo"],
      ...r.steps.map((s) => [s]),
      [],
      ["Resultado Anual (R$)", Number(r.annual.toFixed(2))],
    ];
    XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(sheet), GAIN_DEFS[gid].code);
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
    GAIN_ORDER.forEach((g) => state.selected.add(g));
    renderGainCards();
  });
  document.getElementById("clearSelection").addEventListener("click", () => {
    state.selected.clear();
    state.results = {};
    state.calculated = false;
    document.getElementById("dashboard").style.display = "none";
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

  ["projName", "projCompany", "projResponsible", "projDate"].forEach((id) => {
    document.getElementById(id).addEventListener("input", () => { if (state.calculated) renderReport(GAIN_ORDER.reduce((s, g) => s + (state.results[g]?.annual || 0), 0)); });
  });

  renderGainCards();
}

document.addEventListener("DOMContentLoaded", init);
