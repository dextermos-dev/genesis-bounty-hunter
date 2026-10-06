export class BuyerAgent {
  public id: string;
  public maxBudgetSol: number;

  constructor(id: string, maxBudgetSol: number = 0.10) {
    this.id = id;
    this.maxBudgetSol = maxBudgetSol;
  }

  public evaluateBids(bids: Array<{ sellerId: string; priceSol: number }>): { sellerId: string; priceSol: number } | null {
    const validBids = bids.filter(b => b.priceSol <= this.maxBudgetSol);
    if (validBids.length === 0) return null;
    // Best value selection
    validBids.sort((a, b) => a.priceSol - b.priceSol);
    return validBids[0];
  }
}
