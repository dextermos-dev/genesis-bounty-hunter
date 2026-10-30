/**
 * BOUNTY HUNTER AI · EXECUTIVE FINANCIAL CONTROLLER v4.0
 * Minimalist Institutional Fintech & Live Multi-Chain Web3 Telemetry
 */

const SETTLEMENT_WALLET = "0x8366bCe3a2D379De7656D7A67015789FaF999f20";

let globalData = null;
let currentTab = 'wallets';
let currentReconFilter = 'ALL';
let pipelineSearchQuery = '';

// 16 Verified Merged PRs ($2,350.00 USDC Adjudicado / Pending Sweep)
const WON_PRS = [
  { id: "PR-01", repo: "mallonepay/pay-per-token-llm-gateway", pr: "PR #127", title: "Soroban credit escrow settlement engine", amount: 800, date: "2026-09-09", url: "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/127" },
  { id: "PR-02", repo: "mallonepay/pay-per-token-llm-gateway", pr: "PR #133", title: "Migrate contracts to Soroban SDK 26.1.1 (18/18 CI Verde)", amount: 200, date: "2026-10-29", url: "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/133" },
  { id: "PR-03", repo: "mallonepay/pay-per-token-llm-gateway", pr: "PR #134", title: "External custody contract security audit (Issue #83)", amount: 350, date: "2026-10-29", url: "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/134" },
  { id: "PR-04", repo: "Parabola-org/parabola", pr: "PR #101", title: "Add missing export for calculatePoolShares", amount: 105, date: "2026-10-16", url: "https://github.com/Parabola-org/parabola/pull/101" },
  { id: "PR-05", repo: "Parabola-org/parabola", pr: "PR #104", title: "Fix slippage tolerance bounds in swap math", amount: 105, date: "2026-10-16", url: "https://github.com/Parabola-org/parabola/pull/104" },
  { id: "PR-06", repo: "Parabola-org/parabola", pr: "PR #116", title: "Validate token pair decimals on initialization", amount: 125, date: "2026-10-16", url: "https://github.com/Parabola-org/parabola/pull/116" },
  { id: "PR-07", repo: "Parabola-org/parabola", pr: "PR #109", title: "Clamp oracle update frequency to avoid stale prices", amount: 125, date: "2026-10-16", url: "https://github.com/Parabola-org/parabola/pull/109" },
  { id: "PR-08", repo: "Parabola-org/parabola", pr: "PR #115", title: "Refactor pool reentrancy guard for Gas efficiency", amount: 60, date: "2026-10-16", url: "https://github.com/Parabola-org/parabola/pull/115" },
  { id: "PR-09", repo: "Parabola-org/parabola", pr: "PR #99", title: "Fix edge case in fee distribution rounding", amount: 45, date: "2026-10-16", url: "https://github.com/Parabola-org/parabola/pull/99" },
  { id: "PR-10", repo: "Parabola-org/parabola", pr: "PR #100", title: "Add strict bounds check to pool deposit liquidity", amount: 45, date: "2026-10-16", url: "https://github.com/Parabola-org/parabola/pull/100" },
  { id: "PR-11", repo: "slippay-labs/slippay", pr: "PR #264", title: "Harden token transfer auth callback validation", amount: 75, date: "2026-10-18", url: "https://github.com/slippay-labs/slippay/pull/264" },
  { id: "PR-12", repo: "Chain-Love/chain-love", pr: "PR #4728", title: "Almizaan smart contract security scanner documentation", amount: 140, date: "2026-10-21", url: "https://github.com/Chain-Love/chain-love/pull/4728" },
  { id: "PR-13", repo: "slippay-labs/slippay", pr: "PR #228", title: "Fix decimal truncation on micro-payment streams", amount: 70, date: "2026-10-21", url: "https://github.com/slippay-labs/slippay/pull/228" },
  { id: "PR-14", repo: "slippay-labs/slippay", pr: "PR #453", title: "Add idempotent receipt verification for off-chain relays", amount: 35, date: "2026-10-21", url: "https://github.com/slippay-labs/slippay/pull/453" },
  { id: "PR-15", repo: "slippay-labs/slippay", pr: "PR #435", title: "Enforce non-zero destination check in multi-send", amount: 35, date: "2026-10-21", url: "https://github.com/slippay-labs/slippay/pull/435" },
  { id: "PR-16", repo: "slippay-labs/slippay", pr: "PR #340", title: "Fix timeout retry loop on Soroban RPC network congestion", amount: 35, date: "2026-10-21", url: "https://github.com/slippay-labs/slippay/pull/340" },
  { id: "PR-17", repo: "DevNiola/Prism", pr: "PR #150", title: "Add Dependabot configuration for dependency updates (closes #140)", amount: 150, date: "2026-10-30", url: "https://github.com/DevNiola/Prism/pull/150" }
];

