-- Security review 2026-09-26 (medium): anon inserts could pre-set status / call_brief_de,
-- which would inject text into the voice agent's prompt and skip the pipeline.
-- Browsers may only create fresh requests; everything else is written by n8n / the relay (service role).

drop policy if exists "anon can submit requests" on public.call_requests;

create policy "anon can submit requests" on public.call_requests
  for insert to anon, authenticated
  with check (
    consent_ai_call
    and status = 'submitted'
    and call_brief_de is null
  );
