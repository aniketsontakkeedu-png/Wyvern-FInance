/**
 * Wyvern Fintech OS - Main Frontend Application Logic
 */

const STATE = {
  activeTab: 'overview',
  currency: 'USD', // 'USD' or 'INR'
  fxRate: 83.5, // 1 USD = 83.5 INR
  overview: null,
  transactions: [],
  budget: null,
  indices: [],
  indiaMarket: null,
  globalMap: null,
  investmentRegion: 'india', // 'india' or 'global'
  forecastHorizon: 6,
  audioMuted: false,
  autoRefreshTimer: null
};

// Formatting utilities
function formatMoney(amount, currency = null) {
  const curr = currency || STATE.currency;
  let val = Number(amount) || 0;
  if (curr === 'INR' && (!currency || currency === 'USD')) {
    val = val * STATE.fxRate;
    return '₹' + val.toLocaleString('en-IN', { maximumFractionDigits: 0 });
  } else if (curr === 'INR') {
    return '₹' + val.toLocaleString('en-IN', { maximumFractionDigits: 0 });
  } else {
    return '$' + val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
}

function formatRawINR(amount) {
  return '₹' + (Number(amount) || 0).toLocaleString('en-IN');
}

function formatRawUSD(amount) {
  return '$' + (Number(amount) || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Clock & Telemetry
function startClock() {
  const clockEl = document.getElementById('live-clock');
  function update() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
    const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }).toUpperCase();
    if (clockEl) {
      clockEl.innerHTML = `<span class="text-[#888]">${dateStr}</span> <span class="text-white font-bold">${timeStr}</span>`;
    }
  }
  update();
  setInterval(update, 1000);
}

// Tab Switching
function switchTab(tabName) {
  haptics.playClick();
  STATE.activeTab = tabName;

  document.querySelectorAll('.nav-pill').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });

  document.querySelectorAll('.tab-view').forEach(view => {
    view.classList.toggle('hidden', view.id !== `tab-${tabName}`);
  });

  // Trigger tab-specific refresh if needed
  if (tabName === 'market') {
    loadMarketIndices();
  } else if (tabName === 'investments') {
    loadInvestments();
  } else if (tabName === 'ml') {
    loadMLForecast();
  }
}

// API Calls
async function loadOverview() {
  try {
    const res = await fetch('/api/overview');
    const data = await res.json();
    STATE.overview = data;
    renderOverviewUI(data);
  } catch (err) {
    console.error('Failed to load overview:', err);
  }
}

async function loadTransactions() {
  try {
    const res = await fetch('/api/transactions?limit=60');
    const data = await res.json();
    STATE.transactions = data;
    renderTransactionsTable(data);
    renderAnomaliesRadar(data);
  } catch (err) {
    console.error('Failed to load transactions:', err);
  }
}

async function loadBudget() {
  try {
    const res = await fetch('/api/budget');
    const data = await res.json();
    STATE.budget = data;
    renderBudgetUI(data);
  } catch (err) {
    console.error('Failed to load budget:', err);
  }
}

async function loadMarketIndices() {
  try {
    const res = await fetch('/api/market/indices');
    const data = await res.json();
    STATE.indices = data;
    renderMarketIndices(data);
  } catch (err) {
    console.error('Failed to load market indices:', err);
  }
}

async function loadInvestments() {
  try {
    const [indRes, glbRes] = await Promise.all([
      fetch('/api/market/india'),
      fetch('/api/market/global')
    ]);
    STATE.indiaMarket = await indRes.json();
    STATE.globalMap = await glbRes.json();
    renderInvestmentsUI();
  } catch (err) {
    console.error('Failed to load investments:', err);
  }
}

async function loadMLForecast() {
  try {
    const res = await fetch(`/api/ml/forecast?horizon=${STATE.forecastHorizon}`);
    const data = await res.json();
    renderForecastUI(data);
  } catch (err) {
    console.error('Failed to load ML forecast:', err);
  }
}

