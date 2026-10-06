use anchor_lang::prelude::*;
use crate::state::{ServicePlanTier, UserSubscription};
use crate::errors::SubscriptionError;

#[derive(Accounts)]
pub struct SettlePeriod<'info> {
    #[account(mut, has_one = tier, has_one = subscriber)]
    pub subscription: Account<'info, UserSubscription>,
    #[account(mut, has_one = authority)]
    pub tier: Account<'info, ServicePlanTier>,
    /// Escrow account storing prepaid funds
    /// CHECK: Validated via seeds
    #[account(
        mut,
        seeds = [b"escrow", subscription.key().as_ref()],
        bump
    )]
    pub escrow_vault: AccountInfo<'info>,
    /// Provider authority receiving revenue settlement
    #[account(mut)]
    /// CHECK: Validated against tier.authority
    pub provider_payout_account: AccountInfo<'info>,
    pub authority: Signer<'info>,
    pub subscriber: AccountInfo<'info>,
}

pub fn handler(ctx: Context<SettlePeriod>) -> Result<()> {
    let clock = Clock::get()?;
    let current_time = clock.unix_timestamp;
    let subscription = &mut ctx.accounts.subscription;
    let tier = &ctx.accounts.tier;

    require!(subscription.is_active, SubscriptionError::SubscriptionInactive);

    // Calculate billing cost = base_price + (metered_units * per_unit_price)
    let metered_cost = (subscription.metered_units_consumed as u128)
        .checked_mul(tier.per_unit_price as u128)
        .ok_or(SubscriptionError::MathOverflow)?;
    
    let total_cost = (tier.base_price as u128)
        .checked_add(metered_cost)
        .ok_or(SubscriptionError::MathOverflow)? as u64;

    require!(subscription.prepaid_escrow_balance >= total_cost, SubscriptionError::InsufficientEscrowBalance);

    // Transfer settlement from Escrow Vault PDA to Provider Payout
    let escrow_vault_info = &ctx.accounts.escrow_vault;
    let provider_info = &ctx.accounts.provider_payout_account;

    **escrow_vault_info.try_borrow_mut_lamports()? = escrow_vault_info
        .lamports()
        .checked_sub(total_cost)
        .ok_or(SubscriptionError::InsufficientEscrowBalance)?;

    **provider_info.try_borrow_mut_lamports()? = provider_info
        .lamports()
        .checked_add(total_cost)
        .ok_or(SubscriptionError::MathOverflow)?;

    subscription.prepaid_escrow_balance = subscription.prepaid_escrow_balance.checked_sub(total_cost).ok_or(SubscriptionError::MathOverflow)?;
    
    // Advance billing cycle window
    subscription.current_period_start = current_time;
    subscription.current_period_end = current_time.checked_add(tier.billing_interval_seconds).ok_or(SubscriptionError::MathOverflow)?;
    subscription.metered_units_consumed = 0;

    msg!("Billing cycle settled: {} lamports transferred to provider. Next cycle ends at {}", total_cost, subscription.current_period_end);
    Ok(())
}
