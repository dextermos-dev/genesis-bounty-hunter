use anchor_lang::prelude::*;
use crate::state::{ServicePlanTier, UserSubscription};
use crate::errors::SubscriptionError;

#[derive(Accounts)]
pub struct CancelSubscription<'info> {
    #[account(mut, has_one = subscriber, has_one = tier)]
    pub subscription: Account<'info, UserSubscription>,
    #[account(mut)]
    pub tier: Account<'info, ServicePlanTier>,
    /// Escrow account returning unused prepaid deposit
    /// CHECK: Validated via seeds
    #[account(
        mut,
        seeds = [b"escrow", subscription.key().as_ref()],
        bump
    )]
    pub escrow_vault: AccountInfo<'info>,
    #[account(mut)]
    pub subscriber: Signer<'info>,
}

pub fn handler(ctx: Context<CancelSubscription>) -> Result<()> {
    let subscription = &mut ctx.accounts.subscription;
    let tier = &mut ctx.accounts.tier;

    require!(subscription.is_active, SubscriptionError::SubscriptionInactive);

    // Refund remaining unmetered prepaid escrow to subscriber
    let remaining_refund = subscription.prepaid_escrow_balance;
    if remaining_refund > 0 {
        let escrow_info = &ctx.accounts.escrow_vault;
        let subscriber_info = &ctx.accounts.subscriber.to_account_info();

        **escrow_info.try_borrow_mut_lamports()? = escrow_info
            .lamports()
            .checked_sub(remaining_refund)
            .ok_or(SubscriptionError::InsufficientEscrowBalance)?;

        **subscriber_info.try_borrow_mut_lamports()? = subscriber_info
            .lamports()
            .checked_add(remaining_refund)
            .ok_or(SubscriptionError::MathOverflow)?;
        
        subscription.prepaid_escrow_balance = 0;
    }

    subscription.is_active = false;
    tier.active_subscribers_count = tier.active_subscribers_count.saturating_sub(1);

    msg!("Subscription cancelled. Refunded {} lamports to subscriber.", remaining_refund);
    Ok(())
}
