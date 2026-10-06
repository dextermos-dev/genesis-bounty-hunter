use anchor_lang::prelude::*;
use anchor_lang::system_program::{transfer, Transfer};
use crate::state::{MarketPool, AgentDealEscrow};
use crate::errors::NexusError;

#[derive(Accounts)]
#[instruction(deal_id: [u8; 32])]
pub struct DepositLiquidity<'info> {
    #[account(
        init,
        payer = buyer_agent,
        space = AgentDealEscrow::LEN,
        seeds = [b"agent_deal", market_pool.key().as_ref(), deal_id.as_ref()],
        bump
    )]
    pub deal_escrow: Account<'info, AgentDealEscrow>,
    #[account(mut)]
    pub market_pool: Account<'info, MarketPool>,
    /// Vault account holding deal escrow funds
    /// CHECK: Validated via seeds
    #[account(
        mut,
        seeds = [b"vault", deal_escrow.key().as_ref()],
        bump
    )]
    pub escrow_vault: AccountInfo<'info>,
    #[account(mut)]
    pub buyer_agent: Signer<'info>,
    /// CHECK: Public key of winning seller agent
    pub seller_agent: AccountInfo<'info>,
    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<DepositLiquidity>, _deal_id: [u8; 32], amount: u64, duration_seconds: i64) -> Result<()> {
    require!(amount > 0, NexusError::InsufficientCollateral);
    let clock = Clock::get()?;

    let cpi_ctx = CpiContext::new(
        ctx.accounts.system_program.to_account_info(),
        Transfer {
            from: ctx.accounts.buyer_agent.to_account_info(),
            to: ctx.accounts.escrow_vault.to_account_info(),
        },
    );
    transfer(cpi_ctx, amount)?;

    let deal = &mut ctx.accounts.deal_escrow;
    deal.buyer_agent = ctx.accounts.buyer_agent.key();
    deal.seller_agent = ctx.accounts.seller_agent.key();
    deal.market_pool = ctx.accounts.market_pool.key();
    deal.locked_amount = amount;
    deal.deadline = clock.unix_timestamp.checked_add(duration_seconds).ok_or(NexusError::MathOverflow)?;
    deal.is_settled = false;
    deal.bump = ctx.bumps.deal_escrow;

    msg!("Deal escrow provisioned: {} lamports locked for seller {}", amount, deal.seller_agent);
    Ok(())
}