// Master Reconciliation Ledger (Lo que está en Wallet vs Lo Pendiente)
const RECONCILIATION_DATA = [
  // LÍQUIDO EN WALLET
  {
    type: "LIQUID",
    category: "Líquido en Wallet",
    badgeClass: "success",
    concept: "Base L2 wDOOM Tokens (16 TXs BaseScan)",
    wallet: "0x8366...9f20 (Base L2)",
    amount: "24,887.50 wDOOM (≈ $2.49 USD)",
    status: "Confirmado en Cadena (100% Posesión)",
    urlText: "BaseScan ↗",
    url: "https://basescan.org/token/0x623c84A5E04bF715018203334b0eFE41696eBC3E?a=0x8366bce3a2d379de7656d7a67015789faf999f20"
  },
  {
    type: "LIQUID",
    category: "Líquido en Wallet",
    badgeClass: "purple",
    concept: "Doomsday L1 DOOM Mined (Pool + Génesis)",
    wallet: "doom162df... (PoW L1)",
    amount: "8,382.81 DOOM (≈ $0.84 USD)",
    status: "Top #9 Mundial (49.74 MH/s 24/7)",
    urlText: "Pool Worker ↗",
    url: "https://doomsday.network/pool/worker/doom162df6bb0c219de72343658ec04c1d9b1939c3c5c02f6b94f"
  },
  {
    type: "LIQUID",
    category: "Líquido en Wallet",
    badgeClass: "info",
    concept: "Nano Mainnet M2M Balance",
    wallet: "nano_3i7n... (Block Lattice)",
    amount: "Ӿ0.048 XNO (≈ $0.05 USD)",
    status: "Ledger #491 Verificado",
    urlText: "BlockLattice ↗",
    url: "https://blocklattice.io/account/nano_3i7nondimxz8zbqn6kkoffoqydi61ektguf6sq8n7m7k77iznhn7y9mxxubg"
  },

  // ADJUDICADO PENDIENTE DE COBRO
  {
    type: "PENDING",
    category: "Ganado Pendiente",
    badgeClass: "warning",
    concept: "DevNiola/Prism PR #150 (Dependabot v2 Config #140)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$150.00 USDC",
    status: "Mergeado en main por DevNiola (v1.1.0)",
    urlText: "PR #150 ↗",
    url: "https://github.com/DevNiola/Prism/pull/150"
  },
  {
    type: "PENDING",
    category: "Ganado Pendiente",
    badgeClass: "warning",
    concept: "MallonePay PR #127 (Credit Escrow Custody)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$800.00 USDC",
    status: "Aprobado en main / Sweep Oct 31",
    urlText: "PR #127 ↗",
    url: "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/127"
  },
  {
    type: "PENDING",
    category: "Ganado Pendiente",
    badgeClass: "warning",
    concept: "MallonePay PR #133 (Soroban SDK 26 Migration)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$200.00 USDC",
    status: "18/18 CI Verde / Aprobado",
    urlText: "PR #133 ↗",
    url: "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/133"
  },
  {
    type: "PENDING",
    category: "Ganado Pendiente",
    badgeClass: "warning",
    concept: "MallonePay PR #134 (External Custody Audit #83)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$350.00 USDC",
    status: "16/18 CI Verde / Aprobado",
    urlText: "PR #134 ↗",
    url: "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/134"
  },
  {
    type: "PENDING",
    category: "Ganado Pendiente",
    badgeClass: "warning",
    concept: "Parabola-org Protocol (7 PRs Aprobadas)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$545.00 USDC",
    status: "Mergeadas en main / Batch 1-7 Nov",
    urlText: "Ver Lote ↗",
    url: "https://github.com/Parabola-org/parabola/pulls"
  },
  {
    type: "PENDING",
    category: "Ganado Pendiente",
    badgeClass: "warning",
    concept: "SlipPay Labs Protocol (5 PRs Aprobadas)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$215.00 USDC",
    status: "Mergeadas en main / Batch 5-12 Nov",
    urlText: "Ver Lote ↗",
    url: "https://github.com/slippay-labs/slippay/pulls"
  },
  {
    type: "PENDING",
    category: "Ganado Pendiente",
    badgeClass: "warning",
    concept: "Chain-Love PR #4728 (Almizaan Architecture)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$140.00 USDC",
    status: "Mergeada en main / Sweep Nov 10",
    urlText: "PR #4728 ↗",
    url: "https://github.com/Chain-Love/chain-love/pull/4728"
  },

  // EN REVISIÓN ACTIVA (SPRINT)
  {
    type: "REVIEW",
    category: "En Revisión",
    badgeClass: "info",
    concept: "DevNiola/Prism PRs #378, #379 & #380 (Optimistic UI, CI/CD & Taxonomy Guide)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$750.00 USDC",
    status: "CI Verde / En revisión por mantenedor",
    urlText: "PR #378 ↗",
    url: "https://github.com/DevNiola/Prism/pull/378"
  },
  {
    type: "REVIEW",
    category: "En Revisión",
    badgeClass: "info",
    concept: "Go-Hybrid Wildcard Track (Issue #2189 / PR #2259)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$500.00 USDC",
    status: "Intake PR #2259 abierto por Dimank92 / Ventana Nov 1",
    urlText: "PR #2259 ↗",
    url: "https://github.com/limitlessprojects/Go-Hybrid/pull/2259"
  },
  {
    type: "REVIEW",
    category: "En Revisión",
    badgeClass: "info",
    concept: "Go-Hybrid Soundness & Buildable Fixes (8 PRs #2332-#2339)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$600.00 USDC",
    status: "Rebasadas en main f0fc243 / En revisión activa",
    urlText: "PR #2332 ↗",
    url: "https://github.com/limitlessprojects/Go-Hybrid/pull/2332"
  },
  {
    type: "REVIEW",
    category: "En Revisión",
    badgeClass: "success",
    concept: "PurseKeeper Slot 1: LangChain Python (api#132)",
    wallet: "nano_3i7n... (XNO M2M)",
    amount: "Ӿ150.00 XNO (≈ $50.00 USD)",
    status: "PASS Adjudicado (Decisión #915) / Payout Oct 31",
    urlText: "Issue #132 ↗",
    url: "https://github.com/pursekeeper/api/issues/132"
  },
  {
    type: "REVIEW",
    category: "En Revisión",
    badgeClass: "info",
    concept: "Doomsday Top-10 Leaderboard Bounty Claim",
    wallet: "0x8366...9f20 (wDOOM)",
    amount: "4,000 wDOOM (≈ $80.00 USD)",
    status: "Top-9 Alcanzado / Reclamación activa",
    urlText: "Leaderboard ↗",
    url: "https://doomsday.network/pool/leaderboard"
  },
  {
    type: "REVIEW",
    category: "En Revisión",
    badgeClass: "info",
    concept: "Susu-Labs & Chain-Love PRs (#167, #4773, #4781)",
    wallet: "0x8366...9f20 (Base L2 USDC)",
    amount: "$190.00 USDC",
    status: "En revisión activa por jurado",
    urlText: "PR #167 ↗",
    url: "https://github.com/susu-labs/susu-web/pull/167"
  }
];

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  setupTabs();
  setupEventListeners();
  await loadData();
  
  // Auto-refresh every 20 seconds
  setInterval(loadData, 20000);
}

