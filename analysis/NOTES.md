# Verdict — Illinois tornado year, 2026

**Question.** How extraordinary is Illinois' 2026 tornado count, and what does the 283 on the
IEM plate actually represent? Unit of analysis: state-season, 1 Jan – 13 Aug.

**Confounder named up front.** The headline metric is *reports*, not tornadoes. Report counts
scale with population density, spotter networks and county geometry as much as with weather —
so a raw-count choropleth of LSRs is partly a map of who was watching. Every comparison here is
against the same state's own history, which holds that exposure roughly constant.

## What the data supports

- Illinois logged **283** preliminary tornado reports, **4.13×** its 2004–2025 average for the
  identical window and **#1 of 23** years on the archived record. Its previous year-to-date high
  was 156 (2023) — 2026 is 81% above it.
- The anomaly is regional, not national. Indiana **3.54×**, Pennsylvania **3.00×**, Michigan
  **2.66×**, Wisconsin **1.99×** — Illinois, Indiana and Pennsylvania each at their own #1.
- Simultaneously, classic Tornado Alley was quiet: Texas **0.38×** (21st of 23 years), Florida
  **0.23×**, Tennessee **0.35×**, North Dakota **0.33×**.
- Nationally the season is only **1.16×** normal. The country did not have an unusual number of
  tornadoes; a compact band of the Midwest and Ohio Valley had a disproportionate share.
- Illinois' all-time single-year record for *surveyed* tornadoes is **133 (2024)**. It has been
  in a sustained run: 116 (2023), 133 (2024), 118 (2025).

## What the data does not support

The 283 is not a tornado count and should never be reported as one. Where 2026 surveys are
complete (through 31 May), Illinois has **68 confirmed tornadoes against 143 reports — a ratio
of 0.476**, third-lowest of the fifteen states with enough reports to measure, and well below
Illinois' own 2004–2025 pooled ratio of 0.773.

## The genuine uncertainty — two credible calibrations that disagree

| Calibration | Ratio | Implied 2026 Illinois tornadoes |
|---|---|---|
| Illinois' pooled 2004–2025 history | 0.773 | **219** — would shatter the 133 record |
| Illinois' own observed 2026 surveys | 0.476 | **135** — would just surpass it |

Both are shown, never averaged. The disagreement is itself a finding: something about 2026's
Illinois reporting is unusually duplicative — plausibly the geography of the outbreaks (the
18 April event alone filed 49 reports, and long tracks across the state's dense small-county
grid generate a report per county). Either way the confirmed count lands at or above the state
record, with three and a half months of season left.

## What I would fetch next to tighten it

1. **NCEI storm-events for June–August 2026** (due ~November). June alone produced 109 Illinois
   reports, the biggest month of the year, and none of it is surveyed in the public record. That
   single file would collapse most of the 135–219 gap.
2. **Per-outbreak track lengths** from the eventual SPC file, to test the duplication hypothesis
   directly rather than inferring it from the ratio.
3. **NWS Chicago / Lincoln / Paducah public information statements** for confirmed counts ahead
   of NCEI publication.

## Open threads

- 2003 is missing from the LSR baseline (Autoplot 400s); baseline is 23 years, not 24.
- The ratio calibration pools state-years with ≥5 reports; it is not conditioned on report
  count, and high-count state-years may behave differently from the pool. The 2026-observed
  ratio is the more directly relevant estimator, which is why it anchors the lower bound.
- Detection has improved enormously since 1950. Pre-1990 records in the all-time table are a
  floor, not a like-for-like comparison.
