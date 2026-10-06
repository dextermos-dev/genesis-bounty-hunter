use anchor_lang::prelude::*;

pub mod errors;
pub mod instructions;
pub mod state;

use instructions::init_market::*;
use instructions::deposit_liquidity::*;
use instructions::atomic_settle::*;

declare_id!("NexuS11111111111111111111111111111111111111");

#[program]
pub mod nexus_protocol {
    use super::*;

    /// Initialize a new decentralized autonomous market pool
    pub fn init_market(ctx: Context<InitMarket>, pool_id: [u8; 32], protocol_fee_bps: u16) -> Result<()> {
        instructions::init_market::handler(ctx, pool_id, protocol_fee_bps)
    }

    /// Buyer agent deposits escrow collateral for a matched micro-task
    pub fn deposit_liquidity(ctx: Context<DepositLiquidity>, deal_id: [u8; 32], amount: u64, duration_seconds: i64) -> Result<()> {
        instructions::deposit_liquidity::handler(ctx, deal_id, amount, duration_seconds)
    }

    /// Verifies cryptographic proof and executes atomic instant settlement to seller
    pub fn atomic_settle(ctx: Context<AtomicSettle>, proof_hash: [u8; 32]) -> Result<()> {
        instructions::atomic_settle::handler(ctx, proof_hash)
    }
}
