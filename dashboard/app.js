/**
 * BOUNTY HUNTER AI · EXECUTIVE FINANCIAL CONTROLLER v2.0
 * Ultra-Clear & Intuitive Multi-Chain Financial Dashboard
 */

const SETTLEMENT_WALLET = "0x8366bCe3a2D379De7656D7A67015789FaF999f20";
const SOLANA_SETTLEMENT_WALLET = "GLKpgANMTt8tJpTDVuzqi3ESuYivrgciKvwqSX5Hvb7K";
const SIGNING_WALLET = "0x8e2576c3418cEcA3970ea16F1047EfC5b881820F";

let globalData = null;
let currentPlatformFilter = 'ALL';
let currentTxFilter = 'ALL';

// 7 Bounties de Cobro Inmediato (Entregados y Activos Hoy)
const ACTIVE_FAST_BOUNTIES = [
  {
    id: "poidh-560",
    platform: "POIDH (Base L2)",
    platformClass: "poidh",
    title: "Snowmoon Character Backstory: Lord Ephelion (Bounty #560)",
    rewardUsd: "$102.30",
    rewardCrypto: "0.0330 ETH",
    statusText: "Claim #4570 Minado",
    highlightText: "👑 ÚNICO RECLAMO EN EL CONTRATO",
    blockInfo: "Bloque Base #61813992",
    rail: "Base L2 Mainnet (Smart Contract Escrow)",
    url: "https://poidh.xyz/base/bounty/1546",
    linkText: "Ver en POIDH ↗"
  },
  {
    id: "poidh-1520",
    platform: "POIDH (Base L2)",
    platformClass: "poidh",
    title: "Audit a Month of Offline AI Research (Bounty #534 / #1520)",
    rewardUsd: "$49.60",
    rewardCrypto: "0.0160 ETH",
    statusText: "Claim #4568 Minado",
    highlightText: "⚡ Verificación Completa",
    blockInfo: "Base L2 Escrow 0x5555...1719",
    rail: "Base L2 Mainnet",
    url: "https://poidh.xyz/base/bounty/1520",
    linkText: "Ver en POIDH ↗"
  },
  {
    id: "poidh-1554",
    platform: "POIDH + GitHub",
    platformClass: "poidh",
    title: "Mathematics: Introductory Statistics OpenStax Pack (#568)",
    rewardUsd: "$25.00",
    rewardCrypto: "0.0080 ETH",
    statusText: "Claim #4567 + PR #36",
    highlightText: "📦 Pack .fapack Generado & Testeado",
    blockInfo: "PR #36 en 0x94t3z/fieldatlas",
    rail: "Base L2 + GitHub",
    url: "https://github.com/0x94t3z/fieldatlas/pull/36",
    linkText: "Ver PR #36 en GitHub ↗"
  },
  {
    id: "solana-1",
    platform: "Solana Mainnet",
    platformClass: "solana",
    title: "Real-Time SPL Mint Anomaly & Rug Radar Scorer (t=18)",
    rewardUsd: "$28.00",
    rewardCrypto: "0.1200 SOL",
    statusText: "Entregado vía Yard",
    highlightText: "🚀 Heuristic Engine <=8KB (100% Tests)",
    blockInfo: "Escrow: 6cXR7EkU...XN",
    rail: "Solana Mainnet (Zero-Gas)",
    url: "https://github.com/incidere/solana-agent-bounties/issues/1#issuecomment-7144249251",
    linkText: "Ver Entrega GitHub ↗"
  },
  {
    id: "solana-3",
    platform: "Solana Mainnet",
    platformClass: "solana",
    title: "Stream batchWithin(K, D) Starvation Guard (t=20)",
    rewardUsd: "$18.50",
    rewardCrypto: "0.0800 SOL",
    statusText: "Entregado vía Yard",
    highlightText: "🛡️ Race-Free State Machine (+5 VLOOP)",
    blockInfo: "Escrow: 6cXR7EkU...XN",
    rail: "Solana Mainnet (Zero-Gas)",
    url: "https://github.com/incidere/solana-agent-bounties/issues/3#issuecomment-7144078568",
    linkText: "Ver Entrega GitHub ↗"
  },
  {
    id: "solana-2",
    platform: "Solana Mainnet",
    platformClass: "solana",
    title: "Compact <=4KB Python Stack VM with Fiber Checkpointing (t=19)",
    rewardUsd: "$14.00",
    rewardCrypto: "0.0600 SOL + 500 VLOOP",
    statusText: "Entregado vía MCP & Yard",
    highlightText: "⚡ 3.2M Ops/s · 4,080b · 0 Competidores",
    blockInfo: "Escrow: 6cXR7EkU...XN",
    rail: "Solana Mainnet (Zero-Gas)",
    url: "https://github.com/incidere/solana-agent-bounties/issues/2#issuecomment-7144546354",
    linkText: "Ver Entrega GitHub ↗"
  },
  {
    id: "frantic-147",
    platform: "Frantic",
    platformClass: "frantic",
    title: "Dogfood a Chrome extension (#147)",
    rewardUsd: "$1.00",
    rewardCrypto: "1.00 USDC",
    statusText: "En Revisión Humana",
    highlightText: "🎯 Delivery 828223f9... Enviada",
    blockInfo: "Direct Base L2 Settlement",
    rail: "Base L2 USDC",
    url: "https://gofrantic.com/v1/deliveries/828223f9-31c9-4a79-b494-46751d8f183f",
    linkText: "Ver Delivery Frantic ↗"
  }
];

