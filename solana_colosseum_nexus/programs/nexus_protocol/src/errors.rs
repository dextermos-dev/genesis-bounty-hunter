use anchor_lang::prelude::*;

#[error_code]
pub enum NexusError {
    #[msg("Settlement deadline has passed")]
    SettlementExpired,
    #[msg("Unauthorized agent signer or invalid authority")]
    UnauthorizedSigner,
    #[msg("Insufficient liquidity collateral locked in escrow vault")]
    InsufficientCollateral,
    #[msg("Mathematical calculation overflow")]
    MathOverflow,
    #[msg("Deal is already finalized and settled")]
    DealAlreadySettled,
    #[msg("Cryptographic verification proof signature mismatch")]
    InvalidProofSignature,
}
