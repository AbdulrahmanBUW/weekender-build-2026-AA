---
type: rule
severity: must
source: "§201 StGB"
---
# Rule: Never store call audio

**Rule:** No audio recording anywhere (voice platform recording OFF, no audio files in Supabase/storage). Text transcript only.
**Why:** Recording non-public speech without consent is a criminal offence in Germany.
**How to check:** Check voice platform settings (recording/audio retention disabled) before first real call; grep storage buckets.

Related: [[AI Disclosure]]