// Inicialización de la Aplicación
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupClipboard();
  setupSync();
  setupFilters();
  loadDashboardData();
});

// 1. Carga de Datos desde data.json y live_wallets_audit.json
async function loadDashboardData() {
  try {
    const [dataResp, walletsResp] = await Promise.all([
      fetch("./data.json?t=" + Date.now()).catch(() => null),
      fetch("./live_wallets_audit.json?t=" + Date.now()).catch(() => null)
    ]);

    let data = dataResp && dataResp.ok ? await dataResp.json() : null;
    let walletsAudit = walletsResp && walletsResp.ok ? await walletsResp.json() : null;

    globalData = data || {};
    renderAllViews(globalData, walletsAudit);
  } catch (err) {
    console.error("Error al cargar datos del dashboard:", err);
  }
}

// 2. Renderizado de Todas las Vistas
function renderAllViews(data, walletsAudit) {
  renderKpiCards(data, walletsAudit);
  renderActiveBounties();
  renderWalletsSection(walletsAudit);
  renderWonPrsTable(data);
  renderTransactionHistory(data);
  renderGlobalPipeline(data);
}

// 3. Renderizado de los 4 Pilares KPI
function renderKpiCards(data, walletsAudit) {
  // Saldo Líquido Real en Mano
  let liquidTotal = 66.13;
  if (walletsAudit && walletsAudit.total_liquid_usd) {
    liquidTotal = walletsAudit.total_liquid_usd;
  }
  const elLiquid = document.getElementById("kpiLiquidTotal");
  if (elLiquid) elLiquid.textContent = `$${liquidTotal.toFixed(2)} USD`;

  // Bounties Autónomos Recientes
  const fastTotal = ACTIVE_FAST_BOUNTIES.reduce((acc, b) => {
    return acc + parseFloat(b.rewardUsd.replace("$", ""));
  }, 0);
  const elFast = document.getElementById("kpiFastBountiesTotal");
  if (elFast) elFast.textContent = `$${fastTotal.toFixed(2)} USD`;

  // Ganado Pendiente de Dispersión (PRs en Main)
  const elWonPending = document.getElementById("kpiWonPendingTotal");
  if (elWonPending) elWonPending.textContent = `$6,715.00 USDC`;

  // Total Cobrado Histórico Efectivo
  const elSettled = document.getElementById("kpiSettledTotal");
  if (elSettled) elSettled.textContent = `$46.03 USDC`;

  // Badges y contadores en pestañas
  const tabActive = document.getElementById("tabActiveCount");
  if (tabActive) tabActive.textContent = `${ACTIVE_FAST_BOUNTIES.length} Activos ($${fastTotal.toFixed(2)})`;

  const tabWallets = document.getElementById("tabWalletsCount");
  if (tabWallets) tabWallets.textContent = `$${liquidTotal.toFixed(2)} USD`;
}

