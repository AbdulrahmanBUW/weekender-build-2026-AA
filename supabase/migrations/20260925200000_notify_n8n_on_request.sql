-- New call_request -> POST to n8n production webhook (pattern chosen in DEC-002).
-- URL + shared secret live in Supabase Vault (never in git). Set them once per environment:
--   select vault.create_secret('https://<instance>.app.n8n.cloud/webhook/new-request', 'n8n_new_request_url');
--   select vault.create_secret('<long random string>', 'n8n_webhook_secret');
-- If the URL secret is missing, the trigger is a no-op (inserts never fail because of n8n).
-- Debug deliveries: select id, status_code, error_msg, timed_out from net._http_response order by id desc limit 10;

create extension if not exists pg_net with schema extensions;

create or replace function public.notify_n8n_new_request()
returns trigger
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  v_url    text;
  v_secret text;
begin
  select decrypted_secret into v_url    from vault.decrypted_secrets where name = 'n8n_new_request_url';
  select decrypted_secret into v_secret from vault.decrypted_secrets where name = 'n8n_webhook_secret';

  if v_url is null then
    return new;
  end if;

  perform net.http_post(
    url                  := v_url,
    body                 := jsonb_build_object('type', 'INSERT', 'table', TG_TABLE_NAME, 'record', to_jsonb(new)),
    headers              := jsonb_build_object('Content-Type', 'application/json',
                                               'X-Webhook-Secret', coalesce(v_secret, '')),
    timeout_milliseconds := 5000
  );

  insert into public.events (request_id, source, type, payload)
  values (new.id, 'system', 'n8n_notified', jsonb_build_object('url_host', split_part(v_url, '/', 3)));

  return new;
end $$;

create trigger call_requests_notify_n8n
  after insert on public.call_requests
  for each row execute function public.notify_n8n_new_request();
