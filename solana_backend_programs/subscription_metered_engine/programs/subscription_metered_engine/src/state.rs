use anchor_lang::prelude::*;

#[account]
#[derive(Default)]
pub struct ServicePlanTier {
    /// Merchant or Provider authority
    pub authority: Pubkey,
    /// Identifier slug / seed for tier
    pub tier_id: [u8; 32],
    /// Base periodic cost in lamports / micro-USDC
    pub base_price: u64,
    /// Price per metered unit (e.g., API calls, compute credits)
    pub per_unit_price: u64,
    /// Interval duration in seconds (e.g., 2,592,000 for 30 days)
    pub billing_interval_seconds: i64,
    /// Maximum rate limit per interval (0 for unlimited)
    pub rate_limit_units: u64,
    /// Total active subscribers count
    pub active_subscribers_count: u64,
    /// Bump seed for PDA validation
    pub bump: u8,
}

impl ServicePlanTier {
    pub const LEN: usize = 8 + 32 + 32 + 8 + 8 + 8 + 8 + 8 + 1;
}

#[account]
#[derive(Default)]
pub struct UserSubscription {
    /// Subscriber public key
    pub subscriber: Pubkey,
    /// Associated service tier PDA
    pub tier: Pubkey,
    /// Escrow vault holding prepaid balance
    pub escrow_vault: Pubkey,
    /// Unix timestamp when the current billing cycle started
    pub current_period_start: i64,
    /// Unix timestamp when the current billing cycle expires
    pub current_period_end: i64,
    /// Cumulative metered units consumed in current period
    pub metered_units_consumed: u64,
    /// Total lifetime units consumed across all periods
    pub lifetime_units_consumed: u64,
    /// Prepaid balance deposited in lamports
    pub prepaid_escrow_balance: u64,
    /// Active state flag (true = active, false = cancelled)
    pub is_active: bool,
    /// Bump seed for subscription PDA
    pub bump: u8,
}

impl UserSubscription {
    pub const LEN: usize = 8 + 32 + 32 + 32 + 8 + 8 + 8 + 8 + 8 + 1 + 1;
}