// UI Renderers
function renderOverviewUI(data) {
  document.getElementById('stat-net-worth').textContent = formatMoney(data.net_worth);
  document.getElementById('stat-monthly-spend').textContent = formatMoney(data.current_period_spending);
  document.getElementById('stat-savings-forecast').textContent = formatMoney(data.forecast.current_monthly_avg_savings) + '/mo';
  
  // Anomaly alert pill
  const anomBadge = document.getElementById('stat-anomaly-count');
  if (anomBadge) {
    anomBadge.textContent = `${data.anomaly_count} ANOMALIES DETECTED`;
    if (data.anomaly_count > 0) {
      anomBadge.className = 'badge-ndot badge-red';
    } else {
      anomBadge.className = 'badge-ndot badge-white';
    }
  }

  // Savings rate
  const savRateEl = document.getElementById('stat-savings-rate');
  if (savRateEl) {
    savRateEl.textContent = `${data.forecast.current_savings_rate_pct}%`;
  }

  // Runway
  const runwayEl = document.getElementById('stat-runway');
  if (runwayEl) {
    runwayEl.textContent = `${data.forecast.emergency_runway_months} MO`;
  }

  // Plaid pill
  const plaidPill = document.getElementById('header-plaid-status');
  if (plaidPill && data.plaid_status) {
    plaidPill.textContent = `${data.plaid_status.institution_name.toUpperCase()} // SYNCED`;
  }

  // 50/30/20 bars
  const r = data.rule_50_30_20;
  if (r) {
    document.getElementById('bar-needs').style.width = `${Math.min(100, r.needs.pct)}%`;
    document.getElementById('val-needs').textContent = `${r.needs.pct}% (${formatMoney(r.needs.amount)})`;

    document.getElementById('bar-wants').style.width = `${Math.min(100, r.wants.pct)}%`;
    document.getElementById('val-wants').textContent = `${r.wants.pct}% (${formatMoney(r.wants.amount)})`;

    document.getElementById('bar-savings').style.width = `${Math.min(100, r.savings.pct)}%`;
    document.getElementById('val-savings').textContent = `${r.savings.pct}% (${formatMoney(r.savings.amount)})`;
  }

  // Render overview chart
  renderForecastChart('overviewForecastChart', data.forecast, STATE.currency === 'INR' ? '₹' : '$');

  // Quick Recommendations list
  const recsContainer = document.getElementById('overview-recommendations');
  if (recsContainer && data.top_recommendations) {
    recsContainer.innerHTML = data.top_recommendations.map(r => `
      <div class="p-4 rounded-2xl bg-[#161616] border border-[#262626] flex items-start justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="badge-ndot ${r.priority === 'HIGH' ? 'badge-red' : 'badge-white'} text-[10px]">${r.badge}</span>
            <span class="text-xs font-mono text-[#888]">+${formatMoney(r.monthly_savings_impact)}/mo</span>
          </div>
          <h4 class="text-sm font-semibold text-white mb-1">${r.title}</h4>
          <p class="text-xs text-[#999] leading-relaxed">${r.description}</p>
        </div>
        <button onclick="switchTab('budget')" class="btn-nothing text-[11px] py-1.5 px-3 flex-shrink-0">
          VIEW
        </button>
      </div>
    `).join('');
  }
}

