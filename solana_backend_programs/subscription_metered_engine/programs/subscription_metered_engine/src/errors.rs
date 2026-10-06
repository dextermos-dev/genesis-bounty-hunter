use anchor_lang::prelude::*;

#[error_code]
pub enum SubscriptionError {
    #[msg("Subscription period has not ended yet for regular settlement")]
    PeriodNotElapsed,
    #[msg("Subscription is already cancelled or deactivated")]
    SubscriptionInactive,
    #[msg("Rate limit exceeded for current epoch window")]
    RateLimitExceeded,
    #[msg("Insufficient prepaid credit balance in escrow")]
    InsufficientEscrowBalance,
    #[msg("Invalid authority or signer provided")]
    UnauthorizedSigner,
    #[msg("Calculation overflow occurred during meter settlement")]
    MathOverflow,
    #[msg("Plan price or metering rate cannot be zero")]
    InvalidPlanParameters,
}
