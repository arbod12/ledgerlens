# LedgerLens — Audit Anomaly Detection Engine

A browser-based analytical-procedures engine that screens an **entire general ledger population** (not a sample) for the fraud and error patterns that audit data-analytics teams test for. Built to run fully client-side — uploaded data never leaves the browser, there is no server, and there are no API costs.

**Live demo:** _[add your Netlify URL here]_

---

## Why this exists

Modern audit firms increasingly run full-population analytics with tools like MindBridge, CaseWare IDEA, and DataSnipper, rather than relying on traditional sampling. LedgerLens is a working, transparent demonstration of the core analytical procedures behind those platforms — built by an accounting student to show command of *both* the audit theory and the technology.

It is a demonstration tool on synthetic data, not production audit software.

## What it tests

| # | Procedure | What it catches | Audit rationale |
|---|-----------|-----------------|-----------------|
| 1 | **Benford's Law** (first-digit) | Fabricated / manipulated amounts | Natural financial figures follow a logarithmic first-digit distribution (~30% begin with 1). A large chi-square deviation signals amounts that were invented rather than transacted. |
| 2 | **Duplicate payments** | Double-paid invoices, split billing | Same vendor + same amount within a short window is a classic disbursement-cycle error/fraud. |
| 3 | **Threshold gaming** | Approval-limit circumvention | Entries clustered just below an approval limit suggest deliberate structuring to avoid review. |
| 4 | **Round-dollar entries** | Estimates, manual journal entries | Exact round amounts rarely arise from genuine arms-length transactions; they flag management estimates and top-side entries. |
| 5 | **Off-hours / weekend posting** | Segregation-of-duties red flags | Entries posted outside business hours warrant review for override of controls. |
| 6 | **Statistical outliers** | Unusual magnitude items | Z-score screening surfaces entries far from the population mean for targeted testing. |

Each flagged entry is **risk-scored** (Critical / High / Medium / Low), filterable by test, sortable, and exportable to CSV alongside an auto-generated finding-memo template.

## Tech

- Single self-contained `index.html` — HTML, CSS, vanilla JS, no build step, no dependencies
- All detection logic implemented from first principles (Benford chi-square, z-score outliers, duplicate matching)
- Detection logic validated against an independent Python/pandas reference implementation (see `generate_data.py`)

## Data

`sample_ledger.csv` is **fully synthetic** — 1,563 fabricated journal entries with deliberately planted anomalies so the engine has real signals to find. No real entity, vendor, or transaction is represented. Bring your own GL by matching the column headers.

## Roadmap

- Graph-based vendor-relationship view (hidden-network detection)
- Configurable materiality thresholds per account
- PDF finding-report export

---

Built by **Ariel Bodik** · B.S. Accounting, Fairleigh Dickinson University
