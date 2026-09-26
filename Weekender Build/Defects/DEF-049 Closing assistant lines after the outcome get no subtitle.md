---
type: defect
date: 2026-09-26
status: open
severity: minor
found_in: "[[RUN-023 Merged flow E2E]]"
owner: abdul (n8n 06 or frontend)
---
# Defect: Closing assistant lines after the outcome get no subtitle

## Observed
In the merged E2E call ([[RUN-023 Merged flow E2E]], Russian parent, course trial lesson booked) 23 of 25 transcript lines got a Russian `text_user`. The last two assistant lines stayed empty for good:
- "Wunderbar, ich notiere das." (written 0.6 s after the outcome)
- "Vielen Dank für die Informationen, auf Wiederhören!" (written 3.3 s after the outcome)

Cause: since the credit change ([[RUN-024 n8n credit optimisation]], migration `20260926210000_credits_translate_practice_only.sql`) assistant lines get no live subtitle. Workflow 06 translates them in one batch when `calls.outcome` changes. The relay sets the outcome inside `confirm_booking` / `record_result`, **before** the agent says its filler and goodbye. 06 reads the untranslated lines at that moment (`lines.pending = 13` in the `result_translated` event), so every line written after it is never picked up. The outcome does not change again at `end_call`, so 06 does not run a second time.

This affects every call that ends with a booking or a recorded result: the parent's live transcript ends with 1–2 German-only lines. The summary card is not affected.

## Expected
Every line of the transcript has a subtitle in the parent's language by the time the call has ended.

## Repro
Any course/Kita role-play that books: `node roleplay-course.js <id>` on a briefed `course_enquiry`, then
`select id, speaker, text_de from transcript_lines where call_id = '<call>' and text_user is null;` → the filler and goodbye lines.

## Fix
Not applied here (integration run; n8n owner decides). Options, cheapest first:
1. **n8n 06:** add a Wait node (about 8–10 s) before *Get Untranslated Lines (GET transcript_lines)*. The relay's goodbye and `ended_at` come 3–6 s after the outcome. No extra Claude call. The summary branch can stay before the Wait so `summary_user` is not delayed.
2. **Frontend (P9/P10):** when `text_user` is null and the call has ended, show the German line with a muted "(German)" label instead of an empty subtitle.
3. **DB:** also notify 06 (lines-only path) when `calls.ended_at` is set. Costs one more n8n execution per call.
