---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-017 Family courses seed]]"
owner: abdul
---
# Defect: price_type cannot express fee plus trial

## Observed
`resources.price_type` holds a single value (`free | per_session | subscription | trial_available | unknown`). Most real course providers have **both** a fee model and a trial lesson. For example, Musikschule Adagio charges monthly contract fees and offers a free 30-min trial, and KiDDs has a monthly membership with 3 trial sessions. In [[RUN-017 Family courses seed]], 8 of 18 rows got `trial_available`, so the "subscription" or "per course" information is lost. A "Free" filter also cannot show "free with Dresden-Pass" (Jugendkunstschule) or a free sub-group (Naturcamp Heidefüchse).

## Expected
Parents can filter by "trial lesson available" and still see how they pay (per course or monthly).

## Repro
Try to store a provider that has monthly fees and a free trial. Only one of the two fits.

## Fix
Suggested: add `has_trial boolean not null default false` via a new migration and keep `price_type` for the payment model. Until then, the seed rule is: `trial_available` wins when a trial is stated, and the fee is written in `description_en` / `i18n`. The frontend should show the description and not rely on `price_type` alone.
