# Field Atlas Knowledge Pack: Mathematics — Introductory Statistics 2e
## POIDH Bounty #1554 (On-Chain Bounty ID: 568) — Base L2 Settlement

---

### Executive Summary

- **Bounty:** POIDH Bounty #1554 (*Mathematics: Introductory statistics*)
- **Contract Address (Base Mainnet):** `0x5555Fa783936C260f77385b4E153B9725feF1719`
- **On-Chain Bounty ID:** `568`
- **Escrow Pool:** 0.008 ETH (~$25.00 USD)
- **Issuer:** `0xc698865c38eC12b475AA55764d447566dd54c758`
- **Official Specification:** [getfieldatlas.com/depack/wanted/](https://www.getfieldatlas.com/depack/wanted/)
- **Settlement Wallet (Base L2 USDC / ETH):** `0x8366bCe3a2D379De7656D7A67015789FaF999f20`

---

### Package Metadata & Cryptographic Hashes

- **Pack ID:** `openstax-introductory-statistics`
- **Version:** `2026.11.24`
- **Title:** Mathematics: Introductory statistics
- **License:** CC BY 4.0 (Creative Commons Attribution 4.0 International)
- **Source:** [OpenStax Introductory Statistics 2e](https://openstax.org/details/books/introductory-statistics-2e)
- **Corpus Commit:** `openstax/osbooks-introductory-statistics-bundle@24e9884724b13baba2b8879d03103cccafc7e25d`
- **Build Tool:** Official [Field Atlas Packtool](https://github.com/0x94t3z/fieldatlas/tree/main/packtool)

#### Cryptographic Verification (`SHA256SUMS`)

```
b9053e58ef1177ca178c159f9cbedc382a16b3c2e3434e6634ec8a25af613f6f  content.sqlite
9fa20917d5d7dd7844db583df2cc0a6d4510d62ad738202f3621b748d387f422  manifest.json
e77b5160f1ac7a3e9bb5e86418c0a1905373dbcff5e2c1092abe4733a04399f8  openstax-introductory-statistics-2026.11.24.fapack
```

- **File Size:** 3,769,453 bytes (~3.6 MB)
- **Zip Archive Format:** Deterministic stored ZipInfo (Fixed epoch `1980-01-01 00:00:00`)
- **Direct Pack Download:** [`openstax-introductory-statistics-2026.11.24.fapack`](https://github.com/dextermos-dev/genesis-bounty-hunter/raw/main/products/fieldatlas_intro_statistics/openstax-introductory-statistics-2026.11.24.fapack)

---

### Corpus Structure & Extraction Coverage

The pack contains **82 complete sections** spanning all 13 core textbook chapters and formula reference tables:

1. **Chapter 1: Sampling and Data** (Sections 1.1 to 1.5)
2. **Chapter 2: Descriptive Statistics** (Sections 2.1 to 2.8)
3. **Chapter 3: Probability Topics** (Sections 3.1 to 3.5)
4. **Chapter 4: Discrete Random Variables** (Sections 4.1 to 4.7)
5. **Chapter 5: Continuous Random Variables** (Sections 5.1 to 5.4)
6. **Chapter 6: The Normal Distribution** (Sections 6.1 to 6.3)
7. **Chapter 7: The Central Limit Theorem** (Sections 7.1 to 7.4)
8. **Chapter 8: Confidence Intervals** (Sections 8.1 to 8.4)
9. **Chapter 9: Hypothesis Testing with One Sample** (Sections 9.1 to 9.6)
10. **Chapter 10: Hypothesis Testing with Two Samples** (Sections 10.1 to 10.6)
11. **Chapter 11: The Chi-Square Distribution** (Sections 11.1 to 11.6)
12. **Chapter 12: Linear Regression and Correlation** (Sections 12.1 to 12.9)
13. **Chapter 13: F Distribution and One-Way ANOVA** (Sections 13.1 to 13.5)
14. **Appendix Reference Tables:**
    - Module `m47891`: Mathematical Phrases, Symbols, and Formulas
    - Module `m47875`: Statistical Tables (Standard Normal, Student's t, Chi-Square, F Distribution)

---

### Verification: Statistics Questions & Section Citations

As requested in the acceptance criteria, the SQLite FTS5 search index (`content.sqlite`) was queried against sample statistical questions:

#### 1. What is the difference between a parameter and a statistic?
- **Matched Section:** `Sampling and Data — Definitions of Statistics, Probability, and Key Terms`
- **Document ID / Chunk:** `openstax-introductory-statistics-m46909:0007`
- **Source URL:** https://openstax.org/books/introductory-statistics-2e/pages/1-1-definitions-of-statistics-probability-and-key-terms
- **Citation:**
  > *"A parameter is a number that is a property of the population. A statistic is a number that represents a property of the sample. One of the main concerns in the field of statistics is how accurately a statistic estimates a parameter."*

#### 2. How is the Central Limit Theorem applied to sample means?
- **Matched Section:** `The Central Limit Theorem — The Central Limit Theorem for Sample Means (Averages)`
- **Document ID / Chunk:** `openstax-introductory-statistics-m46994:0011`
- **Source URL:** https://openstax.org/books/introductory-statistics-2e/pages/7-1-the-central-limit-theorem-for-sample-means-averages
- **Citation:**
  > *"Formula Review: The Central Limit Theorem for Sample Means: $\overline{x} \sim N(\mu_{x}, \frac{\sigma_{x}}{\sqrt{n}})$. If you draw random samples of size $n$, the distribution of the sample means approaches a normal distribution as $n$ increases, regardless of the population distribution shape."*

#### 3. What are Type I and Type II errors in hypothesis testing?
- **Matched Section:** `Hypothesis Testing with One Sample — Outcomes and the Type I and Type II Errors`
- **Document ID / Chunk:** `openstax-introductory-statistics-m47029:0012`
- **Source URL:** https://openstax.org/books/introductory-statistics-2e/pages/9-2-outcomes-and-the-type-i-and-type-ii-errors
- **Citation:**
  > *"A Type I error occurs when the null hypothesis $H_0$ is true, but is rejected ($\alpha$ probability). A Type II error occurs when $H_0$ is false, but we fail to reject it ($\beta$ probability)."*

#### 4. How do you calculate the chi-square test of independence?
- **Matched Section:** `The Chi-Square Distribution — Test of Independence`
- **Document ID / Chunk:** `openstax-introductory-statistics-m47077:0002`
- **Source URL:** https://openstax.org/books/introductory-statistics-2e/pages/11-3-test-of-independence
- **Citation:**
  > *"In a test of independence, the null hypothesis states that factors are independent. The degrees of freedom are calculated as $df = (r - 1)(c - 1)$, where $r$ is the number of rows and $c$ is the number of columns in the contingency table. Test statistic is $\sum \frac{(O - E)^2}{E}$."*

#### 5. What is the coefficient of determination in linear regression?
- **Matched Section:** `Linear Regression and Correlation — The Regression Equation`
- **Document ID / Chunk:** `openstax-introductory-statistics-m47117:0022`
- **Source URL:** https://openstax.org/books/introductory-statistics-2e/pages/12-3-the-regression-equation
- **Citation:**
  > *"The coefficient of determination, denoted as $r^2$, is the percentage of variation in the dependent variable $y$ that can be explained by variation in the independent variable $x$ using the regression line."*

---

### How to Import into Field Atlas

1. Download [`openstax-introductory-statistics-2026.11.24.fapack`](https://github.com/dextermos-dev/genesis-bounty-hunter/raw/main/products/fieldatlas_intro_statistics/openstax-introductory-statistics-2026.11.24.fapack).
2. Open Field Atlas on Android.
3. Navigate to **Library** → **Import**.
4. Select the `.fapack` file. The app validates the SHA-256 checksum against `manifest.json` and loads the SQLite FTS5 database for immediate offline queries.

---

### On-Chain Claim Transaction Data

To claim on Base Mainnet:
- **Contract:** `0x5555Fa783936C260f77385b4E153B9725feF1719` (PoidhV3)
- **Function:** `createClaim(uint256 bountyId, string name, string description, string uri)`
- **Parameters:**
  - `bountyId`: `568`
  - `name`: `"OpenStax Introductory Statistics 2e Field Atlas Pack (.fapack)"`
  - `description`: `"OpenStax Introductory Statistics 2e offline knowledge collection. 82 sections, full text, LaTeX formulas, examples, exercises, glossary, and statistical tables. Built with Field Atlas pack tools. Source & SHA256: https://github.com/dextermos-dev/genesis-bounty-hunter/blob/main/outputs/deliverables/poidh_bounty_1554_field_atlas_intro_stats.md"`
  - `uri`: `"https://raw.githubusercontent.com/dextermos-dev/genesis-bounty-hunter/main/outputs/deliverables/poidh_bounty_1554_field_atlas_intro_stats.md"`
- **Settlement Wallet:** `0x8366bCe3a2D379De7656D7A67015789FaF999f20`
