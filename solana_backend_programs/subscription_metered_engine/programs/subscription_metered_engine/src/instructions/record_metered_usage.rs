use anchor_lang::prelude::*;
use crate::state::{ServicePlanTier, UserSubscription};
use crate::errors::SubscriptionError;

#[derive(Accounts)]
pub struct RecordMeteredUsage<'info> {
    #[account(mut, has_one = tier)]
    pub subscription: Account<'info, UserSubscription>,
    #[account(has_one = authority)]
    pub tier: Account<'info, ServicePlanTier>,
    /// Provider/Gateway Oracle signing the verified usage proof
    pub authority: Signer<'info>,
}

pub fn handler(ctx: Context<RecordMeteredUsage>, units_consumed: u64) -> Result<()> {
    let clock = Clock::get()?;
    let current_time = clock.unix_timestamp;
    let subscription = &mut ctx.accounts.subscription;
    let tier = &ctx.accounts.tier;

    require!(subscription.is_active, SubscriptionError::SubscriptionInactive);

    // If period elapsed, current cycle usage must be settled before new cycle metering
    if current_time > subscription.current_period_end {
        msg!("Warning: Period elapsed. Please settle billing cycle.");
    }

    let new_consumed = subscription.metered_units_consumed.checked_add(units_consumed).ok_or(SubscriptionError::MathOverflow)?;

    // Check rate limit if configured (> 0)
    if tier.rate_limit_units > 0 {
        require!(new_consumed <= tier.rate_limit_units, SubscriptionError::RateLimitExceeded);
    }

    subscription.metered_units_consumed = new_consumed;
    subscription.lifetime_units_consumed = subscription.lifetime_units_consumed.checked_add(units_consumed).ok_or(SubscriptionError::MathOverflow)?;

    msg!("Metered usage recorded: +{} units. Total period usage: {} units", units_consumed, subscription.metered_units_consumed);
    Ok(())
}