function renderTransactionsTable(transactions) {
  const tbody = document.getElementById('transactions-tbody');
  if (!tbody) return;

  if (transactions.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center py-8 text-[#666]">No transactions loaded yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = transactions.map(tx => {
    const isAnom = tx.anomaly_analysis && tx.anomaly_analysis.is_anomaly;
    const severity = tx.anomaly_analysis ? tx.anomaly_analysis.severity : 'NORMAL';
    const isIncome = tx.category === 'Income & Deposits';
    const dateFormatted = new Date(tx.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

    let anomBadge = '';
    if (isAnom) {
      const bClass = severity === 'CRITICAL' ? 'badge-red' : 'badge-white';
      anomBadge = `<span class="badge-ndot ${bClass} ml-2 text-[10px]" title="${tx.anomaly_analysis.reasons[0]}">⚡ ${severity}</span>`;
    }

    return `
      <tr>
        <td class="font-mono text-[#888]">${dateFormatted}</td>
        <td>
          <div class="flex items-center font-medium text-white">
            <span>${tx.merchant}</span>
            ${anomBadge}
          </div>
          <div class="text-[11px] text-[#666] font-mono">${tx.channel} • ${tx.id}</div>
        </td>
        <td>
          <span class="inline-block px-2.5 py-1 rounded-full text-[11px] font-mono bg-[#1a1a1a] text-[#bbb] border border-[#2a2a2a]">
            ${tx.category}
          </span>
        </td>
        <td class="text-right font-mono font-semibold ${isIncome ? 'text-[#4ade80]' : 'text-white'}">
          ${isIncome ? '+' : '-'}${formatMoney(tx.amount)}
        </td>
        <td class="text-right">
          <span class="text-[11px] font-mono text-[#777]">${tx.pending ? 'PENDING' : 'SETTLED'}</span>
        </td>
      </tr>
    `;
  }).join('');
}

function renderAnomaliesRadar(transactions) {
  const container = document.getElementById('ml-anomalies-list');
  if (!container) return;

  const anomalies = transactions.filter(t => t.anomaly_analysis && t.anomaly_analysis.is_anomaly);

  if (anomalies.length === 0) {
    container.innerHTML = `<div class="p-6 text-center text-[#666] font-mono">No spending anomalies flagged in recent transactions. Model baseline is healthy.</div>`;
    return;
  }

  container.innerHTML = anomalies.map(tx => {
    const anom = tx.anomaly_analysis;
    const isCrit = anom.severity === 'CRITICAL';

    return `
      <div class="p-5 rounded-2xl bg-[#141414] border ${isCrit ? 'border-[#D71921]' : 'border-[#333]'} relative overflow-hidden">
        <div class="flex items-start justify-between gap-4 mb-3">
          <div class="flex items-center gap-2">
            <span class="glyph-indicator ${isCrit ? '' : 'glyph-indicator-white'}"></span>
            <span class="font-ndot text-xs tracking-wider ${isCrit ? 'text-[#ff4d5a]' : 'text-white'}">${anom.severity} ANOMALY</span>
            <span class="text-xs font-mono text-[#888]">• Score ${anom.anomaly_score}/100</span>
          </div>
          <span class="font-mono font-bold text-white text-base">${formatMoney(tx.amount)}</span>
        </div>

        <h4 class="font-semibold text-white text-sm mb-1">${tx.merchant}</h4>
        <div class="text-xs font-mono text-[#777] mb-3">${tx.category} • ${new Date(tx.date).toLocaleDateString()}</div>

        <div class="p-3 rounded-xl bg-[#0c0c0c] border border-[#222] mb-3">
          <div class="text-xs text-[#ddd] mb-1 font-mono">${anom.reasons.join(' ')}</div>
          <div class="text-[11px] text-[#ff8080] font-mono">Recommendation: ${anom.suggested_action}</div>
        </div>

        <div class="flex items-center justify-between text-[11px] font-mono text-[#666]">
          <span>AI Isolation Forest & MAD Verified</span>
          <button onclick="alert('Transaction flagged for dispute with institution.')" class="btn-nothing text-[10px] py-1 px-3">
            FLAG / DISPUTE
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function renderBudgetUI(data) {
  if (!data) return;

  // Breakdown chart
  renderCategoryChart('budgetCategoryChart', data.category_breakdown);

  // Subscriptions list
  const subsList = document.getElementById('subscriptions-list');
  if (subsList && data.subscriptions) {
    document.getElementById('sub-monthly-total').textContent = formatMoney(data.subscriptions.monthly_total);
    document.getElementById('sub-annual-total').textContent = formatMoney(data.subscriptions.annual_total);
    document.getElementById('sub-count').textContent = data.subscriptions.count;

    subsList.innerHTML = data.subscriptions.items.map(s => `
      <div class="flex items-center justify-between p-3.5 rounded-xl bg-[#161616] border border-[#262626]">
        <div>
          <div class="text-sm font-semibold text-white">${s.merchant}</div>
          <div class="text-[11px] font-mono text-[#777]">Recurring Monthly</div>
        </div>
        <div class="text-right">
          <div class="font-mono font-bold text-white">${formatMoney(s.amount)}/mo</div>
          <div class="text-[11px] font-mono text-[#666]">${formatMoney(s.amount * 12)}/yr</div>
        </div>
      </div>
    `).join('');
  }

  // Full Recommendations list
  const fullRecsContainer = document.getElementById('budget-full-recommendations');
  if (fullRecsContainer && data.recommendations) {
    fullRecsContainer.innerHTML = data.recommendations.map(r => `
      <div class="bento-card bento-card-interactive">
        <div class="flex items-center justify-between mb-3">
          <span class="badge-ndot ${r.priority === 'HIGH' ? 'badge-red' : 'badge-white'} text-[11px]">${r.badge}</span>
          <span class="text-sm font-mono font-bold text-[#4ade80]">+${formatMoney(r.monthly_savings_impact)} / mo</span>
        </div>
        <h3 class="text-base font-bold text-white mb-2">${r.title}</h3>
        <p class="text-xs text-[#aaa] leading-relaxed mb-4">${r.description}</p>
        <div class="p-3 rounded-xl bg-[#0a0a0a] border border-[#222] mb-4 text-xs font-mono text-[#eee]">
          <span class="text-[#ff4d5a] font-bold">ACTION:</span> ${r.suggested_action}
        </div>
        <div class="flex items-center justify-between text-xs font-mono text-[#777]">
          <span>Annual Impact: +${formatMoney(r.annual_savings_impact)}</span>
          <button onclick="applyRecommendation('${r.id}')" class="btn-nothing btn-nothing-red text-xs py-1.5 px-4">
            APPLY RECOMMENDATION
          </button>
        </div>
      </div>
    `).join('');
  }
}

function renderMarketIndices(indices) {
  const container = document.getElementById('market-indices-grid');
  if (!container) return;

  container.innerHTML = indices.map(idx => {
    const isUp = idx.pct_change >= 0;
    return `
      <div class="bento-card p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="font-ndot text-xs text-[#888] tracking-wider">${idx.name}</span>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1e1e1e] text-[#aaa]">${idx.region}</span>
        </div>
        <div class="font-mono text-xl font-bold text-white mb-1">
          ${idx.currency === 'INR' ? '₹' : '$'}${idx.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </div>
        <div class="flex items-center gap-2 font-mono text-xs ${isUp ? 'text-[#4ade80]' : 'text-[#ff4d5a]'}">
          <span>${isUp ? '▲' : '▼'} ${Math.abs(idx.pct_change).toFixed(2)}%</span>
          <span class="text-[#666]">(${isUp ? '+' : ''}${idx.change.toFixed(2)})</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderInvestmentsUI() {
  const isIndia = STATE.investmentRegion === 'india';
  const data = isIndia ? STATE.indiaMarket : STATE.globalMap;
  if (!data) return;

  // Toggle buttons visual state
  document.getElementById('btn-region-india').classList.toggle('active', isIndia);
  document.getElementById('btn-region-global').classList.toggle('active', !isIndia);

  // Currency symbol
  const currSym = data.currency_symbol;

  // Render SIPs
  const sipContainer = document.getElementById('sips-cards-grid');
  if (sipContainer && data.sips) {
    sipContainer.innerHTML = data.sips.map(sip => `
      <div class="bento-card bento-card-interactive flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between gap-2 mb-2">
            <span class="badge-ndot badge-white text-[10px]">${sip.category}</span>
            <span class="badge-ndot badge-red text-[10px]">${sip.risk_level}</span>
          </div>
          <h3 class="text-base font-bold text-white mb-2 leading-snug">${sip.name}</h3>
          
          <div class="grid grid-cols-3 gap-2 p-3 rounded-xl bg-[#0c0c0c] border border-[#222] my-3">
            <div class="text-center">
              <div class="text-[10px] font-mono text-[#777]">1Y CAGR</div>
              <div class="font-mono font-bold text-[#4ade80] text-sm">+${sip.cagr_1y}%</div>
            </div>
            <div class="text-center border-x border-[#222]">
              <div class="text-[10px] font-mono text-[#777]">3Y CAGR</div>
              <div class="font-mono font-bold text-white text-sm">+${sip.cagr_3y}%</div>
            </div>
            <div class="text-center">
              <div class="text-[10px] font-mono text-[#777]">5Y CAGR</div>
              <div class="font-mono font-bold text-[#4ade80] text-sm">+${sip.cagr_5y}%</div>
            </div>
          </div>

          <p class="text-xs text-[#999] leading-relaxed mb-4">${sip.ai_verdict}</p>
        </div>

        <div class="pt-3 border-t border-[#222] flex items-center justify-between">
          <div class="text-xs font-mono text-[#666]">
            Exp: ${sip.expense_ratio}% • Min: ${currSym}${sip.min_sip}
          </div>
          <button onclick="prefillSipCalculator('${sip.name}', ${sip.cagr_5y}, ${sip.min_sip})" class="btn-nothing text-[11px] py-1 px-3">
            CALCULATE SIP
          </button>
        </div>
      </div>
    `).join('');
  }

  // Render Top Stocks
  const stocksContainer = document.getElementById('stocks-cards-grid');
  if (stocksContainer && data.stocks) {
    stocksContainer.innerHTML = data.stocks.map(st => {
      const isUp = st.pct_change >= 0;
      return `
        <div class="bento-card bento-card-interactive flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="font-ndot text-sm font-bold text-white">${st.ticker}</span>
              <span class="badge-ndot ${st.analyst_rating.includes('Strong') ? 'badge-red' : 'badge-white'} text-[10px]">
                ${st.analyst_rating}
              </span>
            </div>
            <h4 class="text-sm font-semibold text-[#ddd] mb-1">${st.name}</h4>
            <div class="text-[11px] font-mono text-[#777] mb-3">${st.sector}</div>

            <div class="flex items-baseline justify-between mb-2">
              <div class="font-mono text-xl font-bold text-white">
                ${currSym}${st.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </div>
              <div class="font-mono text-xs font-semibold ${isUp ? 'text-[#4ade80]' : 'text-[#ff4d5a]'}">
                ${isUp ? '▲' : '▼'} ${Math.abs(st.pct_change).toFixed(2)}%
              </div>
            </div>

            <div class="flex items-center justify-between text-[11px] font-mono text-[#666] p-2.5 rounded-lg bg-[#0c0c0c] mb-3">
              <span>Target: ${currSym}${st.target_price}</span>
              <span>Cap: ${st.market_cap}</span>
            </div>
          </div>

          <div class="pt-2 border-t border-[#222] flex items-center justify-between">
            <span class="text-[10px] font-mono text-[#555]">LIVE FEED</span>
            <button onclick="alert('Added ${st.ticker} to Wyvern Market Watchlist.')" class="btn-nothing text-[10px] py-1 px-2.5">
              + WATCHLIST
            </button>
          </div>
        </div>
      `;
    }).join('');
  }
}

function renderForecastUI(forecastData) {
  renderForecastChart('mlDetailedForecastChart', forecastData, STATE.currency === 'INR' ? '₹' : '$');

  // Populate scenario totals
  const sc = forecastData.scenarios_6_month;
  if (sc) {
    document.getElementById('sc-conservative-total').textContent = formatMoney(sc.conservative.total);
    document.getElementById('sc-conservative-avg').textContent = formatMoney(sc.conservative.monthly_avg) + '/mo';

    document.getElementById('sc-baseline-total').textContent = formatMoney(sc.baseline.total);
    document.getElementById('sc-baseline-avg').textContent = formatMoney(sc.baseline.monthly_avg) + '/mo';

    document.getElementById('sc-optimized-total').textContent = formatMoney(sc.wyvern_optimized.total);
    document.getElementById('sc-optimized-avg').textContent = formatMoney(sc.wyvern_optimized.monthly_avg) + '/mo';
    document.getElementById('sc-optimized-extra').textContent = '+' + formatMoney(sc.wyvern_optimized.extra_accumulated);
  }

  // Populate table
  const tbody = document.getElementById('ml-forecast-tbody');
  if (tbody && forecastData.projections) {
    tbody.innerHTML = forecastData.projections.map(p => `
      <tr>
        <td class="font-mono text-white font-semibold">${p.month}</td>
        <td class="font-mono text-right text-[#4ade80] font-bold">${formatMoney(p.projected_savings)}</td>
        <td class="font-mono text-right text-[#888]">${formatMoney(p.lower_bound)} - ${formatMoney(p.upper_bound)}</td>
        <td class="font-mono text-right text-white">${p.savings_rate_pct}%</td>
        <td class="font-mono text-right text-[#ff4d5a] font-bold">${formatMoney(p.cumulative_projected)}</td>
      </tr>
    `).join('');
  }
}

// Interactive ML Categorizer Playground
async function testCategorize(customText = null) {
  haptics.playClick();
  const input = document.getElementById('ml-test-input');
  const query = customText || (input ? input.value : '');
  if (!query || !query.trim()) return;

  if (input && customText) input.value = customText;

  const resultContainer = document.getElementById('ml-test-result');
  resultContainer.innerHTML = `<div class="text-xs font-mono text-[#888] animate-pulse">Running Scikit-learn Classifier...</div>`;

  try {
    const res = await fetch('/api/ml/categorize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description: query })
    });
    const data = await res.json();

    const confPct = Math.round(data.confidence * 100);
    const probEntries = Object.entries(data.probabilities);

    resultContainer.innerHTML = `
      <div class="p-4 rounded-xl bg-[#0e0e0e] border border-[#292929] mt-3">
        <div class="flex items-center justify-between mb-2">
          <div>
            <span class="text-[10px] font-mono text-[#888] uppercase">Classified Category</span>
            <div class="text-base font-bold text-white font-ndot">${data.category}</div>
          </div>
          <div class="text-right">
            <span class="text-[10px] font-mono text-[#888] uppercase">Confidence</span>
            <div class="text-base font-bold text-[#4ade80] font-mono">${confPct}%</div>
          </div>
        </div>

        <div class="glyph-meter-container mb-4">
          <div class="glyph-meter-fill red" style="width: ${confPct}%;"></div>
        </div>

        <div class="text-[11px] font-mono text-[#777] mb-2 uppercase tracking-wider">Top Probability Distribution</div>
        <div class="space-y-1.5">
          ${probEntries.map(([cat, prob]) => {
            const p = Math.round(prob * 100);
            return `
              <div class="flex items-center justify-between text-xs font-mono">
                <span class="${cat === data.category ? 'text-white font-bold' : 'text-[#888]'}">${cat}</span>
                <span class="text-[#bbb]">${p}%</span>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  } catch (err) {
    resultContainer.innerHTML = `<div class="text-xs text-[#ff4d5a]">Prediction error: ${err.message}</div>`;
  }
}

// SIP Compound Calculator
async function calculateSIP() {
  haptics.playClick();
  const monthly = parseFloat(document.getElementById('sip-input-monthly').value) || 10000;
  const rate = parseFloat(document.getElementById('sip-input-rate').value) || 15;
  const years = parseInt(document.getElementById('sip-input-years').value) || 10;
  const stepUp = parseFloat(document.getElementById('sip-input-stepup').value) || 0;

  try {
    const res = await fetch('/api/calculator/sip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        monthly_investment: monthly,
        annual_return_pct: rate,
        years: years,
        step_up_pct: stepUp
      })
    });
    const data = await res.json();

    const currSym = STATE.investmentRegion === 'india' ? '₹' : '$';

    document.getElementById('sip-out-invested').textContent = currSym + data.total_invested.toLocaleString('en-US');
    document.getElementById('sip-out-returns').textContent = currSym + data.estimated_returns.toLocaleString('en-US');
    document.getElementById('sip-out-total').textContent = currSym + data.total_value.toLocaleString('en-US');
    document.getElementById('sip-out-multiplier').textContent = `${data.wealth_multiplier}x Growth`;

    renderSipGrowthChart('sipGrowthCanvas', data.yearly_breakdown, currSym);
  } catch (err) {
    console.error('SIP calc failed:', err);
  }
}

function prefillSipCalculator(fundName, returnRate, minSip) {
  haptics.playPop();
  switchTab('investments');
  document.getElementById('sip-calc-title').textContent = `SIP Simulator: ${fundName}`;
  document.getElementById('sip-input-rate').value = returnRate;
  document.getElementById('sip-rate-val').textContent = `${returnRate}%`;
  calculateSIP();
  document.getElementById('sip-calculator-section').scrollIntoView({ behavior: 'smooth' });
}

// Plaid Modal & Simulation
function openPlaidModal() {
  haptics.playClick();
  document.getElementById('plaid-modal').classList.remove('hidden');
}

function closePlaidModal() {
  haptics.playClick();
  document.getElementById('plaid-modal').classList.add('hidden');
}

async function connectPlaidBank(bankName) {
  haptics.playClick();
  const statusDiv = document.getElementById('plaid-connection-status');
  statusDiv.innerHTML = `
    <div class="p-4 rounded-xl bg-[#111] border border-[#333] text-center">
      <div class="glyph-indicator mb-2"></div>
      <div class="text-xs font-mono text-white mb-1">Authenticating with ${bankName} Plaid Sandbox...</div>
      <div class="text-[11px] font-mono text-[#888]">Exchanging public_token for access_token</div>
    </div>
  `;

  try {
    const res = await fetch('/api/plaid/exchange-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        public_token: 'public-sandbox-mock-token',
        institution_name: bankName
      })
    });
    const data = await res.json();

    setTimeout(() => {
      haptics.playPop();
      statusDiv.innerHTML = `
        <div class="p-4 rounded-xl bg-[#111] border border-[#4ade80] text-center">
          <div class="text-xs font-mono text-[#4ade80] font-bold mb-1">✓ ${bankName} CONNECTED</div>
          <div class="text-[11px] font-mono text-[#aaa]">Item ID: ${data.item_id} • Status: Active</div>
        </div>
      `;
      loadOverview();
      loadTransactions();
      setTimeout(closePlaidModal, 1500);
    }, 1000);
  } catch (err) {
    statusDiv.innerHTML = `<div class="text-xs text-[#ff4d5a]">Connection failed: ${err.message}</div>`;
  }
}

