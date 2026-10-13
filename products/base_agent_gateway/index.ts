/**
 * Base L2 Agent Micropayment Gateway (TypeScript Client)
 * Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
 */

export interface RFCx402Quote {
  statusCode: 402;
  statusMessage: string;
  protocol: "RFC-x402";
  network: "Base L2 (ChainID: 8453)";
  taskId: string;
  costUsdc: number;
  tokenAddress: string;
  recipientWallet: string;
  expiresAt: number;
  quoteSignature: string;
}

export interface SettlementResult {
  success: boolean;
  channelId: string;
  taskId: string;
  payoutAmountUsdc: number;
  beneficiary: string;
  proofHash: string;
}

export const OFFICIAL_SETTLEMENT_WALLET = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20";
export const BASE_USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
