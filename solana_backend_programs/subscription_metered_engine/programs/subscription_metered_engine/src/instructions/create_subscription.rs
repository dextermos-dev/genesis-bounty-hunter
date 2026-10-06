use anchor_lang::prelude::*;
use anchor_lang::system_program::{transfer, Transfer};
use crate::state::{ServicePlanTier, UserSubscription};
use crate::errors::SubscriptionError;

#[derive(Accounts)]
pub struct CreateSubscription<'info> {
    #[account(
        init,
        payer = subscriber,
        space = UserSubscription::LEN,
        seeds = [b"subscription", tier.key().as_ref(), subscriber.key().as_ref()],
        bump
    )]
    pub subscription: Account<'info, UserSubscription>,
    #[account(mut)]
    pub tier: Account<'info, ServicePlanTier>,
    /// Escrow account storing prepaid funds for metered executions
    /// CHECK: Validated via PDA seeds
    #[account(
        mut,
        seeds = [b"escrow", subscription.key().as_ref()],
        bump
    )]
    pub escrow_vault: AccountInfo<'info>,
    #[account(mut)]
    pub subscriber: Signer<'info>,
    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<CreateSubscription>, initial_deposit: u64) -> Result<()> {
    let clock = Clock::get()?;
    let current_time = clock.unix_timestamp;
    let tier = &mut ctx.accounts.tier;

    require!(initial_deposit >= tier.base_price, SubscriptionError::InsufficientEscrowBalance);

    // Deposit funds into on-chain escrow
    let cpi_context = CpiContext::new(
        ctx.accounts.system_program.to_account_info(),
        Transfer {
            from: ctx.accounts.subscriber.to_account_info(),
            to: ctx.accounts.escrow_vault.to_account_info(),
        },
    );
    transfer(cpi_context, initial_deposit)?;

    let subscription = &mut ctx.accounts.subscription;
    subscription.subscriber = ctx.accounts.subscriber.key();
    subscription.tier = tier.key();
    subscription.escrow_vault = ctx.accounts.escrow_vault.key();
    subscription.current_period_start = current_time;
    subscription.current_period_end = current_time.checked_add(tier.billing_interval_seconds).ok_or(SubscriptionError::MathOverflow)?;
    subscription.metered_units_consumed = 0;
    subscription.lifetime_units_consumed = 0;
    subscription.prepaid_escrow_balance = initial_deposit;
    subscription.is_active = true;
    subscription.bump = ctx.bumps.subscription;

    tier.active_subscribers_count = tier.active_subscribers_count.checked_add(1).ok_or(SubscriptionError::MathOverflow)?;

    msg!("Subscription activated for subscriber {} with {} lamports deposit", subscription.subscriber, initial_deposit);
    Ok(())
}