// Fetch both data.json and live telemetry
async function loadData() {
  try {
    const timestamp = Date.now();
    const [dataRes, telemRes] = await Promise.all([
      fetch(`./data.json?t=${timestamp}`).catch(() => null),
      fetch(`./api/wallet-telemetry?t=${timestamp}`).catch(() => null)
    ]);

    if (dataRes && dataRes.ok) {
      globalData = await dataRes.json();
    }
    if (telemRes && telemRes.ok) {
      const telem = await telemRes.json();
      updateTelemetryUI(telem);
    }
  } catch (err) {
    console.debug("Data load notice:", err);
  }

  renderConsolidatedTokensTable();
  renderReconciliationTable(currentReconFilter);
  renderWonTable();
  renderCalendarTable();
  renderPipelineTable(pipelineSearchQuery);
}

// Live Multi-Chain Network Updates
function updateTelemetryUI(telem) {
  if (!telem) return;
  const b = telem.base_l2 || {};
  const d = telem.doomsday_l1 || {};
  const n = telem.nano_mainnet || {};

  const elBase = document.getElementById('headerBaseBlock');
  if (elBase && b.block_number) elBase.textContent = `#${b.block_number.toLocaleString()}`;

  const elDoom = document.getElementById('headerDoomRank');
  if (elDoom && d.rank_title) elDoom.textContent = d.rank_title;

  const elNano = document.getElementById('headerNanoStatus');
  if (elNano && n.confirmed_balance_xno !== undefined) elNano.textContent = `Ӿ${n.confirmed_balance_xno.toFixed(3)}`;
}

