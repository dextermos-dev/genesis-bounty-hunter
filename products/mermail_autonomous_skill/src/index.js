/**
 * Mermail Autonomous Treasury & Procurement Skill (CommonJS Runtime)
 * Author: Dexter Mos (@dextermos)
 * License: MIT
 */

class MermailTreasurySkill {
  constructor(config) {
    this.allowedChains = config?.allowedChains || ["solana", "base", "ethereum"];
    this.maxSingleTxUsdc = config?.maxSingleTxUsdc || 10000;
  }

  /**
   * Sanitizes text to remove private keys, tokens, or credential leaks.
   */
  sanitizeText(text) {
    if (!text) return "";
    return text
      .replace(/0x[0-9a-fA-F]{64}/g, "[REDACTED_PRIVATE_KEY_OR_SECRET]")
      .replace(/ghp_[A-Za-z0-9_]{36}/g, "[REDACTED_GITHUB_TOKEN]")
      .replace(/sk_live_[0-9a-zA-Z]+/g, "[REDACTED_API_KEY]");
  }

  /**
   * Audits incoming email invoice payload from Mermail MCP.
   */
  auditInvoicePayload(rawMessage) {
    const riskFlags = [];
    const sanitizedBody = this.sanitizeText(rawMessage.body || "");

    if (rawMessage.dkimValid === false) {
      riskFlags.push("DKIM_FAILED_UNTRUSTED_SENDER");
    }

    // Extract EVM wallet (0x + 40 hex chars) or Solana wallet (base58 32-44 chars)
    const evmWalletMatch = sanitizedBody.match(/\b0x[a-fA-F0-9]{40,42}\b/);
    const solanaWalletMatch = sanitizedBody.match(/\b[1-9A-HJ-NP-Za-km-z]{32,44}\b/);
    let recipientWallet = "UNKNOWN";

    if (evmWalletMatch) {
      recipientWallet = evmWalletMatch[0];
    } else if (solanaWalletMatch) {
      recipientWallet = solanaWalletMatch[0];
    }

    if (recipientWallet === "UNKNOWN") {
      riskFlags.push("NO_VALID_ONCHAIN_WALLET_DETECTED");
    }

    // Extract amount
    const amountMatch = sanitizedBody.match(/(\$|USDC\s*|USD\s*)([0-9,]+(\.[0-9]{1,2})?)/i);
    let totalDueUsdc = 0;
    if (amountMatch) {
      totalDueUsdc = parseFloat(amountMatch[2].replace(/,/g, ""));
    }

    if (totalDueUsdc <= 0) {
      riskFlags.push("ZERO_OR_INVALID_AMOUNT");
    }

    if (totalDueUsdc > this.maxSingleTxUsdc) {
      riskFlags.push(`EXCEEDS_SINGLE_TX_LIMIT_${this.maxSingleTxUsdc}_USDC`);
    }

    const domain = (rawMessage.sender || "").split("@")[1] || "unknown.domain";
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
          description: rawMessage.subject || "Invoice item",
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
  evaluateRFP(rawMessage) {
    const sanitized = this.sanitizeText(rawMessage.body || "");
    const domain = (rawMessage.sender || "").split("@")[1] || "procurement.org";

    const mandatoryRequirements = [
      "SOC-2 / Security Self-Assessment",
      "On-Chain Escrow Payout Acceptance",
      "Verifiable GitHub Repository",
      "SLA Delivery within 14 Days"
    ];

    const missingEvidence = [];
    if (!sanitized.toLowerCase().includes("escrow") && !sanitized.toLowerCase().includes("usdc")) {
      missingEvidence.push("Explicit USDC / Non-Custodial Escrow Confirmation");
    }

    const recommendation = missingEvidence.length > 0 ? "SEEK_CLARIFICATION" : "BID";

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

module.exports = { MermailTreasurySkill };
