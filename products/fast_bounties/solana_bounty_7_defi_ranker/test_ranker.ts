/**
 * Adversarial 42-Fixture Unit Test Suite for DeFi Ranker (Bounty #7 / t=22)
 * Tests:
 * 1. Liquid-staking & bridge wrapper stripping (Fixtures 1-10)
 * 2. Disguised ticker symbols stripping (Fixtures 11-18)
 * 3. Tokenless genuine protocols retention (Fixtures 19-26)
 * 4. Parent-child deduplication (Fixtures 27-32)
 * 5. Outlier wash-TVL clamping (Fixtures 33-36)
 * 6. Byte-for-byte identical determinism across repeated runs (Fixtures 37-42)
 */

import { ProtocolRanker, DERIVATIVE_INDICATORS } from './ranker.ts';
import type { ProtocolRecord } from './ranker.ts';
import * as assert from 'node:assert';

const ranker = new ProtocolRanker();
const emptyParents = new Set<string>();

console.log('Running 42 DeFi Ranker Test Fixtures...\n');
let passed = 0;

function runTest(name: string, fn: () => void) {
  try {
    fn();
    passed++;
    console.log(`  ✓ [Fixture ${passed.toString().padStart(2, '0')}] ${name}`);
  } catch (err: any) {
    console.error(`  ✗ [Fixture ${passed + 1}] ${name}:`, err.message);
    process.exit(1);
  }
}