async function syncPlaidNow() {
  haptics.playAlert();
  const btn = document.getElementById('btn-sync-plaid');
  if (btn) btn.textContent = 'SYNCING...';

  try {
    const res = await fetch('/api/plaid/sync', { method: 'POST' });
    const data = await res.json();
    alert(`Plaid Sync Complete: ${data.synced_count} transactions verified and analyzed.`);
    loadOverview();
    loadTransactions();
  } catch (err) {
    alert(`Sync error: ${err.message}`);
  } finally {
    if (btn) btn.textContent = 'SYNC PLAID API';
  }
}

// Add Transaction Modal
function openAddTxModal() {
  haptics.playClick();
  document.getElementById('add-tx-modal').classList.remove('hidden');
}

function closeAddTxModal() {
  haptics.playClick();
  document.getElementById('add-tx-modal').classList.add('hidden');
}

async function submitNewTransaction(e) {
  e.preventDefault();
  haptics.playClick();

  const merchant = document.getElementById('tx-input-merchant').value;
  const amount = parseFloat(document.getElementById('tx-input-amount').value);
  const category = document.getElementById('tx-input-category').value || null;

  if (!merchant || isNaN(amount)) {
    alert('Please enter valid merchant name and amount.');
    return;
  }

  try {
    const res = await fetch('/api/transactions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        merchant: merchant,
        amount: amount,
        category: category
      })
    });
    const result = await res.json();
    haptics.playPop();
    closeAddTxModal();

    const isAnom = result.transaction.anomaly_analysis.is_anomaly;
    if (isAnom) {
      alert(`Transaction added! Anomaly Flagged: ${result.transaction.anomaly_analysis.reasons[0]}`);
    }

    loadOverview();
    loadTransactions();
    loadBudget();
  } catch (err) {
    alert(`Failed to add transaction: ${err.message}`);
  }
}

