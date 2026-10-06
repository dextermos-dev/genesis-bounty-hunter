use anchor_lang::prelude::*;
use crate::state::ServicePlanTier;
use crate::errors::SubscriptionError;

#[derive(Accounts)]
#[instruction(tier_id: [u8; 32])]
pub struct InitializeTier<'info> {
    #[account(
        init,
        payer = authority,
        space = ServicePlanTier::LEN,
        seeds = [b"service_tier", authority.key().as_ref(), tier_id.as_ref()],
        bump
    )]
    pub tier: Account<'info, ServicePlanTier>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

pub fn handler(
    ctx: Context<InitializeTier>,
    tier_id: [u8; 32],
    base_price: u64,
    per_unit_price: u64,
    billing_interval_seconds: i64,
    rate_limit_units: u64,
) -> Result<()> {
    require!(billing_interval_seconds > 0, SubscriptionError::InvalidPlanParameters);

    let tier = &mut ctx.accounts.tier;
    tier.authority = ctx.accounts.authority.key();
    tier.tier_id = tier_id;
    tier.base_price = base_price;
    tier.per_unit_price = per_unit_price;
    tier.billing_interval_seconds = billing_interval_seconds;
    tier.rate_limit_units = rate_limit_units;
    tier.active_subscribers_count = 0;
    tier.bump = ctx.bumps.tier;

    msg!("Service tier initialized: base_price={}, interval={}s", base_price, billing_interval_seconds);
    Ok(())
}
