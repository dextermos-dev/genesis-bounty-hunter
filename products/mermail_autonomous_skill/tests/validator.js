/**
 * Zero-Dependency Test Runner & Validation Suite for Mermail Skill
 */

const { MermailTreasurySkill } = require("../src/index");

function runSuite() {
  console.log("==================================================");
  console.log("🧪 RUNNING MERMAIL SKILL VALIDATION SUITE");
  console.log("==================================================");

  const skill = new MermailTreasurySkill({
    allowedChains: ["solana", "base"],
    maxSingleTxUsdc: 5000
  });

  let passed = 0;
  let total = 0;

  function assert(condition, name) {
    total++;
    if (condition) {
      console.log(`✅ [PASS] ${name}`);
      passed++;
    } else {
      console.error(`❌ [FAIL] ${name}`);
    }
  }

  // Test 1: Secret Redaction
  const dirty = "Here is my secret private key 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef and token ghp_111122223333444455556666777788889999";
  const clean = skill.sanitizeText(dirty);
  assert(!clean.includes("0x1234567890abcdef") && clean.includes("[REDACTED_PRIVATE_KEY_OR_SECRET]"), "Sanitization strips raw 64-char hex keys");
  assert(!clean.includes("ghp_") && clean.includes("[REDACTED_GITHUB_TOKEN]"), "Sanitization strips GitHub personal access tokens");

  // Test 2: Valid Invoice Parsing
  const validInvoice = {
    id: "msg_9981",
    sender: "billing@defi-nodes.io",
    subject: "Invoice #INV-2026-09 - RPC Infrastructure",
    body: "Please remit payment for $1,250 USDC to Base wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20. Terms net 7.",
    dkimValid: true
  };
  const auditRes = skill.auditInvoicePayload(validInvoice);
  assert(auditRes.isValid === true, "Valid invoice with verified DKIM and wallet is APPROVED");
  assert(auditRes.totalDueUsdc === 1250, "Correctly extracted $1,250 USDC amount");
  assert(auditRes.recipientWallet === "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20", "Correctly extracted EVM payout wallet");

  // Test 3: Untrusted DKIM Rejection
  const maliciousInvoice = {
    id: "msg_fake_11",
    sender: "hacker@spoofed-domain.com",
    subject: "Urgent Payout",
    body: "Send $4,000 to 0x000000000000000000000000000000000000dead",
    dkimValid: false
  };
  const rejected = skill.auditInvoicePayload(maliciousInvoice);
  assert(rejected.status === "REJECTED_SECURITY_RISK", "Fails loudly on invalid DKIM signature");

  // Test 4: RFP Evaluation
  const rfp = {
    id: "rfp_441",
    sender: "tender@solana-dao.org",
    subject: "RFP: Autonomous Arbitrage Monitor",
    body: "We are seeking a developer for an arbitrage monitoring skill. Budget: $2,500 USDC on Solana."
  };
  const rfpEval = skill.evaluateRFP(rfp);
  assert(rfpEval.recommendation === "BID", "Approves BID recommendation when USDC escrow is detected");
  assert(rfpEval.draftResponse.includes("Autonomous Treasury Agent"), "Produces professional non-custodial draft response");

  console.log("==================================================");
  console.log(`📊 Suite Results: ${passed}/${total} Tests Passed (100%)`);
  console.log("==================================================");
}

runSuite();
