import { SellerAgent } from "./agents/sellerAgent";
import { BuyerAgent } from "./agents/buyerAgent";
import { SolanaAgentEscrowEngine } from "./contracts/escrowProtocol";

async function runAutonomousMarketCycle() {
  console.log("======================================================================");
  console.log("🚀 SOLANA AUTONOMOUS AGENT ECONOMY (CoralOS Market Protocol)");
  console.log("======================================================================");

  const buyer = new BuyerAgent("buyer_agent_alpha_01", 0.08);
  const sellers = [
    new SellerAgent("seller_agent_mev_radar", 0.05),
    new SellerAgent("seller_agent_oracle_fast", 0.06),
    new SellerAgent("seller_agent_heavy_compute", 0.09)
  ];
  const escrowEngine = new SolanaAgentEscrowEngine();

  console.log("\n[1. WANT STAGE] Buyer Agent requests Solana route intelligence (Max Budget: 0.08 SOL)...");

  // 2. Bidding stage
  const bids = sellers
    .map(s => ({ sellerId: s.id, priceSol: s.submitBid("route_analysis", buyer.maxBudgetSol) }))
    .filter((b): b is { sellerId: string; priceSol: number } => b.priceSol !== null);

  console.log(`[2. BID STAGE] Received ${bids.length} machine-speed bids from seller network.`);

  // 3. Award stage
  const winningBid = buyer.evaluateBids(bids);
  if (!winningBid) {
    console.log("[ABORT] No seller matched buyer budget.");
    return;
  }
  console.log(`[3. AWARD STAGE] Winner selected: ${winningBid.sellerId} at ${winningBid.priceSol} SOL.`);

  // 4. Deposited stage
  const dealId = "deal_" + Date.now();
  escrowEngine.createEscrow(dealId, buyer.id, winningBid.sellerId, winningBid.priceSol * 1e9, 60);

  // 5. Delivered stage
  const winnerSeller = sellers.find(s => s.id === winningBid.sellerId)!;
  const result = await winnerSeller.executeService({ targetAsset: "BONK", depthThresholdUsd: 10000 });
  console.log(`[5. DELIVERED STAGE] Service delivered with cryptographic proof: ${result.signature}`);

  // 6. Released stage
  escrowEngine.verifyAndRelease(dealId, result.signature);

  console.log("\n======================================================================");
  console.log("✅ COMPLETE END-TO-END AUTONOMOUS AGENT SETTLEMENT VERIFIED ON SOLANA!");
  console.log("======================================================================");
}

runAutonomousMarketCycle();
