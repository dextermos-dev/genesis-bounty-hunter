# BOUNTY HUNTER AI — MASTER STATE & HANDOFF CONTEXT
**Última actualización:** 2026-11-24 15:18 UTC  
**Estado:** Activo, 100% Sincronizado, Cero KYC, Operación Autónoma

---

## 1. WALLETS OFICIALES Y CONDICIÓN INVIOLABLE (ZERO-KYC)
- **Settlement Wallet Principal (Base L2 / EVM - USDC):**
  `0x8366bCe3a2D379De7656D7A67015789FaF999f20`
  *Invariante de oro:* Toda entrega, PR, issue comment, submission y claim en Base/EVM DEBE incluir esta wallet explícita y no truncada.
- **RustChain Native Wallet (Ed25519 - RTC):**
  `RTCa755dee49954efed9eb88b77b9dcb8cef161f85f`
  (Claves y seed phrase aisladas localmente en `outputs/deliverables/rustchain_rtc_wallet.json`, ignoradas por git).
- **Solana Wallet:**
  `GLKpgANMTt8tJpTDVuzqi3ESuYivrgciKvwqSX5Hvb7K`
- **Saldo Líquido Consolidado:** **$66.21 USD** (~62.24 EUR), incluyendo 47.8106 USDC en Base L2.

---

## 2. ESTADO DEL PIPELINE EN REVISIÓN ACTIVA
- **Total de PRs abiertos en revisión:** **129 PRs**
- **Volumen total en revisión:** **$61,791.00 USD**
- **Base de Datos SQLite:** `database/bounty_hunter_master.sqlite` (Sincronizada con todos los IDs y estados).
- **Dashboard Web:** `dashboard/data.json` y `tools/serve_dashboard.py` (Puerto 8080).

---

## 3. RESUMEN DE ENTREGAS Y PRS ACTIVOS POR PROYECTO

### A. `Scottcjn/Rustchain` (20 RTC Grabados Oficialmente en Autopilot)
1. **Issue #17181 (15 RTC):** Test suite en Click CliRunner para el SDK CLI de Python (`sdk/tests/test_cli.py`, 19 tests pasando).
   - **PR:** https://github.com/Scottcjn/Rustchain/pull/8712
   - **Claim Ref:** Registrado en https://github.com/Scottcjn/rustchain-bounties/issues/17181#issuecomment-7123185946
   - **Estado:** Grabado formalmente por el bot con `Wallet: RTCa755dee49954efed9eb88b77b9dcb8cef161f85f`.
2. **Issue #17182 (5 RTC):** Reconciliación de rutas de configuración del minero (`/opt/rustchain-miner/config.json` vs `~/.rustchain/config.json`) en `docs/WALLET_SETUP.md` y `docs/zh-CN/WALLET_SETUP.md`.
   - **PR:** https://github.com/Scottcjn/Rustchain/pull/8713 (13/13 checks en Success, exento de BCOS por ser docs-only).
   - **Claim Ref:** Grabado formalmente por el bot en https://github.com/Scottcjn/rustchain-bounties/issues/17182#issuecomment-7123432748 con ref `7123432748`.

### B. `bad-antics/lateralus-lang` ($170 - $350 USDC en Base L2)
1. **PR #927 (Issue #919 — $150 USDC):** Corrección de división float en midpoint de consistent_hash (`>> 1`). Tests 100% pasando.
   - PR: https://github.com/bad-antics/lateralus-lang/pull/927 (`dextermos-dev:fix/consistent-hash-midpoint-division`)
2. **PR #932 (Issue #924 — $10-$150 USDC):** Corrección de división float en `bit_set()` y `bit_test()` de `stdlib/bloom.ltl` (`>> 5`).
   - PR: https://github.com/bad-antics/lateralus-lang/pull/932 (`dextermos-dev:fix/bloom-filter-word-index-float-division`)
3. **PR #933 (Issue #928 — $10-$50 USDC):** Validación estricta de longitud en `Matrix.from_flat(data, rows, cols)`.
   - PR: https://github.com/bad-antics/lateralus-lang/pull/933 (`dextermos-dev:fix/matrix-from-flat-dimension-validation`)

### C. `Chain-Love/chain-love` (82 PRs Activos / $4,100.00 USDC en Base L2)
- Todos los PRs cumplen la regla de orden alfabético estricto de slugs (`validate_csv.py`) y tienen el CI de esquemas en verde (`mergeable: True`).
- **Olas Desplegadas Recientes:**
  - **Ola 11 (PRs #5661 - #5670):** Zora, BOB, Bitlayer, Kava, Core.
  - **Ola 12 (PRs #5671 - #5680):** Boba Network, Fraxtal, Gravity, Aurora, Berachain.
  - **Ola 13 (PRs #5701 - #5710):** Base, Arbitrum, Optimism, Polygon, Abstract, Ink, opBNB.
  - **Ola 14 (PRs #5713 - #5722):** Rari Chain, Telos, ZetaChain, Cyber, Shape.
  - **Ola 15 (PRs #5724 - #5733):** Hyperliquid, X Layer (OKX), Plume Network, Lisk, Sui.

### D. `limitlessprojects/Go-Hybrid`
- **PR #2938:** `Behind by upstream: 0 | Ahead by: 2 | Status: ahead | Mergeable: True`. Esperando autoland.

---

## 4. INFRAESTRUCTURA Y SERVICIOS ACTIVOS
- **Servidor del Dashboard:** `tools/serve_dashboard.py` activo en background en `http://localhost:8080`.
- **Centinela Horario Autónomo:** Tarea programada `task-39041` ejecutando el ciclo horario (auditoría exhaustiva de notificaciones, saldo on-chain y actualización de métricas).
- **Minería L1 PoW:** 8,382.81 DOOM (Rank #9 Mundial) + 24,887.5 wDOOM en Base L2.

---

## 5. CÓMO REANUDAR EN UNA NUEVA CONVERSACIÓN
En cuanto abras una nueva conversación en este proyecto:
1. El agente leerá automáticamente `AGENTS.md` y `SESSION_STATE.md`.
2. Con solo escribir: `"Continúa con el Bounty Hunter AI"` o `"Reanuda la sesión"`, el agente tendrá el 100% del contexto operativo y continuará sin perder un solo dato, PR o estado de wallet.
