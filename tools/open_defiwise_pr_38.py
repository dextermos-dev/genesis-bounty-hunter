import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

pr_title = 'feat: unlock advanced modules using on-chain XP historical_balance (#38)'
pr_body = """### Summary & Motivation
This PR resolves issue #38 by introducing on-chain XP requirement gating for advanced modules using the Soroban XP contract's `meets_requirement` and `historical_balance`.

Previously, module unlocking in `Dashboard` and `ModuleCard` relied solely on `useProgress.isModuleUnlocked` (local progression in `localStorage`). Advanced modules now declare on-chain minimum XP thresholds (`minXp`), querying user historical XP when a wallet is connected and presenting clear, actionable feedback when a wallet is disconnected or balance is insufficient without falsely unlocking content.

---

### Key Changes
1. **Module Data Schema & Course Declarations (`src/data/courses.ts`)**:
   - Added optional `minXp?: number` field to the `Module` interface.
   - Declared on-chain gating thresholds on advanced modules:
     - `mod-2` (\"Smart Contracts\"): `minXp: 50` (completing module 1 grants 50 XP).
     - `mod-3` (\"El Valor del Dinero en el Tiempo y la Inflación\"): `minXp: 100`.
2. **On-Chain Query & Argument Builders (`src/lib/stellar.ts`)**:
   - Added `buildMeetsRequirementArgs(userPublicKey, minXp)` helper returning strongly-typed Soroban `ScVal` arguments (`Address` and `i128`).
   - Implemented `meetsXPRequirement(userPublicKey, minXp)` to query Soroban `meets_requirement` read-only method.
3. **Hook Integration (`src/hooks/useStellarProgress.ts`)**:
   - Exposed `checkMeetsRequirement(minXp)` callback inside `useStellarProgress`, checking on-chain contract and falling back to cached `historicalXP`.
4. **UI Wireup & Informative Lock States (`Dashboard` & `ModuleCard`)**:
   - Wired `stellarProgress.connected` and `stellarProgress.historicalXP` in `src/app/dashboard/page.tsx`.
   - Updated `ModuleCard.tsx` to handle `lockedReason`:
     - Disconnected wallet: *\"Conectá tu wallet para verificar tu XP on-chain (requiere X XP)\"*.
     - Insufficient XP: *\"Requiere X XP históricos on-chain (actual: Y XP)\"*.
     - Prerequisite module: *\"Completá el módulo anterior para desbloquear\"*.
     - Displays badge with XP requirement chip on locked card.

---

### Invariant Guarantee (§ Technical Context)
* **Historical Balance Invariant**: Gating strictly evaluates against `historical_balance` (the append-only ledger accumulator in Soroban that never decreases), **never** liquid `balance`.
* Spending, burning, or transferring XP tokens cannot revoke earned course progress or re-lock completed/accessible modules.

---

### Verification & Testing
- **Rust Contract Tests**: `cargo test --package defiwise-xp-token` passed (4/4 tests including `test_meets_requirement` and `test_historical_never_decreases`).
- **Unit Tests**: `npx vitest run` passed (28/28 tests across `stellar.test.ts`, `ModuleCard.test.tsx`, and `QuizView.test.tsx`).
- **ESLint**: `npm run lint` passed with 0 errors.
- **Production Build**: `npm run build` compiled successfully (exit code 0) with 11/11 static pages generated.

---

### Settlement Wallet (Mandatory Invariant)
* **Settlement Wallet**: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`

Thank you for reviewing! Always happy to adapt any styling, thresholds, or copy to match the team's roadmap.

Closes #38
"""

payload = {
    'title': pr_title,
    'body': pr_body,
    'head': 'dextermos-dev:feat/unlock-modules-onchain-historical-xp-issue-38',
    'base': 'main'
}

req = urllib.request.Request(
    'https://api.github.com/repos/BuenDia-Builders/defiwise-stellar/pulls',
    data=json.dumps(payload).encode('utf-8'),
    headers=headers
)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('PR successfully created!')
        print('PR Number:', data.get('number'))
        print('PR URL:', data.get('html_url'))
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code)
    print(e.read().decode('utf-8'))
except Exception as e:
    print('Error:', e)
