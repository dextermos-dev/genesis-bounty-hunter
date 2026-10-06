/**
 * Mermail Autonomous Treasury & Procurement Skill
 * Author: Dexter Mos (@dextermos)
 * License: MIT
 */

export interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: number;
  total: number;
}

export interface InvoiceAuditResult {
  messageId: string;
  vendorDomain: string;
  recipientWallet: string;
  totalDueUsdc: number;
  lineItems: InvoiceItem[];
  riskFlags: string[];
  isValid: boolean;
  status: "APPROVED_FOR_DRAFT" | "REQUIRES_CLARIFICATION" | "REJECTED_SECURITY_RISK";
}

export interface RFPMetric {
  title: string;
  issuerDomain: string;
  budgetUsdc: number;
  deadline: string;
  mandatoryRequirements: string[];
  missingEvidence: string[];
  recommendation: "BID" | "NO_BID" | "SEEK_CLARIFICATION";
  draftResponse: string;
}

export class MermailTreasurySkill {
  private allowedChains: string[];
  private maxSingleTxUsdc: number;

  constructor(config?: { allowedChains?: string[]; maxSingleTxUsdc?: number }) {
    this.allowedChains = config?.allowedChains || ["solana", "base", "ethereum"];
    this.maxSingleTxUsdc = config?.maxSingleTxUsdc || 10000;
  }

  /**
   * Sanitizes text to remove private keys, tokens, or credential leaks.
   */
  public sanitizeText(text: string): string {
    return text
      .replace(/(0x)?[0-9a-fA-F]{64}/g, "[REDACTED_PRIVATE_KEY_OR_SECRET]")
      .replace(/ghp_[A-Za-z0-9_]{36}/g, "[REDACTED_GITHUB_TOKEN]")
      .replace(/sk_live_[0-9a-zA-Z]+/g, "[REDACTED_API_KEY]");
  }

  /**
   * Audits incoming email invoice payload from Mermail MCP.
   */
  public auditInvoicePayload(rawMessage: {
    id: string;
    sender: string;
    subject: string;
    body: string;
    dkimValid?: boolean;
  }): InvoiceAuditResult {
    const riskFlags: string[] = [];
    const sanitizedBody = this.sanitizeText(rawMessage.body);

    if (rawMessage.dkimValid === false) {
      riskFlags.push("DKIM_FAILED_UNTRUSTED_SENDER");
    }

    // Extract wallet
    const solanaWalletMatch = sanitizedBody.match(/[1-9A-HJ-NP-Za-km-z]{32,44}/);
    const evmWalletMatch = sanitizedBody.match(/0x[a-fA-F0-9]{40}/);
    const recipientWallet = evmWalletMatch ? evmWalletMatch[0] : (solanaWalletMatch ? solanaWalletMatch[0] : "UNKNOWN");

    if (recipientWallet === "UNKNOWN") {
      riskFlags.push("NO_VALID_ONCHAIN_WALLET_DETECTED");
    }

    // Extract amount
    const amountMatch = sanitizedBody.match(/(\$|USDC\s*|USD\s*)([0-9]+(\.[0-9]{1,2})?)/i);
    const totalDueUsdc = amountMatch ? parseFloat(amountMatch[2]) : 0;

    if (totalDueUsdc <= 0) {
      riskFlags.push("ZERO_OR_INVALID_AMOUNT");
    }

    if (totalDueUsdc > this.maxSingleTxUsdc) {
      riskFlags.push(`EXCEEDS_SINGLE_TX_LIMIT_${this.maxSingleTxUsdc}_USDC`);
    }

    const domain = rawMessage.sender.split("@")[1] || "unknown.domain";

    const isValid = riskFlags.length === 0;
    const status = riskFlags.includes("DKIM_FAILED_UNTRUSTED_SENDER")
      ? "REJECTED_SECURITY_RISK"
      : (isValid ? "APPROVED_FOR_DRAFT" : "REQUIRES_CLARIFICATION");

    return {
      messageId: rawMessage.id,
      vendorDomain: domain,
      recipientWallet,
      totalDueUsdc,
      lineItems: [
        {
          description: rawMessage.subject,
          quantity: 1,
          unitPrice: totalDueUsdc,
          total: totalDueUsdc
        }
      ],
      riskFlags,
      isValid,
      status
    };
  }

  /**
   * Evaluates an RFP and produces a structured Decision Packet.
   */
  public evaluateRFP(rawMessage: {
    id: string;
    sender: string;
    subject: string;
    body: string;
  }): RFPMetric {
    const sanitized = this.sanitizeText(rawMessage.body);
    const domain = rawMessage.sender.split("@")[1] || "procurement.org";

    const mandatoryRequirements: string[] = [
      "SOC-2 / Security Self-Assessment",
      "On-Chain Escrow Payout Acceptance",
      "Verifiable GitHub Repository",
      "SLA Delivery within 14 Days"
    ];

    const missingEvidence: string[] = [];
    if (!sanitized.toLowerCase().includes("escrow") && !sanitized.toLowerCase().includes("usdc")) {
      missingEvidence.push("Explicit USDC / Non-Custodial Escrow Confirmation");
    }

    const recommendation: "BID" | "NO_BID" | "SEEK_CLARIFICATION" =
      missingEvidence.length > 0 ? "SEEK_CLARIFICATION" : "BID";

    const draftResponse = `Hello Procurement Team at ${domain},\n\nWe have reviewed RFP "${rawMessage.subject}". Our technical core meets all mandatory requirements.\n\nPlease clarify the payout terms via on-chain USDC settlement.\n\nBest regards,\nAutonomous Treasury Agent (@dextermos)`;

    return {
      title: rawMessage.subject,
      issuerDomain: domain,
      budgetUsdc: 2500,
      deadline: new Date(Date.now() + 14 * 86400000).toISOString(),
      mandatoryRequirements,
      missingEvidence,
      recommendation,
      draftResponse
    };
  }
}
