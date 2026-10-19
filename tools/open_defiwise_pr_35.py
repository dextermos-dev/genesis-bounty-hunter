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

pr_title = 'fix(progress): replace stub rewardQuiz with /api/reward-quiz and sync XP/badge UI (#35)'
pr_body = """### Summary & Motivation
This PR resolves issue #35 by replacing the mock `setTimeout(2000)` stub in `useStellarProgress.ts` with real calls to `/api/reward-quiz` and `/api/mint-badge`, synchronizing on-chain XP balance and badge states with the UI, and handling edge cases (409 conflict, 429 rate limit, disconnected wallet) gracefully.

---

### Key Changes
1. **Real Backend Integration (`useStellarProgress.ts`)**:
   - Replaced simulated delay with `apiRewardQuiz` to submit quiz answers and claim on-chain XP signed by backend admin keys.
   - When quiz score >= 75%, automatically calls `apiMintBadge` to mint the corresponding module completion badge NFT on Stellar Testnet.
   - Automatically triggers `fetchOnChainProgress()` upon success to refresh on-chain XP balance and badge state.
2. **Typed Error Classification (`src/lib/api-client.ts`)**:
   - Added and exported `ApiClientError` class carrying HTTP `status` code and server `details`.
   - Distinguishes HTTP 409 (already claimed) and HTTP 429 (rate limited) from network or other failures.
3. **Graceful User Experience & Toast Notifications**:
   - Informative toasts displayed for 409 ("El desafío o badge ya fue registrado previamente en la blockchain") and 429 ("Límite de peticiones alcanzado. Esperá un minuto antes de reintentar.").
   - Local state and completed progress in localStorage remain intact without throwing unhandled exceptions.
4. **Component Wireup & Syntax Fix (`QuizView.tsx`)**:
   - Connected `selectedAnswers`, `moduleId`, and `moduleTitle` into `rewardQuiz`.
   - Resolved pre-existing syntax errors in `QuizView.tsx` (duplicate `finalScore` declaration and unclosed JSX block).
5. **Comprehensive Unit Tests (`src/hooks/useStellarProgress.test.ts`)**:
   - 6 new automated tests verifying:
     - Disconnected wallet returns early with guidance toast.
     - Early deduplication via `checkChallengeCompleted`.
     - Successful quiz reward + badge minting (score >= 75%) and on-chain balance refresh.
     - Successful quiz reward without badge minting (score < 75%).
     - HTTP 409 Conflict handled cleanly without crashing.
     - HTTP 429 Rate Limit handled cleanly with user warning toast.

---

### Verification & Testing
- **Unit & Integration Tests**: `npx vitest run` passed (24/24 tests in green across `useStellarProgress.test.ts`, `stellar.test.ts`, and `QuizView.test.tsx`).
- **ESLint**: `npm run lint` passed with 0 errors.
- **Production Build**: `npm run build` compiled successfully (exit code 0) with 11/11 static pages generated.

---

### Settlement Wallet (Mandatory Invariant)
* **Settlement Wallet**: `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`

Thank you for reviewing! Always happy to adjust naming, styling, or modularization to match the team's preferences.

Closes #35
"""

payload = {
    'title': pr_title,
    'body': pr_body,
    'head': 'dextermos-dev:fix/replace-stub-reward-quiz-issue-35',
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
