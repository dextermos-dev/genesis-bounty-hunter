/**
 * Offline Protocol Snapshot Derivative Stripper & Implied-FDV Ranker (Bounty #7 / t=22)
 * Deterministic Zero-Network Node 22+ TypeScript CLI
 * Zero external npm runtime dependencies.
 * Byte-for-byte identical output across two runs.
 */

import * as fs from 'node:fs';
import * as path from 'node:path';

export interface ProtocolRecord {
  name: string;
  category: string;
  chains: string[];
  tvl_usd: number;
  tvl_7d_delta?: number;
  fees_30d_usd?: number;
  revenue_30d_usd?: number;
  symbol?: string | null;
  parent_protocol?: string | null;
  governance_links?: string[];
  description?: string;
}

export interface RankedEntry {
  rank: number;
  name: string;
  category: string;
  chains: string[];
  tvl_usd: number;
  implied_fdv_low: number;
  implied_fdv_mid: number;
  implied_fdv_high: number;
  capital_efficiency_ratio: number;
  playbook_steps: string[];
}

export interface BoardOutput {
  version: string;
  timestamp: string;
  total_ingested: number;
  total_qualified: number;
  protocols: RankedEntry[];
}

export const DERIVATIVE_INDICATORS = [
  'liquid-staked', 'liquid staking', 'restaked', 'restaking wrapper',
  'wrapped', 'bridged', 'vault receipt', 'lp token', 'forked wrapper',
  'yield aggregator receipt', 'synthetic debt'
];

export const DERIVATIVE_PREFIXES = ['w', 'st', 'rst', 'ez', 'cb', 'r', 'k', 's'];
export const DERIVATIVE_BASE_TOKENS = ['eth', 'btc', 'sol', 'usdc', 'usdt', 'matic', 'avax'];

export const SECTOR_MULTIPLIERS: Record<string, { tvl: number; fee: number }> = {
  'dexes': { tvl: 1.8, fee: 18.0 },
  'lending': { tvl: 1.2, fee: 14.0 },
  'derivatives': { tvl: 2.2, fee: 20.0 },
  'perpetuals': { tvl: 2.5, fee: 22.0 },
  'yield': { tvl: 0.8, fee: 10.0 },
  'cross chain': { tvl: 1.5, fee: 16.0 },
  'cdp': { tvl: 1.1, fee: 12.0 },
  'liquid staking': { tvl: 0.6, fee: 8.0 },
  'default': { tvl: 1.0, fee: 15.0 }
};

export class ProtocolRanker {
  public isTokenlessAndNonDerivative(p: ProtocolRecord, existingParents: Set<string>): boolean {
    const nameLow = p.name.toLowerCase();
    const descLow = (p.description || '').toLowerCase();
    const catLow = p.category.toLowerCase();
    const symbolLow = (p.symbol || '').trim().toLowerCase();

    // 1. Rule: Strip if already has live liquid governance/utility token
    if (symbolLow && symbolLow !== 'none' && symbolLow !== 'null' && symbolLow !== 'n/a') {
      if (!['lp', 'vault', 'receipt', 'shares'].includes(symbolLow)) {
        return false;
      }
    }

    // 2. Rule: Strip wrapper derivatives
    for (const ind of DERIVATIVE_INDICATORS) {
      if (nameLow.includes(ind) || catLow.includes(ind) || descLow.includes(ind)) {
        return false;
      }
    }

    // Check prefixed wrapper symbols
    for (const base of DERIVATIVE_BASE_TOKENS) {
      for (const pre of DERIVATIVE_PREFIXES) {
        if (symbolLow === `${pre}${base}`) {
          return false;
        }
      }
    }

    // 3. Rule: Prevent parent-child double counting
    if (p.parent_protocol && existingParents.has(p.parent_protocol.toLowerCase())) {
      return false;
    }

    return true;
  }

  public clampTvl(tvl: number, delta7d?: number): number {
    if (tvl <= 0) return 0;
    if (delta7d && delta7d > 4.0) {
      const excess = delta7d - 4.0;
      return tvl / (1.0 + excess * 0.4);
    }
    return tvl;
  }

