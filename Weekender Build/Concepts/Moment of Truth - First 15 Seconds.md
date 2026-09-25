---
type: concept
tags: [product, voice]
sources: ["[[Idea A - HalloTermin (Abdul)]]"]
---
# Moment of Truth — the first 15 seconds after pickup

"Praxis Dr. Weber, guten Tag?" — in these seconds the receptionist decides to engage or hang up.

## How we win it
1. **Disclosure + purpose in one breath** (see [[AI Disclosure]]):
   > Guten Tag, hier spricht die KI-Assistentin von Frau Priya Sharma. Sie spricht leider noch kein Deutsch, deshalb rufe ich in ihrem Auftrag an. Ich möchte gern einen Termin für eine Erstuntersuchung vereinbaren.
2. **Zero hesitation** — the call brief already has name, DOB, insurance, referral, new-patient flag.
3. **Pre-authorized decisions** — slot inside approved windows → "Ja, Dienstag 8:15 passt."
4. **Escape hatch** — if the practice insists on the patient: offer callback number / (v2) interpreter mode.
5. **Read-back** — "Ich wiederhole: Dienstag, 29. September, 8:15 Uhr, bei Dr. Weber. Richtig?" (see [[Read-back before booking]]).

## Demo metrics
- Pickup → purpose stated: **< 10 s**
- Pickup → booked slot: **< 90 s**

Log each measured attempt as a note in `Runs/`.