// Tab Switching
function setupTabs() {
  const tabs = document.querySelectorAll('.tab-link');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content-panel').forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      const targetId = `panel-${tab.getAttribute('data-tab')}`;
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add('active');
      }
    });
  });
}

// Event Listeners
function setupEventListeners() {
  // Sync button
  const syncBtn = document.getElementById('btnSyncAll');
  if (syncBtn) {
    syncBtn.addEventListener('click', async () => {
      syncBtn.style.opacity = '0.5';
      await loadData();
      setTimeout(() => syncBtn.style.opacity = '1', 400);
    });
  }

  // Hero wallet copy
  const walletCopy = document.getElementById('heroWalletCopy');
  if (walletCopy) {
    walletCopy.addEventListener('click', () => {
      navigator.clipboard.writeText(SETTLEMENT_WALLET);
      alert(`Settlement Wallet Oficial copiada al portapapeles:\n${SETTLEMENT_WALLET}`);
    });
  }

  // Reconciliation filter buttons
  const filterBtns = document.querySelectorAll('.btn-filter');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentReconFilter = btn.getAttribute('data-filter');
      renderConsolidatedTokensTable();
  renderReconciliationTable(currentReconFilter);
    });
  });

  // Pipeline search
  const pipeSearch = document.getElementById('pipelineSearch');
  if (pipeSearch) {
    pipeSearch.addEventListener('input', (e) => {
      pipelineSearchQuery = e.target.value.toLowerCase();
      renderPipelineTable(pipelineSearchQuery);
    });
  }
}

// 1. Render Reconciliation Table
function renderReconciliationTable(filter = 'ALL') {
  const tbody = document.getElementById('reconciliationTableBody');
  if (!tbody) return;

  const items = RECONCILIATION_DATA.filter(item => {
    if (filter === 'ALL') return true;
    return item.type === filter;
  });

  tbody.innerHTML = items.map(r => `
    <tr>
      <td><span class="badge-status ${r.badgeClass}">${r.category}</span></td>
      <td class="cell-primary">${r.concept}</td>
      <td class="cell-mono" style="font-size: 0.74rem;">${r.wallet}</td>
      <td class="cell-mono" style="color: var(--accent-emerald); font-weight: 700;">${r.amount}</td>
      <td>${r.status}</td>
      <td>
        <a href="${r.url}" target="_blank" class="btn-tile-action" style="padding: 4px 8px; font-size: 0.7rem;">
          ${r.urlText}
        </a>
      </td>
    </tr>
  `).join('');
}