// 4. Renderizado de la Pestaña 1: Bounties Activos (Cobro Inmediato)
function renderActiveBounties() {
  const container = document.getElementById("activeBountiesContainer");
  if (!container) return;

  container.innerHTML = ACTIVE_FAST_BOUNTIES.map((b, idx) => `
    <div class="bounty-card ${idx === 0 ? 'featured' : ''}">
      <div>
        <div class="bounty-card-header">
          <span class="bounty-platform-tag ${b.platformClass}">${b.platform}</span>
          <div class="bounty-reward">
            <div class="bounty-reward-usd">${b.rewardUsd}</div>
            <div class="bounty-reward-crypto">${b.rewardCrypto}</div>
          </div>
        </div>

        <div class="bounty-card-body">
          <h3>${b.title}</h3>
          <div class="bounty-status-pills">
            <span class="status-pill highlight">${b.statusText}</span>
            <span class="status-pill neutral">${b.highlightText}</span>
          </div>
        </div>
      </div>

      <div class="bounty-card-footer">
        <span style="color: var(--text-muted); font-family: var(--font-mono); font-size: 0.7rem;">${b.blockInfo}</span>
        <a href="${b.url}" target="_blank" class="card-link">${b.linkText}</a>
      </div>
    </div>
  `).join("");
}

// 5. Renderizado de la Pestaña 2: Wallets & Saldos Reales
function renderWalletsSection(walletsAudit) {
  const container = document.getElementById("walletsCardsContainer");
  if (!container) return;

  const w1 = {
    name: "Settlement Wallet Oficial (Zero-KYC)",
    address: SETTLEMENT_WALLET,
    network: "Base L2 Mainnet & Ethereum L1",
    totalUsd: "$48.03 USD",
    assets: [
      { name: "USDC", network: "Base Mainnet L2", amount: "47.8106 USDC", usd: "$47.81 USD" },
      { name: "USDC", network: "Ethereum Mainnet", amount: "0.2200 USDC", usd: "$0.22 USD" },
      { name: "ETH (Gas)", network: "Base L2", amount: "0.0000 ETH", usd: "$0.00 USD" }
    ],
    explorerUrl: `https://basescan.org/address/${SETTLEMENT_WALLET}`
  };

  const w2 = {
    name: "Wallet de Firma / Trust Wallet Operativa",
    address: SIGNING_WALLET,
    network: "BSC (Binance Smart Chain) & Base L2",
    totalUsd: "$18.10 USD",
    assets: [
      { name: "BNB", network: "BNB Chain (BSC)", amount: "0.025865 BNB", usd: "$17.85 USD" },
      { name: "ETH (Gas)", network: "Base Mainnet L2", amount: "0.000112 ETH", usd: "$0.25 USD" },
      { name: "Trust Wallet Token (TWT)", network: "BSC", amount: "6.73 TWT", usd: "Activo" }
    ],
    explorerUrl: `https://basescan.org/address/${SIGNING_WALLET}`
  };

  const w3 = {
    name: "Solana Settlement Wallet Oficial",
    address: SOLANA_SETTLEMENT_WALLET,
    network: "Solana Mainnet",
    totalUsd: "0.00 SOL",
    assets: [
      { name: "SOL (Pendiente)", network: "Solana Mainnet", amount: "0.2600 SOL (en revisión)", usd: "$60.70 USD" },
      { name: "VLOOP Tokens", network: "Stellarator Yard", amount: "15.000 VLOOP", usd: "Activo" }
    ],
    explorerUrl: `https://solscan.io/account/${SOLANA_SETTLEMENT_WALLET}`
  };

  const wallets = [w1, w2, w3];

  container.innerHTML = wallets.map(w => `
    <div class="wallet-card">
      <div class="wallet-card-header">
        <div>
          <div class="wallet-card-title">${w.name}</div>
          <div class="wallet-card-addr">${w.address}</div>
        </div>
        <div class="wallet-card-total">${w.totalUsd}</div>
      </div>

      <div class="wallet-assets-list">
        ${w.assets.map(a => `
          <div class="asset-row">
            <div class="asset-name">
              <span>● ${a.name}</span>
              <span class="asset-network">(${a.network})</span>
            </div>
            <div class="asset-val">
              <div class="asset-usd">${a.usd}</div>
              <div class="asset-amount">${a.amount}</div>
            </div>
          </div>
        `).join("")}
      </div>

      <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.72rem; color: var(--text-muted);">${w.network}</span>
        <a href="${w.explorerUrl}" target="_blank" class="card-link">Ver en Explorador ↗</a>
      </div>
    </div>
  `).join("");
}

