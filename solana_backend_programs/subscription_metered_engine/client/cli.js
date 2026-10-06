#!/usr/bin/env node
/**
 * Interactive Client & CLI for Solana Subscription & Metered Backend Program
 * Author: Dexter Mos (@dextermos / @dextermostard)
 */

console.log(`
======================================================================
⚡ SOLANA ON-CHAIN SUBSCRIPTION & METERED USAGE BACKEND CLI
======================================================================
Author: Dexter Mos (@dextermos)
Program ID: SubEng111111111111111111111111111111111111
Target Network: Solana Devnet / Localnet
======================================================================
Available Commands:
  1. init-tier         - Initialize a new service tier (pricing & rate limits)
  2. subscribe         - Subscribe to plan with prepaid escrow deposit
  3. record-usage      - Log metered API calls / compute usage
  4. settle-period     - Execute periodic settlement and payout transfer
  5. cancel-plan       - Cancel subscription and refund unused escrow balance
======================================================================
`);
