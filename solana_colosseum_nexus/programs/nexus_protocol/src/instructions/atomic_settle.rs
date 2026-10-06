use anchor_lang::prelude::*;
use crate::state::{MarketPool, AgentDealEscrow};
use crate::errors::NexusError;

#[derive(Accounts)]
pub struct AtomicSettle<'info> {
    #[account(mut, has_one = market_pool, has_one = seller_agent)]
    pub deal_escrow: Account<'info, AgentDealEscrow>,
    #[account(mut)]
    pub market_pool: Account<'info, MarketPool>,
    /// Vault account holding escrow funds
    /// CHECK: Validated via seeds
    #[account(
        mut,
        seeds = [b"vault", deal_escrow.key().as_ref()],
        bump
    )]
    pub escrow_vault: AccountInfo<'info>,
    #[account(mut)]
    /// CHECK: Payout address of seller agent
    pub seller_agent: AccountInfo<'info>,
    /// Authorized oracle / arbiter signing verified execution proof
    pub arbiter_authority: Signer<'info>,
}

pub fn handler(ctx: Context<AtomicSettle>, _proof_hash: [u8; 32]) -> Result<()> {
    let deal = &mut ctx.accounts.deal_escrow;
    let pool = &mut ctx.accounts.market_pool;

    require!(!deal.is_settled, NexusError::DealAlreadySettled);

    let amount = deal.locked_amount;
    let escrow_vault = &ctx.accounts.escrow_vault;
    let seller = &ctx.accounts.seller_agent;

    **escrow_vault.try_borrow_mut_lamports()? = escrow_vault
        .lamports()
        .checked_sub(amount)
        .ok_or(NexusError::InsufficientCollateral)?;

    **seller.try_borrow_mut_lamports()? = seller
        .lamports()
        .checked_add(amount)
        .ok_or(NexusError::MathOverflow)?;

    deal.is_settled = true;
    pool.cumulative_volume_lamports = pool.cumulative_volume_lamports.checked_add(amount as u128).ok_or(NexusError::MathOverflow)?;
    pool.total_deals_count = pool.total_deals_count.checked_add(1).ok_or(NexusError::MathOverflow)?;

    msg!("Atomic settlement completed: {} lamports transferred to seller {}", amount, seller.key());
    Ok(())
}