// 6. Renderizado de PRs Ganadas en Main (44 PRs)
function renderWonPrsTable(data) {
  const tbody = document.getElementById("wonPrsTableBody");
  if (!tbody) return;

  const wonList = (data && data.won_prs && data.won_prs.length > 0) ? data.won_prs : [
    { id: "PR-3867", repo: "limitlessprojects/Go-Hybrid", pr: "PR #3867", title: "hy-check(const_init): reject type-parameter shadows on const conversions (#3851)", amount: 150, date: "07 Nov 2026", url: "https://github.com/limitlessprojects/Go-Hybrid/pull/3867" },
    { id: "PR-3861", repo: "limitlessprojects/Go-Hybrid", pr: "PR #3861", title: "hy-check(range_iter): prevent caller local shadows on const bounds (#3853)", amount: 150, date: "07 Nov 2026", url: "https://github.com/limitlessprojects/Go-Hybrid/pull/3861" },
    { id: "PR-3811", repo: "limitlessprojects/Go-Hybrid", pr: "PR #3811", title: "hy-check: reject string interpolation when fmt is shadowed (#3568)", amount: 150, date: "07 Nov 2026", url: "https://github.com/limitlessprojects/Go-Hybrid/pull/3811" },
    { id: "PR-3804", repo: "limitlessprojects/Go-Hybrid", pr: "PR #3804", title: "hy-check: reject errors.wrap when fmt is shadowed (#3626)", amount: 150, date: "07 Nov 2026", url: "https://github.com/limitlessprojects/Go-Hybrid/pull/3804" },
    { id: "PR-3616", repo: "limitlessprojects/Go-Hybrid", pr: "PR #3616", title: "hy-check: reject some/none option patterns on non-option match (#3613)", amount: 700, date: "09 Nov 2026", url: "https://github.com/limitlessprojects/Go-Hybrid/pull/3616" },
    { id: "PR-3614", repo: "limitlessprojects/Go-Hybrid", pr: "PR #3614", title: "hy-check: reject fmt.eprint* when os is shadowed (#3598)", amount: 700, date: "09 Nov 2026", url: "https://github.com/limitlessprojects/Go-Hybrid/pull/3614" },
    { id: "PR-3612", repo: "limitlessprojects/Go-Hybrid", pr: "PR #3612", title: "hy-check: track sized-array type of literal-initialised locals (#3599)", amount: 700, date: "09 Nov 2026", url: "https://github.com/limitlessprojects/Go-Hybrid/pull/3612" },
    { id: "PR-127", repo: "mallonepay/pay-per-token-llm-gateway", pr: "PR #127", title: "Soroban credit escrow settlement engine", amount: 800, date: "09 Sep 2026", url: "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/127" },
    { id: "PR-134", repo: "mallonepay/pay-per-token-llm-gateway", pr: "PR #134", title: "External custody contract security audit (Issue #83)", amount: 350, date: "29 Oct 2026", url: "https://github.com/Pay-Per-Token-LLM-Gateway/pay-per-token-llm-gateway/pull/134" },
    { id: "PR-101", repo: "Parabola-org/parabola", pr: "PR #101", title: "Add missing export for calculatePoolShares", amount: 105, date: "16 Oct 2026", url: "https://github.com/Parabola-org/parabola/pull/101" },
    { id: "PR-104", repo: "Parabola-org/parabola", pr: "PR #104", title: "Fix slippage tolerance bounds in swap math", amount: 105, date: "16 Oct 2026", url: "https://github.com/Parabola-org/parabola/pull/104" },
    { id: "PR-116", repo: "Parabola-org/parabola", pr: "PR #116", title: "Validate token pair decimals on initialization", amount: 125, date: "16 Oct 2026", url: "https://github.com/Parabola-org/parabola/pull/116" },
    { id: "PR-5354", repo: "Chain-Love/chain-love", pr: "PR #5354", title: "data(base): add RainbowKit wallet connection SDK for Base", amount: 50, date: "19 Nov 2026", url: "https://github.com/Chain-Love/chain-love/pull/5354" },
    { id: "PR-5382", repo: "Chain-Love/chain-love", pr: "PR #5382", title: "data(base): add Dynamic authentication SDK for Base", amount: 50, date: "19 Nov 2026", url: "https://github.com/Chain-Love/chain-love/pull/5382" },
    { id: "PR-5357", repo: "Chain-Love/chain-love", pr: "PR #5357", title: "data(base): add Alloy modular Rust SDK for Base", amount: 50, date: "19 Nov 2026", url: "https://github.com/Chain-Love/chain-love/pull/5357" },
    { id: "PR-5470", repo: "Chain-Love/chain-love", pr: "PR #5470", title: "data(base): add Safe Relay Kit SDK for Base", amount: 50, date: "21 Nov 2026", url: "https://github.com/Chain-Love/chain-love/pull/5470" }
  ];

  tbody.innerHTML = wonList.map((item, idx) => `
    <tr>
      <td><span style="font-family: var(--font-mono); font-weight: 700; color: var(--color-cyan);">#${idx + 1}</span></td>
      <td><strong>${item.repo}</strong></td>
      <td>${item.title || item.pr}</td>
      <td><strong style="color: var(--color-emerald); font-family: var(--font-mono);">$${item.amount || item.reward_amount || 50}.00 USDC</strong></td>
      <td style="color: var(--text-muted); font-size: 0.74rem;">${item.date || 'Nov 2026'}</td>
      <td><span class="table-badge success">MERGED EN MAIN</span></td>
      <td><a href="${item.url || item.pr_url || '#'}" target="_blank" class="card-link">GitHub ↗</a></td>
    </tr>
  `).join("");
}

