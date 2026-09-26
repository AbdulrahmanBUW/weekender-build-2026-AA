-- n8n Gateway credits (26.09): live subtitles only for what the OTHER SIDE says.
-- The parent already approved the assistant's German lines on the approval card; those are translated
-- once, in a batch, when the call ends (workflow 06). This halves the Claude calls AND the n8n executions per call.
-- Emergency kill switch (no live subtitles at all):  delete from vault.secrets where name = 'n8n_translate_line_url';

create or replace function public.on_transcript_line()
returns trigger language plpgsql security definer set search_path = public as $$
declare v_lang text;
begin
  if new.speaker <> 'practice' then
    return new;                                  -- agent/system lines: no live translation
  end if;
  if char_length(trim(new.text_de)) < 2 then
    return new;                                  -- empty/noise lines
  end if;
  select r.user_language into v_lang
    from public.calls c join public.call_requests r on r.id = c.request_id where c.id = new.call_id;
  perform public.notify_n8n('n8n_translate_line_url', jsonb_build_object(
    'line_id', new.id, 'call_id', new.call_id, 'speaker', new.speaker, 'text_de', new.text_de,
    'user_language', coalesce(v_lang, 'en')));
  return new;
end $$;
