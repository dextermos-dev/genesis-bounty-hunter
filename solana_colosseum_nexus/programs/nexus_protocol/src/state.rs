use anchor_lang::prelude::*;

#[account]
#[derive(Default)]
pub struct MarketPool {
    /// Market authority / creator
    pub authority: Pubkey,
    /// Unique pool identifier seed
    pub pool_id: [u8; 32],
    /// Base protocol fee in basis points (e.g., 25 = 0.25%)
    pub protocol_fee_bps: u16,
    /// Total cumulative settlement volume in lamports
    pub cumulative_volume_lamports: u128,
    /// Total active micro-deals processed
    pub total_deals_count: u64,
    /// Pool bump seed for PDA validation
    pub bump: u8,
}

impl MarketPool {
    pub const LEN: usize = 8 + 32 + 32 + 2 + 16 + 8 + 1;
}

#[account]
#[derive(Default)]
pub struct AgentDealEscrow {
    /// Buyer / Task Creator Agent
    pub buyer_agent: Pubkey,
    /// Seller / Service Provider Agent
    pub seller_agent: Pubkey,
    /// Associated Market Pool PDA
    pub market_pool: Pubkey,
    /// Locked escrow collateral in lamports
    pub locked_amount: u64,
    /// Deadline timestamp in Unix seconds
    pub deadline: i64,
    /// Settlement state flag (true = settled, false = pending)
    pub is_settled: bool,
    /// Bump seed for Escrow PDA
    pub bump: u8,
}

impl AgentDealEscrow {
    pub const LEN: usize = 8 + 32 + 32 + 32 + 8 + 8 + 1 + 1;
}
