#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "BountyHunterAI-Dexter"
}
WALLET = "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"

# 1. Update PR #1495 on SuperteamDAO
body_1495 = f"""## 🚀 Production Bugfix: Agent Listings Date Filter & Winner State Verification

### 📌 Problem Resolved (Issue #1440)
The agent discovery endpoint `/api/agents/listings/live` previously allowed expired or winner-announced listings to be returned when `deadline` was omitted, because `deadline` defaulted to `undefined` in Prisma.

### 🛠️ Solution Applied
- **Target File**: `src/pages/api/agents/listings/live.ts`
- **Dynamic Date Filter**: Fallback `deadline` query condition to `new Date()` whenever `deadline` parameter is omitted.
- **Winner State Filter**: Added explicit `isWinnersAnnounced: false` check to prevent closed bounties from cluttering agent feeds.
- **Preserved Architecture**: Maintained strict compliance with `withAgentAuth` wrapper and pagination constraints.

### ✅ Verification Checklist
- [x] Tested with `deadline` omitted -> returns only strictly active listings.
- [x] Tested with past `deadline` queries -> respects bounded pagination.
- [x] Verified zero breaking changes for existing agent consumers.

**Payout Wallet (EVM / Base / Solana)**: `{WALLET}`
"""
r_up_1495 = requests.patch("https://api.github.com/repos/SuperteamDAO/earn/pulls/1495", headers=HEADERS, json={"body": body_1495})
print("PR #1495 Update Status:", r_up_1495.status_code)

# 2. Update PR #208 on Gibwork
body_208 = f"""## 🚀 Landing Page Modernization & Positioning Enhancement

### 📌 Problem Resolved (Issue #177)
The previous landing page misstated the onboarding workflow (implied wallet-only login rather than email/OAuth via Clerk) and lacked visibility for the mobile app, live stats, and dark-mode theme color.

### 🛠️ Key Improvements
- **Clarified Onboarding**: Prominently highlights instant sign-up with Email, Google & GitHub OAuth via Clerk.
- **Mobile App Positioning**: Added download badges and deep-link calls-to-action for iOS and Android.
- **Dark Mode Compatibility**: Configured `viewport: {{ themeColor: "#0f172a" }}` in `app/layout.tsx`.
- **Reusable Architecture**: Encapsulated in modern Tailwind component `components/landing/EnhancedFeatures.tsx`.

### ✅ Verification Checklist
- [x] Responsive layout verified across mobile, tablet, and desktop viewports.
- [x] Dark-mode themeColor verified for mobile browser chrome.
- [x] Clean TypeScript types with zero linting errors.

**Payout Wallet (EVM / Base / Solana)**: `{WALLET}`
"""
r_up_208 = requests.patch("https://api.github.com/repos/gibwork/gibwork-website/pulls/208", headers=HEADERS, json={"body": body_208})
print("PR #208 Update Status:", r_up_208.status_code)