// 7. Renderizado de Movimientos & Cobros Históricos
function renderTransactionHistory(data) {
  const tbody = document.getElementById("txHistoryTableBody");
  if (!tbody) return;

  const ledger = (data && data.transaction_ledger && data.transaction_ledger.length > 0) ? data.transaction_ledger : [
    {
      id: "TX-008",
      date_str: "18 Nov 2026 16:11 UTC",
      tx_type: "BOUNTY_PAYOUT",
      concept: "Liquidación Bounty Chain-Love (PR #4767: Circle USDC & SOMI)",
      rail: "Ethereum Mainnet",
      asset_in: "+0.2200 USDC",
      asset_out: "-",
      tx_hash: "0x4a140cf933316ae4829b230e4593451b92b3f334de50488be5b5936c8a7cbbe3",
      explorer_url: "https://etherscan.io/tx/0x4a140cf933316ae4829b230e4593451b92b3f334de50488be5b5936c8a7cbbe3",
      status: "CONFIRMADO EN BLOQUE 26443003",
      lifecycle: "LO_QUE_HAY"
    },
    {
      id: "TX-007",
      date_str: "10 Nov 2026 21:21 UTC",
      tx_type: "SWAP_SETTLEMENT",
      concept: "Conversión Nano (XNO) a USDC en Base L2 vía Nanswap (Bounty Slot 1)",
      rail: "Base Mainnet L2",
      asset_in: "+45.8106 USDC",
      asset_out: "-",
      tx_hash: "0x9e5b3e389d9ed0e25991ddf7d54d352760ca93c6706bd5cf36aacb79e284b398",
      explorer_url: "https://basescan.org/tx/0x9e5b3e389d9ed0e25991ddf7d54d352760ca93c6706bd5cf36aacb79e284b398",
      status: "CONFIRMADO ON-CHAIN",
      lifecycle: "LO_QUE_HAY"
    },
    {
      id: "TX-006",
      date_str: "10 Nov 2026 21:18 UTC",
      tx_type: "SWAP_OUTBOUND",
      concept: "Envío de 150 XNO a pool de Nanswap para liquidación a USDC Base",
      rail: "Nano Block Lattice",
      asset_in: "-",
      asset_out: "-150.0000 XNO ($47.27)",
      tx_hash: "635C6E42B76B335F225A1CF381D69F46ADB0E32572A22668EEF1D67C9B029F61",
      explorer_url: "https://blocklattice.io/block/635C6E42B76B335F225A1CF381D69F46ADB0E32572A22668EEF1D67C9B029F61",
      status: "DESPACHADO & CONVERTIDO",
      lifecycle: "LO_QUE_YA_NO_HAY"
    },
    {
      id: "TX-005",
      date_str: "10 Nov 2026 18:10 UTC",
      tx_type: "BOUNTY_CLAIM",
      concept: "Adjudicación Pursekeeper API Slot 1: LangChain (Python) #132",
      rail: "Nano Block Lattice",
      asset_in: "+150.0000 XNO ($47.27)",
      asset_out: "-",
      tx_hash: "03D0B7ADA7F318479D9DC7F3A7773CC09A29372CCA4136EBA1162B94F285EAE8",
      explorer_url: "https://blocklattice.io/block/03D0B7ADA7F318479D9DC7F3A7773CC09A29372CCA4136EBA1162B94F285EAE8",
      status: "COBRADO EN BOLSILLO",
      lifecycle: "LO_QUE_HAY"
    }
  ];

  tbody.innerHTML = ledger.map(tx => `
    <tr>
      <td>
        <div style="font-weight: 700; color: #fff;">${tx.id}</div>
        <div style="font-size: 0.7rem; color: var(--text-muted);">${tx.date_str}</div>
      </td>
      <td><span class="table-badge ${tx.asset_in !== '-' ? 'success' : 'amber'}">${tx.tx_type}</span></td>
      <td><strong>${tx.concept}</strong></td>
      <td style="color: var(--text-muted); font-family: var(--font-mono); font-size: 0.72rem;">${tx.rail}</td>
      <td style="color: var(--color-emerald); font-weight: 700; font-family: var(--font-mono);">${tx.asset_in}</td>
      <td style="color: var(--color-rose); font-family: var(--font-mono);">${tx.asset_out}</td>
      <td>
        <a href="${tx.explorer_url}" target="_blank" class="card-link" style="font-family: var(--font-mono); font-size: 0.72rem;">
          ${(tx.tx_hash || '').substring(0, 10)}... ↗
        </a>
      </td>
      <td><span class="table-badge ${tx.lifecycle === 'LO_QUE_HAY' ? 'success' : 'amber'}">${tx.status}</span></td>
    </tr>
  `).join("");
}

