-- Demo data: one finished booking so the UI has something to show before the first real call.
insert into public.call_requests (id, status, patient_name, patient_dob, insurance_type, insurance_name,
  user_email, practice_name, practice_phone, reason_category, has_referral, is_new_patient, time_windows,
  consent_ai_call, call_brief_de)
values ('00000000-0000-0000-0000-000000000001', 'booked', 'Priya Sharma', '2002-03-14', 'gkv', 'Techniker Krankenkasse',
  'priya@example.com', 'Hausarztpraxis Dr. Weber', '+49 351 0000000', 'first_visit', false, true,
  '[{"date":"2026-09-29","from":"08:00","to":"12:00"},{"date":"2026-09-30","from":"14:00","to":"18:00"}]', true,
  'Termin für eine Erstuntersuchung, Neupatientin, gesetzlich versichert (TK), keine Überweisung.');

insert into public.calls (id, request_id, provider, started_at, ended_at, outcome, booked_slot, bring_items, summary_en)
values ('00000000-0000-0000-0000-0000000000c1', '00000000-0000-0000-0000-000000000001', 'mock',
  now() - interval '5 min', now() - interval '3 min', 'booked', '2026-09-29 08:15+02',
  array['Versichertenkarte'], 'Booked: Tue 29 Sep, 08:15 with Dr. Weber. Bring your insurance card.');

insert into public.transcript_lines (call_id, speaker, text_de, text_en) values
('00000000-0000-0000-0000-0000000000c1','practice','Praxis Dr. Weber, guten Tag?','Dr. Weber''s practice, hello?'),
('00000000-0000-0000-0000-0000000000c1','agent','Guten Tag, hier spricht die KI-Assistentin von Frau Priya Sharma. Sie spricht leider noch kein Deutsch, deshalb rufe ich in ihrem Auftrag an. Ich möchte gern einen Termin für eine Erstuntersuchung vereinbaren.','Hello, this is Ms Priya Sharma''s AI assistant. She doesn''t speak German yet, so I''m calling on her behalf. I''d like to book a first examination.'),
('00000000-0000-0000-0000-0000000000c1','practice','Ist sie Neupatientin? Hat sie eine Überweisung?','Is she a new patient? Does she have a referral?'),
('00000000-0000-0000-0000-0000000000c1','agent','Ja, sie ist Neupatientin, gesetzlich versichert bei der TK, eine Überweisung hat sie nicht.','Yes, she is a new patient, publicly insured with TK, she has no referral.'),
('00000000-0000-0000-0000-0000000000c1','practice','Dienstag, 8:15 Uhr?','Tuesday, 8:15?'),
('00000000-0000-0000-0000-0000000000c1','agent','Ich wiederhole: Dienstag, 29. September, 8:15 Uhr, bei Dr. Weber. Richtig?','Let me repeat: Tuesday 29 September, 8:15, with Dr. Weber. Correct?'),
('00000000-0000-0000-0000-0000000000c1','practice','Richtig. Bitte die Versichertenkarte mitbringen.','Correct. Please bring the insurance card.');

insert into public.events (request_id, source, type, payload) values
('00000000-0000-0000-0000-000000000001','app','request_submitted','{}'),
('00000000-0000-0000-0000-000000000001','n8n','brief_created','{}'),
('00000000-0000-0000-0000-000000000001','voice','call_started','{"provider":"mock"}'),
('00000000-0000-0000-0000-000000000001','voice','call_ended','{"outcome":"booked"}'),
('00000000-0000-0000-0000-000000000001','n8n','email_sent','{"to":"priya@example.com"}');