  public generatePlaybook(p: ProtocolRecord): string[] {
    const cat = p.category.toLowerCase();
    const primaryChain = (p.chains && p.chains.length > 0) ? p.chains[0] : 'Base';

    if (cat.includes('dex') || cat.includes('swap')) {
      return [
        `Deposit initial liquidity into standard two-asset pool on ${primaryChain}`,
        `Execute recurring micro-swaps across supported paired tokens to build routing volume`,
        `Maintain continuous LP position for >= 14 epoch days`,
        `Stake LP receipt into gauge contract if fee-sharing is enabled`,
        `Participate in snapshot community gauge signaling`
      ];
    } else if (cat.includes('lend') || cat.includes('borrow')) {
      return [
        `Supply core blue-chip collateral into isolated market on ${primaryChain}`,
        `Borrow low-volatility asset within conservative health factor >= 1.75`,
        `Accrue interest across continuous multi-week accounting window`,
        `Repay borrowed balance to demonstrate lifecycle solvency`,
        `Participate in risk parameter governance discussions`
      ];
    } else if (cat.includes('perp') || cat.includes('deriv')) {
      return [
        `Deposit margin collateral into clearing house contract on ${primaryChain}`,
        `Open hedged delta-neutral position across low-spread market`,
        `Execute limit orders to provide non-toxic maker liquidity`,
        `Maintain active collateral state for >= 21 calendar days`,
        `Withdraw fractional margin to test settlement pipeline`
      ];
    } else {
      return [
        `Connect verified smart wallet to core contract interface on ${primaryChain}`,
        `Execute baseline interaction transaction meeting protocol minimum tier`,
        `Retain continuous position across multi-epoch monitoring duration`,
        `Claim accrued utility rewards where applicable`
      ];
    }
  }

  public calculateImpliedFdv(p: ProtocolRecord): { low: number; mid: number; high: number; efficiency: number } {
    const cat = p.category.toLowerCase();
    const mult = SECTOR_MULTIPLIERS[cat] || SECTOR_MULTIPLIERS['default'];

    const clampedTvl = this.clampTvl(p.tvl_usd, p.tvl_7d_delta);
    const feesAnnualized = (p.fees_30d_usd || 0) * 12.0;

    const efficiency = clampedTvl > 0 ? Number((feesAnnualized / clampedTvl).toFixed(4)) : 0.0;
    const tvlVal = clampedTvl * mult.tvl;
    const feeVal = feesAnnualized * mult.fee;

    const baseFdv = Math.max(tvlVal, (tvlVal * 0.6 + feeVal * 0.4));

    const low = Math.round(baseFdv * 0.7);
    const mid = Math.round(baseFdv);
    const high = Math.round(baseFdv * 1.45);

    return { low, mid, high, efficiency };
  }

  public rank(records: ProtocolRecord[]): BoardOutput {
    const sorted = [...records].sort((a, b) => a.name.localeCompare(b.name));

    const existingParents = new Set<string>();
    for (const p of sorted) {
      if (p.parent_protocol) {
        existingParents.add(p.parent_protocol.toLowerCase());
      }
    }

    const qualified: RankedEntry[] = [];
    for (const p of sorted) {
      if (!this.isTokenlessAndNonDerivative(p, existingParents)) {
        continue;
      }

      const { low, mid, high, efficiency } = this.calculateImpliedFdv(p);
      const steps = this.generatePlaybook(p);

      qualified.push({
        rank: 0,
        name: p.name,
        category: p.category,
        chains: [...(p.chains || [])].sort(),
        tvl_usd: Math.round(p.tvl_usd),
        implied_fdv_low: low,
        implied_fdv_mid: mid,
        implied_fdv_high: high,
        capital_efficiency_ratio: efficiency,
        playbook_steps: steps
      });
    }

    qualified.sort((a, b) => {
      if (b.implied_fdv_mid !== a.implied_fdv_mid) {
        return b.implied_fdv_mid - a.implied_fdv_mid;
      }
      return a.name.localeCompare(b.name);
    });

    qualified.forEach((item, idx) => {
      item.rank = idx + 1;
    });

    return {
      version: "2.2.0-deterministic",
      timestamp: "2026-11-24T00:00:00Z",
      total_ingested: records.length,
      total_qualified: qualified.length,
      protocols: qualified
    };
  }
}

// CLI Execution
const isMain = process.argv[1] && (
  process.argv[1].endsWith('ranker.ts') || 
  process.argv[1].endsWith('ranker.js')
);

if (isMain) {
  const args = process.argv.slice(2);
  const inputPath = args[0] || 'sample_protocols.json';
  const outputPath = args[1] || 'board.json';

  if (fs.existsSync(inputPath)) {
    const raw = fs.readFileSync(inputPath, 'utf-8');
    const protocols: ProtocolRecord[] = JSON.parse(raw);
    const ranker = new ProtocolRanker();
    const board = ranker.rank(protocols);
    fs.writeFileSync(outputPath, JSON.stringify(board, null, 2), 'utf-8');
    console.log(`Ranked ${board.total_qualified} / ${board.total_ingested} protocols -> ${outputPath}`);
  }
}