function applyRecommendation(recId) {
  haptics.playPop();
  alert(`Wyvern AI: Recommendation [${recId}] activated! Budget allocations rebalanced in real time.`);
}

function toggleCurrency() {
  haptics.playClick();
  STATE.currency = STATE.currency === 'USD' ? 'INR' : 'USD';
  const currBtn = document.getElementById('btn-currency-toggle');
  if (currBtn) currBtn.textContent = STATE.currency === 'USD' ? '$ USD' : '₹ INR';
  if (STATE.overview) renderOverviewUI(STATE.overview);
  if (STATE.transactions) renderTransactionsTable(STATE.transactions);
  if (STATE.budget) renderBudgetUI(STATE.budget);
}

function toggleAudio() {
  const isEnabled = haptics.toggle();
  const btn = document.getElementById('btn-audio-toggle');
  if (btn) {
    btn.textContent = isEnabled ? 'AUDIO: ON' : 'AUDIO: OFF';
    btn.classList.toggle('text-white', isEnabled);
    btn.classList.toggle('text-[#555]', !isEnabled);
  }
}

// Initializer
document.addEventListener('DOMContentLoaded', () => {
  startClock();
  loadOverview();
  loadTransactions();
  loadBudget();
  loadMarketIndices();
  loadInvestments();
  loadMLForecast();

  // Range slider listeners for SIP calculator
  const monthlySlider = document.getElementById('sip-input-monthly');
  if (monthlySlider) {
    monthlySlider.addEventListener('input', (e) => {
      document.getElementById('sip-monthly-val').textContent = formatMoney(e.target.value);
      calculateSIP();
    });
  }

  const rateSlider = document.getElementById('sip-input-rate');
  if (rateSlider) {
    rateSlider.addEventListener('input', (e) => {
      document.getElementById('sip-rate-val').textContent = `${e.target.value}%`;
      calculateSIP();
    });
  }

  const yearsSlider = document.getElementById('sip-input-years');
  if (yearsSlider) {
    yearsSlider.addEventListener('input', (e) => {
      document.getElementById('sip-years-val').textContent = `${e.target.value} Years`;
      calculateSIP();
    });
  }

  const stepUpSlider = document.getElementById('sip-input-stepup');
  if (stepUpSlider) {
    stepUpSlider.addEventListener('input', (e) => {
      document.getElementById('sip-stepup-val').textContent = `${e.target.value}% / yr`;
      calculateSIP();
    });
  }

  // Periodic indices refresh (every 30 seconds)
  setInterval(() => {
    if (STATE.activeTab === 'market' || STATE.activeTab === 'overview') {
      loadMarketIndices();
    }
  }, 30000);
});
