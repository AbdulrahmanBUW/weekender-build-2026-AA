---
type: rule
severity: must
source: https://supabase.com/docs/guides/troubleshooting/cant-access-supabase-project-lovable-cloud
---
# Rule: Connect our own Supabase before the first backend prompt in Lovable

**Rule:** Create the Supabase project (Frankfurt) first, then connect it in Lovable (**More → Cloud → "Already have a Supabase project? Connect it here"**) *before* asking Lovable for anything that needs a database, login or storage. Do not click "Enable Cloud". (This follows the proposed [[DEC-002 Backend and integration pattern (proposed)]].)
**Why:** Once Lovable Cloud is enabled, "it cannot be disconnected or switched to an external Supabase connection" ([Supabase](https://supabase.com/docs/guides/troubleshooting/cant-access-supabase-project-lovable-cloud)). There is no one-click migration ([Lovable](https://docs.lovable.dev/integrations/supabase)). And Cloud withholds the secret key that n8n and the relay need.
**How to check:** Click the Cloud icon in the Lovable top bar. It must show the **Supabase logo and our project name**, not Lovable's own Database/Users menu ([how to identify](https://supabase.com/docs/guides/troubleshooting/identify-lovable-cloud-or-supabase-backend)).