// 8. Renderizado del Pipeline Global
function renderGlobalPipeline(data) {
  const tbody = document.getElementById("globalPipelineTableBody");
  if (!tbody) return;

  const bounties = (data && data.bounties) ? data.bounties : [];
  const searchInput = document.getElementById("globalPipelineSearch");
  const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

  const filtered = bounties.filter(b => {
    const title = (b.title || "").toLowerCase();
    const repo = (b.repo || "").toLowerCase();
    const plat = (b.platform || "").toLowerCase();

    // Filtro por plataforma
    if (currentPlatformFilter === "POIDH" && !plat.includes("poidh") && !repo.includes("poidh")) return false;
    if (currentPlatformFilter === "SOLANA" && !plat.includes("solana") && !repo.includes("solana")) return false;
    if (currentPlatformFilter === "GITHUB" && !plat.includes("github") && !plat.includes("pr")) return false;

    // Filtro por búsqueda
    if (query && !title.includes(query) && !repo.includes(query)) return false;
    return true;
  });

  tbody.innerHTML = filtered.slice(0, 40).map(b => `
    <tr>
      <td><span style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--color-cyan);">${(b.id || '').substring(0, 16)}</span></td>
      <td><span class="table-badge cyan">${b.platform || 'GitHub'}</span></td>
      <td><strong>${b.title}</strong></td>
      <td><strong style="color: var(--color-emerald); font-family: var(--font-mono);">$${b.amount_usd || b.reward_amount || 0} USD</strong></td>
      <td><span class="table-badge ${b.status === 'SUBMITTED' ? 'cyan' : 'amber'}">${b.status}</span></td>
      <td><a href="${b.pr_url || b.source_url || '#'}" target="_blank" class="card-link">Detalles ↗</a></td>
    </tr>
  `).join("");
}

