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

-- ---------- v2 (generic tasks + multilingual) ----------
update public.call_requests
   set task_type = 'doctor_appointment', user_language = 'en',
       goal_user = 'Book a first examination with a GP (new patient, public insurance).',
       goal_de = 'Termin für eine Erstuntersuchung (Neupatientin, gesetzlich versichert).',
       organisation_category = 'doctor',
       allowed_facts = '[{"key":"dob","label":"Date of birth","value":"14.03.2002"},{"key":"insurance","label":"Insurance","value":"Techniker Krankenkasse (gesetzlich)"}]'
 where id = '00000000-0000-0000-0000-000000000001';

update public.transcript_lines set text_user = text_en where call_id = '00000000-0000-0000-0000-0000000000c1';

-- Demo 2: Arabic user, pharmacy stock question (information task, "completed")
insert into public.call_requests (id, status, task_type, patient_name, user_language, practice_name, practice_phone,
  organisation_category, goal_user, goal_de, allowed_facts, time_windows, consent_ai_call, call_brief_de)
values ('00000000-0000-0000-0000-000000000002', 'completed', 'pharmacy_question', 'Amina Haddad', 'ar',
  'Apotheke am Albertplatz', '+49 351 0000001', 'pharmacy',
  'اسأل إذا كان دواء إيبوبروفين 400 متوفرًا للاستلام اليوم',
  'Nachfragen, ob Ibuprofen 400 heute zur Abholung vorrätig ist.',
  '[{"key":"medicine","label":"Medicine","value":"Ibuprofen 400, 20 Tabletten"}]', '[]', true,
  'ERÖFFNUNG: Guten Tag, hier ist die KI-Assistentin von Amina Haddad. Ich rufe für sie an, weil ihr Deutsch noch nicht so gut ist, und wollte fragen, ob Ibuprofen 400 heute vorrätig ist.');

insert into public.calls (id, request_id, provider, started_at, ended_at, outcome, result, summary_en, summary_user, disclosure_variant)
values ('00000000-0000-0000-0000-0000000000c2', '00000000-0000-0000-0000-000000000002', 'mock',
  now() - interval '9 min', now() - interval '8 min', 'completed',
  '{"in_stock": true, "pickup_until": "18:30", "price_eur": 3.49}',
  'Ibuprofen 400 is in stock. You can pick it up today until 18:30. Price about 3.49 EUR.',
  'إيبوبروفين 400 متوفر. يمكنك استلامه اليوم حتى الساعة 18:30. السعر حوالي 3.49 يورو.', 'warm_default');

insert into public.transcript_lines (call_id, speaker, text_de, text_en, text_user) values
('00000000-0000-0000-0000-0000000000c2','practice','Apotheke am Albertplatz, guten Tag?','Pharmacy at Albertplatz, hello?','صيدلية ألبرت بلاتس، مرحبًا؟'),
('00000000-0000-0000-0000-0000000000c2','agent','Guten Tag, hier ist die KI-Assistentin von Amina Haddad. Ich wollte fragen, ob Sie Ibuprofen 400 heute vorrätig haben.','Hello, this is Amina Haddad''s AI assistant. I wanted to ask whether you have Ibuprofen 400 in stock today.','مرحبًا، أنا المساعدة الذكية لأمينة حداد. أردت أن أسأل إن كان لديكم إيبوبروفين 400 اليوم.'),
('00000000-0000-0000-0000-0000000000c2','practice','Ja, haben wir da. Sie kann es bis halb sieben abholen.','Yes, we have it. She can pick it up until half past six.','نعم، لدينا. يمكنها استلامه حتى السادسة والنصف.'),
('00000000-0000-0000-0000-0000000000c2','agent','Vielen Dank, dann sage ich ihr Bescheid. Auf Wiederhören.','Thank you, I will let her know. Goodbye.','شكرًا جزيلًا، سأخبرها. إلى اللقاء.');