// 2. Render Won PRs Table (16 PRs)
function renderWonTable() {
  const tbody = document.getElementById('wonTableBody');
  if (!tbody) return;

  tbody.innerHTML = WON_PRS.map((p, idx) => `
    <tr>
      <td><span class="badge-status success">#${idx + 1} MERGED</span></td>
      <td>
        <div class="cell-primary">${p.title}</div>
        <div style="font-size: 0.7rem; color: var(--text-muted);">${p.repo}</div>
      </td>
      <td>
        <a href="${p.url}" target="_blank" style="color: var(--accent-cyan); font-family: var(--font-mono); text-decoration: none; font-weight: 600;">
          ${p.pr} ↗
        </a>
      </td>
      <td class="cell-mono" style="color: var(--accent-emerald); font-weight: 800;">
        +$${p.amount}.00 USDC
      </td>
      <td class="cell-mono" style="font-size: 0.75rem; color: var(--text-muted);">${p.date}</td>
      <td>
        <span class="badge-status warning">⏳ EN COLA DE SWEEP</span>
      </td>
    </tr>
  `).join('');
}

// 3. Render Calendar Table
function renderCalendarTable() {
  const tbody = document.getElementById('calendarTableBody');
  if (!tbody || !globalData) return;

  const calendarItems = globalData.settlement_calendar || [];
  tbody.innerHTML = calendarItems.map(c => `
    <tr>
      <td class="cell-mono" style="color: var(--accent-cyan); font-weight: 700;">${c.estimated_window || 'Octubre 2026'}</td>
      <td>
        <div class="cell-primary">${c.project}</div>
        <div style="font-size: 0.7rem; color: var(--text-muted);">${c.scope || ''}</div>
      </td>
      <td style="font-size: 0.75rem;">${c.payout_channel}</td>
      <td class="cell-mono" style="color: var(--accent-emerald); font-weight: 700;">$${c.amount_usd}.00 ${c.currency}</td>
      <td><span class="badge-status warning">${c.status}</span></td>
    </tr>
  `).join('');
}

// 4. Render Pipeline Table
function renderPipelineTable(query = '') {
  const tbody = document.getElementById('pipelineTableBody');
  if (!tbody || !globalData) return;

  let items = globalData.bounties || [];
  if (query) {
    items = items.filter(b => {
      const text = `${b.id || ''} ${b.title || ''} ${b.repo || b.project || ''}`.toLowerCase();
      return text.includes(query);
    });
  }

  tbody.innerHTML = items.slice(0, 30).map(b => {
    const repo = b.repo || b.project || b.repository || 'N/A';
    const reward = b.amount_usd || b.reward_usd || b.amount || 70.0;
    const url = b.pr_url || b.html_url || b.url || '#';
    return `
      <tr>
        <td class="cell-mono" style="font-size: 0.72rem; color: var(--text-muted);">${b.id || 'bounty'}</td>
        <td class="cell-primary" style="font-size: 0.78rem;">${repo}</td>
        <td>${b.title || 'Resolución de Issue'}</td>
        <td class="cell-mono" style="color: var(--accent-emerald); font-weight: 700;">$${reward}</td>
        <td><span class="badge-status info">${b.status || 'OPEN'}</span></td>
        <td><a href="${url}" target="_blank" class="btn-tile-action" style="padding: 3px 8px; font-size: 0.68rem;">Ver ↗</a></td>
      </tr>
    `;
  }).join('');
}



