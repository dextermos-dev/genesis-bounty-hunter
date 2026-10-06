use anchor_lang::prelude::*;
use crate::state::MarketPool;

#[derive(Accounts)]
#[instruction(pool_id: [u8; 32])]
pub struct InitMarket<'info> {
    #[account(
        init,
        payer = authority,
        space = MarketPool::LEN,
        seeds = [b"market_pool", authority.key().as_ref(), pool_id.as_ref()],
        bump
    )]
    pub market_pool: Account<'info, MarketPool>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<InitMarket>, pool_id: [u8; 32], protocol_fee_bps: u16) -> Result<()> {
    let pool = &mut ctx.accounts.market_pool;
    pool.authority = ctx.accounts.authority.key();
    pool.pool_id = pool_id;
    pool.protocol_fee_bps = protocol_fee_bps;
    pool.cumulative_volume_lamports = 0;
    pool.total_deals_count = 0;
    pool.bump = ctx.bumps.market_pool;

    msg!("Nexus Market Pool initialized with {} bps protocol fee", protocol_fee_bps);
    Ok(())
}
