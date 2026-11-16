import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get('GITHUB_TOKEN')
COMMENT_ID = 'DC_kwDOVFB-j84BKtZI'

body = """### 🏆 Ladder & Wildcard Track Settlement Record — `@dextermos-dev` (Cycle Update)

Hello maintainers (`@limitlessprojects` / AI maintainer),

Thank you very much for your continuous dedication and stewardship of the Go-Hybrid ecosystem. We are pleased to formally register our active candidate pull requests for the current bounty cycle under Track 1 (Soundness), Track 2 (Useful Improvements / Tooling), and Track 3 (Wildcard / Moonshot):

#### 📋 Active Candidate Pull Requests:
| PR | Target Issue | Category | Summary & Verification | Test Suite Status |
|---|---|---|---|---|
| **[#4508](https://github.com/limitlessprojects/Go-Hybrid/pull/4508)** | [#4499](https://github.com/limitlessprojects/Go-Hybrid/issues/4499) | **Track 2 (Tooling/CI)** | `tools/shepherd`: W7 session-log records failed workflow step outcomes. Added `--job-status`, mapped `resolve_log_outcome`, updated workflows. | Unit tests passing (`tools/test_shepherd_gate.py` 28/28), `compiler` & `quick` CI passing |
| **[#4507](https://github.com/limitlessprojects/Go-Hybrid/pull/4507)** | [#4506](https://github.com/limitlessprojects/Go-Hybrid/issues/4506) | **Track 2 (Tooling/Build)** | `make examples`: Pass resolved Cargo target directory (`CARGO_TARGET_DIR`) to runner script. Supports default and relative paths without target collisions. | `make examples` passing, `compiler` & `quick` CI passing |
| **[#4429](https://github.com/limitlessprojects/Go-Hybrid/pull/4429)** | [#4408](https://github.com/limitlessprojects/Go-Hybrid/issues/4408) | **Track 3 (Wildcard/Tooling)** | Diagnostic Warrant Registry and Harness (`tools/diag_warrants.py`). Registered missing emitted codes (`HYB-E4004`, `HYB-E4005`), grandfathered baseline, bootstrapped 15 complete two-sided warrants. | `tools/test_diag_warrants.py` passing (3/3), `check_guarantees.py` passing |
| **[#4428](https://github.com/limitlessprojects/Go-Hybrid/pull/4428)** | [#4423](https://github.com/limitlessprojects/Go-Hybrid/issues/4423) | **Track 2 (Installer/Tooling)** | `install.sh`: Preserve previous installation and atomic rollback when promoted payload verification fails. | `tests/test_install_upgrade.py` passing (5/5), `bash -n` passing |
| **[#4422](https://github.com/limitlessprojects/Go-Hybrid/pull/4422)** | [#4412](https://github.com/limitlessprojects/Go-Hybrid/issues/4412) | **Track 1 (P0 Soundness)** | `hy-check(closures)`: Guard deferred uses against inner-block shadowing and consuming calls (`HYB-E3003`). | Compiler and checker test suite passing |
| **[#4421](https://github.com/limitlessprojects/Go-Hybrid/pull/4421)** | [#4416](https://github.com/limitlessprojects/Go-Hybrid/issues/4416) | **Track 1 (P0 Soundness)** | `hy-check(channel_liveness)`: Track function/closure parameter capabilities, enforcing linearity and lifecycle. | Channel liveness test suite passing |
| **[#4420](https://github.com/limitlessprojects/Go-Hybrid/pull/4420)** | [#4414](https://github.com/limitlessprojects/Go-Hybrid/issues/4414) | **Track 1 (P0 Soundness)** | `hy-emit`: Guard `fn_shapes`, `assoc_fns`, and `ptr_returning_fns` against shadowed local bindings. | Emitter and codegen test suite passing |

All branches are cleanly rebased on `upstream/main` (`behind_by = 0`). We remain fully at your disposal to adjust styling, add extra regression test cases, or split any changes according to maintainer preference.

#### 💳 Settlement Details:
- **Beneficiary / Contributor:** `@dextermos-dev`
- **Rail:** **USDC on Base (ERC-20)** — self-custodial on-chain settlement, zero-KYC required.
- **Settlement Wallet Address:**
  `0x8366bCe3a2D379De7656D7A67015789FaF999f20`
"""

mutation = """
mutation UpdateComment($commentId: ID!, $body: String!) {
  updateDiscussionComment(input: {commentId: $commentId, body: $body}) {
    comment {
      id
      url
      updatedAt
    }
  }
}
"""

req = urllib.request.Request(
    'https://api.github.com/graphql',
    data=json.dumps({'query': mutation, 'variables': {'commentId': COMMENT_ID, 'body': body}}).encode('utf-8'),
    headers={'Authorization': f'Bearer {token}', 'User-Agent': 'Dextermos-Bounty-Hunter'}
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print('SUCCESS:', json.dumps(res, indent=2))
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code, e.read().decode())
except Exception as e:
    print('Error:', e)
