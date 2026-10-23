import urllib.request
import urllib.error
import json
import os

token = ""
with open('.env') as f:
    for line in f:
        if line.startswith('GITHUB_TOKEN='):
            token = line.strip().split('=', 1)[1]
            break

title = "fix(hy-syntax): reject prefixed base literals with fractional part (fixes #1168)"

body = """### Summary

Fixes #1168.

Per SPEC-LANGUAGE.md (LX6):
> Numeric literals: decimal integer, octal (`0o` or `0`), hex (`0x`), binary (`0b`), and float (`2.`, `.5`, `1.5`, `1e9`). Hybrid has no hex-float literals.

Prior to this fix, when a prefixed base integer literal (`0x`, `0b`, `0o`) was followed directly by a fraction dot (such as `0x1.8`), the lexer stopped scanning digits at the `.`, emitting `Tok::Int("0x1")`. Because newlines and statement boundaries are contextual, the remaining `.8` was scanned as an orphan `Tok::Float(".8")`. The parser treated this as two statements (`n := 0x1` followed by expression statement `.8`), passing `hyb check` with 0 diagnostics and subsequently failing `go build` (`.8 is not used`), breaking the Row 13 `BUILDABLE` guarantee.

### Solution

1. In `compiler/crates/hy-syntax/src/lexer.rs` within `lex_number()`:
   - When encountering a `.` after scanning prefixed base digits, verify that it is not a range operator (`self.at(0) == Some('.') && self.at(1) != Some('.')`).
   - If a fractional dot is present, consume the dot and following characters (`[a-zA-Z0-9_+-]`) into the token so that the entire malformed literal is preserved within a single span.
   - Emit an explicit fail-closed `HYB-E0002` [LX6] diagnostic (`malformed 0{base} integer literal: prefixed base literals cannot have a fractional part (SPEC-LANGUAGE.md LX6)`).
2. Ensured integer range syntax (`0x0..0x10`, `0x1..=0x10`, `0b0..0b10`, `0o0..0o7`) remains 100% valid by guarding against `self.at(1) == Some('.')`.

### Verification & Tests

1. Added comprehensive unit tests in `compiler/crates/hy-syntax/src/lexer.rs`:
   - `prefixed_base_literal_fraction_issue_1168`: validates `0x1.8`, `0x1.f`, `0x1.8p-2`, `0x1.`, `0o7.5`, `0b1.0` all emit `HYB-E0002` [LX6] diagnostics and that range operations `0x1..0x10` and `0x1..=0x10` remain untouched.
2. Added dedicated integration tests in `compiler/crates/hy-syntax/tests/lexer_soundness.rs`:
   - `prefixed_base_literal_with_fraction_fails_closed`: verifies fail-closed rejection on `0x1.8`, `0x1.8p+3`, `0b101.1`, `0o77.2`, `0xDEAD.BEEF`, while confirming valid ranges stay accepted.
3. Test suite results:
   - `cargo test -p hy-syntax`: 112 unit tests + 8 integration tests + 5 parse tests all pass (exit code 0).

We remain completely at the maintainers' disposal to adjust diagnostics, split commits, or adapt any formatting preferences as needed. Thank you very much for your time and guidance!

**Settlement Wallet (USDC / Base L2):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {
    'title': title,
    'head': 'dextermos-dev:fix/1168-reject-hex-literal-with-fraction',
    'base': 'main',
    'body': body
}

req = urllib.request.Request(
    'https://api.github.com/repos/limitlessprojects/Go-Hybrid/pulls',
    data=json.dumps(payload).encode('utf-8')
)
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Accept', 'application/vnd.github+json')
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req) as resp:
        res = json.load(resp)
        print('PR created successfully!')
        print('PR URL:', res['html_url'])
        print('PR Number:', res['number'])
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, e.reason)
    print(e.read().decode('utf-8'))
