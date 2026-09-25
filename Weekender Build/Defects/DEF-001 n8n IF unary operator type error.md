---
type: defect
date: 2026-09-25
status: fixed
severity: minor
found_in: "[[RUN-003 n8n workflow 01 logic test]]"
owner: claude
---
# Defect: n8n IF unary operator type error

## Observed
`Wrong type: '' is a string but was expecting a boolean [condition 0]` in the IF node.

## Expected
Condition "consent is true" evaluates without a right-hand value.

## Repro
IF v2.3, strict type validation, operator `{type:'boolean', operation:'true'}` with `rightValue: ''`.

## Fix
Add `singleValue: true` to unary operators (`true`, `notEmpty`, …). Applies to every IF/Filter we build via the SDK.
