# IPL Decision Intelligence & Contextual Auction Engine

An end-to-end cricket analytics and prescriptive operations platform built in Python.

## Core Modules
- **Phase Feature Decomposer:** Evaluates ball-by-ball events across Powerplay, Middle, and Death overs to compute True Strike Rate (TSR).
- **Algorithmic Valuation:** Maps composite situational impact to IPL auction salary distributions (₹0.5 Cr - ₹18.0 Cr).
- **Player2Vec Embeddings:** High-dimensional cosine similarity vectors to identify budget arbitrage alternatives.
- **SHAP Model Explainability:** Waterfall plots attributing individual price driver impact.
- **Mixed-Integer Linear Programming (MILP):** PuLP CBC solver optimizing 11-player lineups under purse and overseas caps.
- **Counterfactuals & GenAI:** What-If injury replacement scenarios with Gemini 2.5 Flash scouting briefs.

## Files
- `ipl_auction_valuations_2026.csv`
- `ipl_phase_batting_metrics.csv`
- `ipl_phase_bowling_metrics.csv`
- `requirements.txt`