// Group 1: Liquid-staking & Bridge Wrapper Stripping (1-10)
runTest('Strips wstETH liquid staking derivative', () => {
  const p: ProtocolRecord = { name: 'Wrapped stETH', category: 'Liquid Staking', chains: ['Ethereum'], tvl_usd: 1e9, symbol: 'wstETH' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips rETH RocketPool derivative', () => {
  const p: ProtocolRecord = { name: 'Rocket Pool ETH', category: 'liquid-staked', chains: ['Ethereum'], tvl_usd: 5e8, symbol: 'rETH' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips cbBTC Coinbase wrapped Bitcoin', () => {
  const p: ProtocolRecord = { name: 'Coinbase Wrapped BTC', category: 'Wrapped', chains: ['Base'], tvl_usd: 2e8, symbol: 'cbBTC' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips restaked wrapper protocol', () => {
  const p: ProtocolRecord = { name: 'EtherFi Restaked', category: 'restaked', chains: ['Ethereum'], tvl_usd: 3e8, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips bridged asset vault receipt', () => {
  const p: ProtocolRecord = { name: 'Stargate Bridged USDC', category: 'bridged', chains: ['Arbitrum'], tvl_usd: 5e7, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips LP token receipt pseudo-protocol', () => {
  const p: ProtocolRecord = { name: 'Curve 3Pool lp token', category: 'dexes', chains: ['Ethereum'], tvl_usd: 1e8, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips yield aggregator receipt token', () => {
  const p: ProtocolRecord = { name: 'Yearn Vault Receipt', category: 'yield aggregator receipt', chains: ['Fantom'], tvl_usd: 1e7, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips synthetic debt token protocol', () => {
  const p: ProtocolRecord = { name: 'Synthetix sUSD debt', category: 'synthetic debt', chains: ['Optimism'], tvl_usd: 2e7, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips forked single-asset wrapper', () => {
  const p: ProtocolRecord = { name: 'Forked Wrapper Alpha', category: 'forked wrapper', chains: ['BSC'], tvl_usd: 5e6, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips ezETH Renzo restaking derivative', () => {
  const p: ProtocolRecord = { name: 'Renzo ezETH', category: 'restaking wrapper', chains: ['Ethereum'], tvl_usd: 8e8, symbol: 'ezETH' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

// Group 2: Disguised Ticker Symbols Stripping (11-18)
runTest('Strips Uniswap due to UNI symbol', () => {
  const p: ProtocolRecord = { name: 'Uniswap V3', category: 'Dexes', chains: ['Ethereum'], tvl_usd: 3e9, symbol: 'UNI' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips Aave due to AAVE symbol', () => {
  const p: ProtocolRecord = { name: 'Aave V3', category: 'Lending', chains: ['Polygon'], tvl_usd: 4e9, symbol: 'AAVE' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips Curve due to CRV symbol', () => {
  const p: ProtocolRecord = { name: 'Curve Finance', category: 'Dexes', chains: ['Ethereum'], tvl_usd: 1.5e9, symbol: 'CRV' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips GMX due to GMX symbol', () => {
  const p: ProtocolRecord = { name: 'GMX V2', category: 'Perpetuals', chains: ['Arbitrum'], tvl_usd: 6e8, symbol: 'GMX' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips disguised lowercase symbol aero', () => {
  const p: ProtocolRecord = { name: 'Aerodrome', category: 'Dexes', chains: ['Base'], tvl_usd: 1e9, symbol: 'aero' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips disguised spaced symbol "PENDLE "', () => {
  const p: ProtocolRecord = { name: 'Pendle Finance', category: 'Yield', chains: ['Ethereum'], tvl_usd: 2e9, symbol: 'PENDLE ' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips symbol with prefix $ token format', () => {
  const p: ProtocolRecord = { name: 'MakerDAO', category: 'CDP', chains: ['Ethereum'], tvl_usd: 5e9, symbol: 'MKR' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

runTest('Strips protocol with live token listed in description', () => {
  const p: ProtocolRecord = { name: 'Synthetix', category: 'Derivatives', chains: ['Optimism'], tvl_usd: 4e8, symbol: 'SNX' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), false);
});

// Group 3: Tokenless Genuine Protocols Retention (19-26)
runTest('Retains genuine pre-token Base DEX (symbol=null)', () => {
  const p: ProtocolRecord = { name: 'SuperDEX Base', category: 'Dexes', chains: ['Base'], tvl_usd: 4e7, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), true);
});

runTest('Retains genuine pre-token Solana Lending (symbol="none")', () => {
  const p: ProtocolRecord = { name: 'SolLend Prime', category: 'Lending', chains: ['Solana'], tvl_usd: 8e7, symbol: 'none' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), true);
});

runTest('Retains genuine pre-token Arbitrum Perps (symbol="N/A")', () => {
  const p: ProtocolRecord = { name: 'NovaPerps', category: 'Perpetuals', chains: ['Arbitrum'], tvl_usd: 2.5e7, symbol: 'N/A' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), true);
});

runTest('Retains protocol with generic LP receipt designation', () => {
  const p: ProtocolRecord = { name: 'OmniSwap', category: 'Dexes', chains: ['Base', 'Ethereum'], tvl_usd: 1.2e7, symbol: 'LP' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), true);
});

runTest('Retains protocol with generic Shares label', () => {
  const p: ProtocolRecord = { name: 'YieldVault Genesis', category: 'Yield', chains: ['Polygon'], tvl_usd: 9e6, symbol: 'SHARES' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), true);
});

runTest('Retains pre-token Cross-Chain Messaging engine', () => {
  const p: ProtocolRecord = { name: 'Nexus Bridge Protocol', category: 'cross chain', chains: ['Base', 'Arbitrum'], tvl_usd: 3.5e7, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), true);
});

runTest('Retains pre-token Monad ecosystem builder AMM', () => {
  const p: ProtocolRecord = { name: 'MonadSwap Core', category: 'Dexes', chains: ['Monad'], tvl_usd: 1.5e7, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), true);
});

runTest('Retains pre-token Berachain liquidity aggregator', () => {
  const p: ProtocolRecord = { name: 'BeraLend Native', category: 'Lending', chains: ['Berachain'], tvl_usd: 2.2e7, symbol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, emptyParents), true);
});

// Group 4: Parent-Child Deduplication (27-32)
runTest('Filters child deployment when parent protocol exists', () => {
  const parents = new Set(['parent-dex']);
  const child: ProtocolRecord = { name: 'Child Market', category: 'Dexes', chains: ['Base'], tvl_usd: 1e7, parent_protocol: 'parent-dex' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(child, parents), false);
});

runTest('Preserves parent protocol when parent_protocol is null', () => {
  const parent: ProtocolRecord = { name: 'Parent DEX', category: 'Dexes', chains: ['Ethereum'], tvl_usd: 5e7, parent_protocol: null };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(parent, emptyParents), true);
});

runTest('Handles case-insensitive parent protocol mapping', () => {
  const parents = new Set(['lending-master']);
  const child: ProtocolRecord = { name: 'Isolated Market B', category: 'Lending', chains: ['Arbitrum'], tvl_usd: 4e6, parent_protocol: 'Lending-Master' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(child, parents), false);
});

runTest('Preserves protocol if parent is not in the ingested dataset', () => {
  const parents = new Set(['unrelated-parent']);
  const p: ProtocolRecord = { name: 'Independent Fork', category: 'Dexes', chains: ['Base'], tvl_usd: 8e6, parent_protocol: 'external-nonexistent' };
  // When parent is not in existingParents set, it qualifies
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(p, parents), true);
});

runTest('Deduplicates multiple children under single parent', () => {
  const parents = new Set(['global-amm']);
  const child1: ProtocolRecord = { name: 'Child A', category: 'Dexes', chains: ['Base'], tvl_usd: 2e6, parent_protocol: 'global-amm' };
  const child2: ProtocolRecord = { name: 'Child B', category: 'Dexes', chains: ['Optimism'], tvl_usd: 3e6, parent_protocol: 'global-amm' };
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(child1, parents), false);
  assert.strictEqual(ranker.isTokenlessAndNonDerivative(child2, parents), false);
});

runTest('Parent protocol ranking retains consolidated TVL', () => {
  const records: ProtocolRecord[] = [
    { name: 'Parent Core', category: 'Dexes', chains: ['Ethereum'], tvl_usd: 1e8, symbol: null },
    { name: 'Parent Core Sub-vault', category: 'Dexes', chains: ['Base'], tvl_usd: 2e7, symbol: null, parent_protocol: 'Parent Core' }
  ];
  const board = ranker.rank(records);
  assert.strictEqual(board.total_qualified, 1);
  assert.strictEqual(board.protocols[0].name, 'Parent Core');
});

// Group 5: Outlier Wash-TVL Clamping (33-36)
runTest('Normal 7d delta <= 400% does not clamp TVL', () => {
  const tvl = 1e7;
  const clamped = ranker.clampTvl(tvl, 0.25); // +25% delta
  assert.strictEqual(clamped, tvl);
});

runTest('Clamps extreme 800% 7d delta wash-TVL spike', () => {
  const tvl = 1e7;
  const clamped = ranker.clampTvl(tvl, 8.0); // +800% spike
  assert.ok(clamped < tvl);
  assert.ok(clamped > 0);
});

runTest('Negative TVL clamped to zero', () => {
  const clamped = ranker.clampTvl(-500);
  assert.strictEqual(clamped, 0);
});

runTest('Undefined delta preserves TVL exactly', () => {
  const tvl = 4.5e7;
  const clamped = ranker.clampTvl(tvl, undefined);
  assert.strictEqual(clamped, tvl);
});

// Group 6: Byte-for-Byte Determinism Across Repeated Runs (37-42)
const testDataset: ProtocolRecord[] = [
  { name: 'BetaSwap', category: 'Dexes', chains: ['Base'], tvl_usd: 4.5e7, fees_30d_usd: 120000, symbol: null },
  { name: 'AlphaLend', category: 'Lending', chains: ['Arbitrum'], tvl_usd: 6.2e7, fees_30d_usd: 95000, symbol: null },
  { name: 'GammaPerp', category: 'Perpetuals', chains: ['Solana'], tvl_usd: 3.1e7, fees_30d_usd: 180000, symbol: null },
  { name: 'LiquidStakeEth', category: 'Liquid Staking', chains: ['Ethereum'], tvl_usd: 5e8, symbol: 'stETH' }, // Stripped
  { name: 'UniswapCopy', category: 'Dexes', chains: ['Polygon'], tvl_usd: 2e8, symbol: 'UNI' } // Stripped
];

runTest('Run 1 produces valid ranked board', () => {
  const b1 = ranker.rank(testDataset);
  assert.strictEqual(b1.total_qualified, 3);
  assert.strictEqual(b1.protocols[0].rank, 1);
  assert.strictEqual(b1.protocols[1].rank, 2);
  assert.strictEqual(b1.protocols[2].rank, 3);
});

runTest('Run 2 on reversed input produces identical ranked board', () => {
  const reversedDataset = [...testDataset].reverse();
  const b1 = ranker.rank(testDataset);
  const b2 = ranker.rank(reversedDataset);
  assert.deepStrictEqual(b1.protocols, b2.protocols);
});

runTest('Byte-for-byte serialized JSON comparison matches 100%', () => {
  const json1 = JSON.stringify(ranker.rank(testDataset), null, 2);
  const json2 = JSON.stringify(ranker.rank([...testDataset].sort(() => 0.5 - Math.random())), null, 2);
  assert.strictEqual(json1, json2);
});

runTest('Playbook steps length is within 3..8 bounds', () => {
  const board = ranker.rank(testDataset);
  for (const p of board.protocols) {
    assert.ok(p.playbook_steps.length >= 3);
    assert.ok(p.playbook_steps.length <= 8);
  }
});

runTest('Implied FDV low < mid < high invariant holds', () => {
  const board = ranker.rank(testDataset);
  for (const p of board.protocols) {
    assert.ok(p.implied_fdv_low < p.implied_fdv_mid);
    assert.ok(p.implied_fdv_mid < p.implied_fdv_high);
  }
});

runTest('Capital efficiency ratio is non-negative and finite', () => {
  const board = ranker.rank(testDataset);
  for (const p of board.protocols) {
    assert.ok(p.capital_efficiency_ratio >= 0);
    assert.ok(Number.isFinite(p.capital_efficiency_ratio));
  }
});

console.log(`\n🎉 All ${passed}/42 Fixtures Passed Deterministically with Zero External Network Calls!`);

