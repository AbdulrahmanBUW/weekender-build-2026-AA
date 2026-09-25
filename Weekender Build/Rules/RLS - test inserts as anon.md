---
type: rule
severity: should
source: https://supabase.com/docs/guides/database/postgres/row-level-security
---
# Rule: RLS - write explicit policies and test as the browser would

**Rule:** Every table the app touches has RLS enabled, with explicit policies that name the role (`to anon` / `to authenticated`). Test the insert, select and Realtime path **from the published app (or with the publishable key)**, not from the SQL editor or n8n, because those bypass RLS.
**Why:** With RLS on and no policy, anon requests are silently denied (empty lists, insert errors, no Realtime events). Tests with the secret key or the SQL editor "work" because `service_role` bypasses RLS, which hides the bug until the demo. `insert().select()` also needs a SELECT policy ([RLS docs](https://supabase.com/docs/guides/database/postgres/row-level-security)).
**How to check:** Submit the form on `https://<name>.lovable.app` in a private window → the row appears in the Table Editor → the page shows the status change when you run `update call_requests set status='calling' where id='…'` in the SQL editor. Policy SQL is in [[Supabase - Practical Guide#2. RLS for a demo without real login]].
