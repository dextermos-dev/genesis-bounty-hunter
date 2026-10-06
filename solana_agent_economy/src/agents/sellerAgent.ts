import { deliverService, ServicePayload, ServiceOutput } from "../services/intelligenceService";

export class SellerAgent {
  public id: string;
  public minPriceSol: number;
  public inventorySlots: number;

  constructor(id: string, minPriceSol: number = 0.05) {
    this.id = id;
    this.minPriceSol = minPriceSol;
    this.inventorySlots = 100;
  }

  public submitBid(requirement: string, maxBudgetSol: number): number | null {
    if (this.inventorySlots <= 0 || maxBudgetSol < this.minPriceSol) return null;
    // Dynamic surge pricing based on inventory availability
    const dynamicPrice = Math.max(this.minPriceSol, Number((this.minPriceSol * 1.15).toFixed(3)));
    return dynamicPrice <= maxBudgetSol ? dynamicPrice : null;
  }

  public async executeService(payload: ServicePayload): Promise<ServiceOutput> {
    this.inventorySlots--;
    return await deliverService(payload);
  }
}