// 0. Render Consolidated Multi-Wallet Tokens Table (STRICTLY IN-WALLET ONLY)
function renderConsolidatedTokensTable() {
  const tbody = document.getElementById('consolidatedTokensTableBody');
  if (!tbody) return;

  // STRICTLY CONFIRMED ASSETS CURRENTLY IN OUR PHYSICAL WALLETS (TOTAL = $3.38 USDC)
  const realTokensInWallet = [
    {
      name: 'wDOOM (Wrapped DOOM)',
      badge: 'wdoom',
      network: 'Base Mainnet L2 (Chain 8453)',
      wallet: '0x8366bCe3...9f20',
      balance: '24,887.50 wDOOM',
      price: '$0.00010 USD',
      amount_usdc: 2.49,
      status: '🟢 En Cartera (16 TXs en BaseScan)',
      statusClass: 'success'
    },
    {
      name: 'DOOM (PoW Nativo L1)',
      badge: 'doom',
      network: 'Doomsday Layer-1 PoW',
      wallet: 'doom162df6bb...6b94f',
      balance: '8,382.81 DOOM',
      price: '$0.00010 USD',
      amount_usdc: 0.84,
      status: '🟢 En Cartera (Minado L1 - Top #9)',
      statusClass: 'purple'
    },
    {
      name: 'XNO (Nano Protocol)',
      badge: 'xno',
      network: 'Nano Block Lattice Mainnet',
      wallet: 'nano_3i7nondim...xxubg',
      balance: 'Ӿ0.048 XNO',
      price: '~$1.05 USD',
      amount_usdc: 0.05,
      status: '🟢 En Cartera (Slot 1 PASS - Ӿ150 en Cola)',
      statusClass: 'success'
    },
    {
      name: 'USDC (Circle USD Coin)',
      badge: 'usdc',
      network: 'Base Mainnet L2 (Chain 8453)',
      wallet: '0x8366bCe3...9f20',
      balance: '0.00 USDC',
      price: '$1.00 USD',
      amount_usdc: 0.00,
      status: '⏳ 0.00 en Cartera (Pendiente de envío)',
      statusClass: 'warning'
    },
    {
      name: 'ETH (Ethereum Gas)',
      badge: 'usdc',
      network: 'Base Mainnet L2 (Chain 8453)',
      wallet: '0x8366bCe3...9f20',
      balance: '0.0000 ETH',
      price: '$2,650.00 USD',
      amount_usdc: 0.00,
      status: '⚪ 0.00 en Cartera (Gasless ERC-4337)',
      statusClass: 'info'
    }
  ];

  tbody.innerHTML = realTokensInWallet.map(t => `
    <tr>
      <td class="cell-primary">
        <span class="token-icon-badge ${t.badge}">●</span>
        ${t.name}
      </td>
      <td>
        <span style="font-size: 0.75rem; color: #E2E8F0;">${t.network}</span>
      </td>
      <td class="cell-mono" style="font-size: 0.74rem; color: var(--text-muted);">
        ${t.wallet}
      </td>
      <td class="cell-mono" style="font-weight: 700; color: #fff;">
        ${t.balance}
      </td>
      <td class="cell-mono" style="font-size: 0.75rem; color: var(--text-muted);">
        ${t.price}
      </td>
      <td class="cell-mono" style="color: ${t.amount_usdc > 0 ? 'var(--accent-emerald)' : 'var(--text-muted)'}; font-weight: 800; font-size: 0.88rem;">
        ${t.amount_usdc > 0 ? '+' : ''}$${t.amount_usdc.toFixed(2)} USDC
      </td>
      <td>
        <span class="badge-status ${t.statusClass}">${t.status}</span>
      </td>
    </tr>
  `).join('') + `
    <tr style="background: rgba(0, 245, 160, 0.04); border-top: 2px solid rgba(0, 245, 160, 0.2);">
      <td colspan="5" style="font-weight: 800; color: #fff; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em;">
        TOTAL REAL EN CARTERAS (CERO SALDOS ESTIMADOS):
      </td>
      <td class="cell-mono" style="color: var(--accent-emerald); font-weight: 900; font-size: 1rem;">
        $3.38 USDC
      </td>
      <td>
        <span class="badge-status success">100% EN POSESIÓN</span>
      </td>
    </tr>
  `;
}
