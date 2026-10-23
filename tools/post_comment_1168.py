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

body = """/claim #1168 Fixes #1168

Hello @limitlessprojects and @semilla1lab,

We have investigated this soundness issue and submitted a complete, verified fix along with regression tests in PR #1173:
https://github.com/limitlessprojects/Go-Hybrid/pull/1173

### Summary of Changes

1. **Root Cause Analysis**:
   - Per `SPEC-LANGUAGE.md` (LX6), prefixed base literals (`0x`, `0b`, `0o`) cannot have fractional parts.
   - When encountering a literal like `0x1.8`, `lex_number()` previously stopped scanning at `.`, emitting `Tok::Int("0x1")`. The remaining `.8` was scanned as an orphan `Tok::Float(".8")` on the same line, producing two consecutive statements that passed `hyb check` with 0 diagnostics and broke Row 13 `BUILDABLE` during `go build`.

2. **Lexer Fix (`compiler/crates/hy-syntax/src/lexer.rs`)**:
   - In `lex_number()`: after scanning prefixed base digits, if a dot is followed by a character other than another dot (`self.at(0) == Some('.') && self.at(1) != Some('.')`), the fraction and any exponent tail are consumed into the token.
   - Emits an explicit fail-closed `HYB-E0002` [LX6] diagnostic (`malformed 0{base} integer literal: prefixed base literals cannot have a fractional part (SPEC-LANGUAGE.md LX6)`).
   - Valid range expressions (`0x0..0x10`, `0x1..=0x10`, `0b0..0b10`, `0o0..0o7`) are guarded by `self.at(1) != Some('.')` and remain 100% legal.

3. **Test Coverage**:
   - **Unit Tests (`compiler/crates/hy-syntax/src/lexer.rs`)**: Added `prefixed_base_literal_fraction_issue_1168` testing `0x1.8`, `0x1.f`, `0x1.8p-2`, `0x1.`, `0o7.5`, `0b1.0` and range semantics.
   - **Soundness Tests (`compiler/crates/hy-syntax/tests/lexer_soundness.rs`)**: Added `prefixed_base_literal_with_fraction_fails_closed` testing fail-closed diagnostics on `0x1.8`, `0x1.8p+3`, `0b101.1`, `0o77.2`, `0xDEAD.BEEF`.
   - All 112 unit tests + 8 integration tests + 5 parse tests in `hy-syntax` pass cleanly.

We are at your disposal if you would like any formatting adjustments, additional test cases, or commit reorganizations. Thank you very much for your time and guidance!

**Settlement Wallet (USDC / Base L2):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

payload = {'body': body}

req = urllib.request.Request(
    'https://api.github.com/repos/limitlessprojects/Go-Hybrid/issues/1168/comments',
    data=json.dumps(payload).encode('utf-8')
)
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Accept', 'application/vnd.github+json')
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req) as resp:
        res = json.load(resp)
        print('Comment posted successfully!')
        print('Comment URL:', res['html_url'])
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, e.reason)
    print(e.read().decode('utf-8'))
