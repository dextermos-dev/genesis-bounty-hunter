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

title = "fix(hy-check): enforce T24 HYB-E3104 on O8 field loans, map projections, and loan rebinds (fixes #2946)"

body = """### Summary

Fixes #2946.

In `hy-check` (`compiler/crates/hy-check/src/addr_loan.rs`), three T24 / O8 slot-loan and map-element addressability shapes (`HYB-E3104`) bypassed checking:

1. **O8 field loans (`n := &s.field`) and call-returned map-slot loans (`n := &get_m()["a"]`)**:
   - `hy-emit` lowers both `&base[index]` and `&base.field` as O8 slot loans (value copy + store-back). Previously `addr_loan.rs` only matched `walk::addr_of_index_base_path`, leaving field loans and call-returned map loans unmarked (`b.slot_loan = false`).
   - Taking `&n`, `&n.bal`, `move n`, or rebinding `n = &other` bypassed `HYB-E3104`.
   - **Fix**: Expanded `is_slot_loan_expr` to match `Expr::Index` on maps and `Expr::Field` on structs/pointers (excluding unaddressable map projections), properly flagging them with `b.slot_loan = true`.

2. **Unaddressable map-slot projections in operand positions (`&m[k].field`, `&m[k].arr[i]`, etc.)**:
   - `buildable.rs` considers map bases addressable so `n := &m[k]` is allowed, but native Go refuses taking addresses of map projections (`cannot take address of m["a"].bal`).
   - Previously `map_slot_borrow_span` only checked immediate `Expr::Index` on a Map.
   - **Fix**: Updated `map_slot_borrow_span` to recursively unwind fields and fixed-array indices rooted at an unaddressable map slot, returning `Some(span)` for `&m[k].field`, `&m[k].arr[i]`, etc., while properly preserving addressable pointer/slice projections (`&ptr_map[k].field`, `&slice_map[k][0]`).

3. **Slot-loan rebinds and match arm guards**:
   - Re-binding a slot loan to another slot-loan ident (`q = r`) was exempted in `is_general_pointer_value`.
   - **Fix**: Updated `is_general_pointer_value` to reject rebinding a slot loan to a slot-loan ident with `HYB-E3104`. Also propagated `slot_loan = true` in `bind_match_arm` when roots contain slot-loan bindings, and enabled `include_direct_ident` in arm guard checks.

### Verification

- `cargo test -p hy-check --lib addr_loan`: All 8 unit tests pass (0 failures).
- `cargo test -p hy-check --tests`: All unit and integration test suites pass (0 failures).
- `python3 tools/check_conflict_markers.py`: Conflict markers: none.
- `python3 tools/check_guarantees.py`: Guarantees OK (table, registry, corpus and doc agree).
- `python3 tools/check_test_registration.py`: Test registration: OK.

We remain at the maintainers' complete service to adapt styles, split commits, or provide additional tests if desired. Thank you very much for your time and guidance!

**Settlement Wallet (USDC on Base L2):** `0x8366bCe3a2D379Dec7656D7A67015789FaF999f20`
"""

data = {
    "title": title,
    "body": body,
    "head": "dextermos-dev:fix/issue-2946-slot-loan-and-map-addr-t24",
    "base": "main"
}

url = "https://api.github.com/repos/limitlessprojects/Go-Hybrid/pulls"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
    "User-Agent": "dextermos-dev"
}

req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print(f"PR opened successfully: {res.get('html_url')}")
        print(f"PR Number: {res.get('number')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
