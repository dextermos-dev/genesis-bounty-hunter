use anchor_lang::prelude::*;

pub mod errors;
pub mod instructions;
pub mod state;

use instructions::*;

declare_id!("SubEng111111111111111111111111111111111111");

#[program]
pub mod subscription_metered_engine {
    use super::*;

    /// Initialize a new merchant/provider service tier with pricing and rate limits
    pub fn initialize_tier(
        ctx: Context<InitializeTier>,
        tier_id: [u8; 32],
        base_price: u64,
        per_unit_price: u64,
        billing_interval_seconds: i64,
        rate_limit_units: u64,
    ) -> Result<()> {
        instructions::initialize_tier::handler(
            ctx,
            tier_id,
            base_price,
            per_unit_price,
            billing_interval_seconds,
            rate_limit_units,
        )
    }

    /// User activates subscription by depositing initial escrow collateral
    pub fn create_subscription(
        ctx: Context<CreateSubscription>,
        initial_deposit: u64,
    ) -> Result<()> {
        instructions::create_subscription::handler(ctx, initial_deposit)
    }

    /// Provider/Gateway records verified metered API/compute usage
    pub fn record_metered_usage(
        ctx: Context<RecordMeteredUsage>,
        units_consumed: u64,
    ) -> Result<()> {
        instructions::record_metered_usage::handler(ctx, units_consumed)
    }

    /// Settle billing cycle and transfer earned fees to provider payout account
    pub fn settle_period(ctx: Context<SettlePeriod>) -> Result<()> {
        instructions::settle_period::handler(ctx)
    }

    /// Subscriber cancels active plan and refunds remaining unconsumed prepaid escrow
    pub fn cancel_subscription(ctx: Context<CancelSubscription>) -> Result<()> {
        instructions::cancel_subscription::handler(ctx)
    }
}
