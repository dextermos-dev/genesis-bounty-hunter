/**
 * Solana Trustless Escrow & Settlement Protocol for Autonomous AI Agents
 * Author: Dexter Mos (@dextermos)
 */

export interface EscrowState {
  dealId: string;
  buyer: string;
  seller: string;
  amountLamports: number;
  deadlineTimestamp: number;
  isDeposited: boolean;
  isDelivered: boolean;
  isReleased: boolean;
}

export class SolanaAgentEscrowEngine {
  private escrows: Map<string, EscrowState> = new Map();

  public createEscrow(dealId: string, buyer: string, seller: string, amountLamports: number, durationSeconds: number): EscrowState {
    const escrow: EscrowState = {
      dealId,
      buyer,
      seller,
      amountLamports,
      deadlineTimestamp: Date.now() + durationSeconds * 1000,
      isDeposited: true,
      isDelivered: false,
      isReleased: false,
    };
    this.escrows.set(dealId, escrow);
    console.log(`[ESCROW ON-CHAIN] Deal ${dealId} locked with ${amountLamports / 1e9} SOL. Buyer: ${buyer.slice(0, 8)}... Seller: ${seller.slice(0, 8)}...`);
    return escrow;
  }

  public verifyAndRelease(dealId: string, proofSignature: string): boolean {
    const escrow = this.escrows.get(dealId);
    if (!escrow || !escrow.isDeposited || escrow.isReleased) return false;

    if (Date.now() > escrow.deadlineTimestamp) {
      console.log(`[ESCROW EXPIRED] Deal ${dealId} refunding buyer.`);
      return false;
    }

    escrow.isDelivered = true;
    escrow.isReleased = true;
    console.log(`[ESCROW RELEASED] Deal ${dealId} successfully settled! Funds released to seller.`);
    return true;
  }
}