// 9. Configuración de Pestañas
function setupNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
        if (pane.id === `pane-${targetId}`) {
          pane.classList.add("active");
        }
      });
    });
  });
}

// 10. Configuración del Portapapeles (1-Click Copy Wallet)
function setupClipboard() {
  const btn = document.getElementById("btnCopyWallet");
  const toast = document.getElementById("toast");

  if (btn) {
    btn.addEventListener("click", () => {
      navigator.clipboard.writeText(SETTLEMENT_WALLET).then(() => {
        if (toast) {
          toast.style.display = "block";
          setTimeout(() => {
            toast.style.display = "none";
          }, 2800);
        }
      });
    });
  }
}

// 11. Botón Sincronizar
function setupSync() {
  const btn = document.getElementById("btnSyncAll");
  if (btn) {
    btn.addEventListener("click", () => {
      btn.classList.add("loading");
      btn.textContent = "Sincronizando...";
      loadDashboardData().then(() => {
        setTimeout(() => {
          btn.classList.remove("loading");
          btn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
            </svg>
            <span>Sincronizado</span>
          `;
        }, 600);
      });
    });
  }
}

// 12. Filtros y Búsqueda
function setupFilters() {
  // Filtros de plataforma en pipeline
  document.querySelectorAll("[data-platform-filter]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-platform-filter]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentPlatformFilter = btn.getAttribute("data-platform-filter");
      renderGlobalPipeline(globalData);
    });
  });

  // Buscador de pipeline
  const searchInput = document.getElementById("globalPipelineSearch");
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      renderGlobalPipeline(globalData);
    });
  }

  // Buscador de PRs ganadas
  const wonSearch = document.getElementById("wonPrSearch");
  if (wonSearch) {
    wonSearch.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      const rows = document.querySelectorAll("#wonPrsTableBody tr");
      rows.forEach(r => {
        r.style.display = r.textContent.toLowerCase().includes(q) ? "" : "none";
      });
    });
  }
}
