// Task templates: ONE object per call_requests.task_type. Add a new task type here only.
// Fields:
//   label        English name (logs / test page)
//   mode         'appointment' (agree to a slot inside the windows) | 'information' (collect an answer)
//   purposeDe    (req, h) => German clause that ends the greeting: "... und <purposeDe>."
//   goalDe       (req, h) => German fallback goal when n8n has not written goal_de yet
//   useDoctorFields  include reason/insurance/new-patient/referral facts (doctor only)
//   functions    (req) => which agent functions apply ('confirm_booking','record_result'; needs_user + end_call are always added)
//   success      outcome that counts as success ('booked' | 'completed')
//   resultType   default record_result.result_type for this task
//   resultHint   what record_result.details should contain (English, for the function description)
//   rules        extra German rules for this type: string[] or (req, h) => string[]
//                placeholders: {reason} (doctor reason), {person} (how to refer to the person: sie/er/Frau X/name)
//   bookingKind  optional: what confirm_booking books (e.g. 'trial_lesson'); stored in calls.result.booking_kind
//   bookingDetails  true = confirm_booking also takes `details` (same keys as resultHint), so ONE call records
//                the booked slot plus everything else the other side said (places, waiting list, price…)
//   keyterms     optional German words that help speech recognition for this task type
// h = helpers passed in by server.js: { reason, fact(key), party(), hasWindows }

const withWindows = (req, ...fns) => (req.time_windows?.length ? ['confirm_booking', ...fns] : fns.length ? fns : ['record_result']);

// ---------- helpers for the family task types (course_enquiry, kita_enquiry) ----------
// Facts come from the intake (n8n 04) as {key, label, value}; key names can vary a little, so look up by list + regex.
function factBy(req, h, keys, re) {
  for (const k of keys) { const v = h.fact(k); if (v) return v; }
  const list = Array.isArray(req.allowed_facts) ? req.allowed_facts : [];
  const f = re && list.find(x => x && x.value != null && String(x.value).trim() && re.test(String(x.key || '').toLowerCase()));
  return f ? String(f.value).replace(/\s+/g, ' ').trim().slice(0, 80) : '';
}

const NUM_DE = ['null', 'ein', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun', 'zehn', 'elf', 'zwölf',
  'dreizehn', 'vierzehn', 'fünfzehn', 'sechzehn', 'siebzehn', 'achtzehn'];
const MONTHS_DE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
const MONTH_PREFIX = { jan: 0, feb: 1, mar: 2, mär: 2, mae: 2, apr: 3, may: 4, mai: 4, jun: 5, jul: 6, aug: 7, sep: 8, oct: 9, okt: 9, nov: 10, dec: 11, dez: 11 };

// "6", "6 Jahre", "6 years", "sechs", "2,5 Jahre", "18 Monate" -> { years, half? } | { months } | { raw } | null
// NOTE: never match "language" (contains "age") — the regex below only takes age/alter as a whole key part.
const AGE_KEY_RE = /(^|_)(age|alter)(_|$)|child_?age|kind_?alter/;
const AGE_WORDS = { eins: 1, ein: 1, eine: 1, zwei: 2, drei: 3, vier: 4, 'fünf': 5, sechs: 6, sieben: 7, acht: 8, neun: 9, zehn: 10, elf: 11, 'zwölf': 12,
  one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12 };
function childAge(req, h) {
  const raw = factBy(req, h, ['child_age', 'child_age_years', 'age', 'kid_age', 'alter', 'alter_kind'], AGE_KEY_RE);
  if (!raw) return null;
  const s = raw.toLowerCase();
  const m = /(\d{1,2})(?:[.,](\d))?/.exec(s);
  const word = (s.match(/[a-zäöüß]+/g) || []).map(w => AGE_WORDS[w]).find(Boolean);
  const n = m ? Number(m[1]) : word || null;
  if (n == null) return { raw };
  if (/monat|month/.test(s) && !/jahr|year/.test(s)) return { months: n, raw };
  if (n < 1 || n > 18) return { raw };
  return { years: n, half: m?.[2] === '5', raw };
}
const ageWord = a => `${NUM_DE[a.years]}${a.half ? 'einhalb' : ''}`;   // "sechs", "zweieinhalb", "eineinhalb"

// "2027-02", "02/2027", "Februar 2027", "from February", "feb" -> "Februar 2027" / "Februar"; else the raw text
function monthDe(value) {
  const s = String(value || '').replace(/\s+/g, ' ').trim();
  if (!s) return '';
  let m = /^(\d{4})-(\d{1,2})/.exec(s);
  if (m && +m[2] >= 1 && +m[2] <= 12) return `${MONTHS_DE[+m[2] - 1]} ${m[1]}`;
  m = /^(?:\d{1,2}\.)?(\d{1,2})[./](\d{4})$/.exec(s);   // 02/2027, 2.2027, 14.05.2024 (day dropped on purpose)
  if (m && +m[1] >= 1 && +m[1] <= 12) return `${MONTHS_DE[+m[1] - 1]} ${m[2]}`;
  const year = /\b(20\d{2})\b/.exec(s)?.[1];
  for (const w of s.toLowerCase().match(/[a-zäöü]{3,}/g) || []) {
    const i = MONTH_PREFIX[w.slice(0, 3)];
    if (i !== undefined) return `${MONTHS_DE[i]}${year ? ` ${year}` : ''}`;
  }
  return s.replace(/^(ab|from)\s+/i, '').slice(0, 40);   // "ab sofort" -> "sofort": the clause already says "ab …"
}

const startMonth = (req, h) => monthDe(factBy(req, h, ['start_month', 'desired_start', 'start_date', 'from_month', 'startmonat'], /start|beginn|from_month|ab_wann/)
  || (req.constraints && typeof req.constraints === 'object' ? req.constraints.start_month || '' : ''));
const birthOf = (req, h) => factBy(req, h, ['child_birth', 'child_birth_month', 'birth_month', 'child_dob', 'geburtsmonat'], /birth|geburt|dob/);
const cap = s => s.charAt(0).toUpperCase() + s.slice(1);

// course: "für Sechsjährige" / "für Kinder von 18 Monaten" / ''
function courseAudience(req, h) {
  const a = childAge(req, h);
  if (!a) return '';
  if (a.years) return `für ${cap(ageWord(a))}jährige`;
  if (a.months) return `für Kinder von ${a.months} Monaten`;
  return '';   // unclear text (e.g. "Kleinkind"): leave it out of the greeting; it is still in FAKTEN
}
// kita: "ein zweijähriges Kind" / "ein Kind von 14 Monaten" / "ein im Mai 2024 geborenes Kind" / "ein Kind"
function kitaChild(req, h) {
  const a = childAge(req, h);
  if (a?.years) return `ein ${ageWord(a)}jähriges Kind`;
  if (a?.months) return `ein Kind von ${a.months} Monaten`;
  const b = birthOf(req, h);
  return b ? `ein im ${monthDe(b)} geborenes Kind` : 'ein Kind';
}

export const REASON_DE = {
  first_visit: 'Erstuntersuchung', checkup: 'Vorsorgeuntersuchung', acute: 'Akuttermin',
  follow_up: 'Folgetermin', specialist: 'Facharzttermin', other: 'Termin'
};

export const TASK_TEMPLATES = {
  doctor_appointment: {
    label: 'Doctor appointment',
    mode: 'appointment',
    purposeDe: (req, h) => `hätte gern einen Termin für eine ${h.reason}`,
    goalDe: (req, h) => `Einen Termin für eine ${h.reason} in der Praxis vereinbaren.`,
    useDoctorFields: true,
    functions: () => ['confirm_booking'],
    success: 'booked',
    rules: [
      'Nenne niemals Symptome oder Diagnosen. Wenn gefragt: "Es geht um eine {reason}, weitere Details bespricht die Person gern selbst."',
      'Wenn keine Neupatienten angenommen werden: bedanke dich und rufe end_call mit outcome "rejected_no_new_patients" auf.'
    ]
  },
  authority_appointment: {
    label: 'Authority appointment',
    mode: 'appointment',
    purposeDe: () => 'möchte gern einen Termin vereinbaren',
    goalDe: () => 'Einen Termin bei der Behörde vereinbaren.',
    functions: req => withWindows(req, 'record_result'),
    success: 'booked',
    resultType: 'how_to_book',
    resultHint: 'how to book instead (online portal, walk-in hours, documents to bring)',
    rules: [
      'Wenn am Telefon kein Termin vergeben wird: frag, wie man einen Termin bekommt (Online-Portal, offene Sprechstunde, mitzubringende Unterlagen) und rufe record_result mit result_type "how_to_book" auf.',
      'Keine Angaben zu Staatsangehörigkeit oder Aufenthaltsstatus, außer sie stehen in den FAKTEN.'
    ]
  },
  landlord_request: {
    label: 'Landlord / property management',
    mode: 'appointment',
    purposeDe: () => 'möchte gern ein Problem in der Wohnung melden',
    goalDe: () => 'Ein Problem in der Wohnung melden und einen Termin für die Reparatur vereinbaren.',
    functions: req => withWindows(req, 'record_result'),
    success: 'booked',
    resultType: 'reported',
    resultHint: 'ticket/reference number, who will come, next step',
    rules: [
      'Vereinbare nur einen Besichtigungs- oder Reparaturtermin innerhalb der Zeitfenster. Sprich niemals über Miete, Mieterhöhung, Kündigung oder Vertragsänderungen.',
      'Wenn kein Termin genannt wird, sondern ein Rückruf oder eine Vorgangsnummer: rufe record_result mit result_type "reported" auf.'
    ]
  },
  contract_question: {
    label: 'Contract question',
    mode: 'information',
    purposeDe: () => 'hätte eine kurze Frage zu einem Vertrag',
    goalDe: () => 'Informationen zum Vertrag einholen, zum Beispiel wie und bis wann man kündigen kann.',
    functions: () => ['record_result'],
    success: 'completed',
    resultType: 'contract_info',
    resultHint: 'how to cancel, notice period/deadline, where to send it (address, email, portal), form required',
    rules: [
      'NUR Informationen einholen. Du kündigst, bestellst oder bestätigst am Telefon niemals etwas und stimmst keinem Vertrag zu. Wenn man dir eine Kündigung am Telefon anbietet: "Danke, sie macht das lieber schriftlich. Wohin soll sie die Kündigung schicken?"'
    ]
  },
  bank_enquiry: {
    label: 'Bank enquiry',
    mode: 'appointment',
    purposeDe: () => 'möchte gern einen Beratungstermin vereinbaren',
    goalDe: () => 'Einen Termin in der Filiale vereinbaren oder erfragen, welche Unterlagen nötig sind.',
    functions: req => withWindows(req, 'record_result'),
    success: 'booked',
    resultType: 'documents',
    resultHint: 'documents needed, opening hours, how to book',
    rules: [
      'Nenne niemals vollständige Kontonummern, PINs oder Passwörter. Kundennummern höchstens so, wie sie in den FAKTEN stehen.',
      'Wenn kein Termin möglich ist, frage nach den nötigen Unterlagen und rufe record_result mit result_type "documents" auf.'
    ]
  },
  pharmacy_question: {
    label: 'Pharmacy question',
    mode: 'information',
    purposeDe: (req, h) => (h.fact('medicine') ? `wollte fragen, ob Sie ${h.fact('medicine')} vorrätig haben` : 'hätte eine kurze Frage zu einem Medikament'),
    goalDe: (req, h) => `Nachfragen, ob ${h.fact('medicine') || 'das Medikament'} vorrätig ist und bis wann man es abholen kann.`,
    functions: () => ['record_result'],
    success: 'completed',
    resultType: 'stock_check',
    resultHint: 'in_stock (boolean), pickup_until (HH:MM), price_eur (number), can_reserve (boolean), alternative (string)',
    rules: [
      'Frag nur nach Verfügbarkeit, Abholung, Reservierung und Preis. Du gibst und erbittest keine medizinische Beratung und nennst keinen Grund, warum das Medikament gebraucht wird.',
      'Wenn es nicht vorrätig ist: frag, ob man es bestellen kann und ab wann es da ist.'
    ]
  },
  restaurant_booking: {
    label: 'Restaurant booking',
    mode: 'appointment',
    purposeDe: (req, h) => `möchte gern einen Tisch${h.party() ? ` für ${h.party()} Personen` : ''} reservieren`,
    goalDe: (req, h) => `Einen Tisch${h.party() ? ` für ${h.party()} Personen` : ''} reservieren.`,
    functions: () => ['confirm_booking'],
    success: 'booked',
    rules: [
      'Die Personenzahl ist fest (siehe RAHMEN). Reserviere auf den Namen der Person.',
      'Wenn nichts im Zeitfenster frei ist: bedanke dich und rufe end_call mit outcome "rejected" auf.'
    ]
  },
  course_enquiry: {
    label: "Kids' course enquiry",
    mode: 'appointment',
    purposeDe: (req, h) => {
      const aud = courseAudience(req, h);
      return aud ? `wollte fragen, ob es in Ihrem Kurs ${aud} noch einen Platz oder eine Probestunde gibt`
        : 'wollte fragen, ob es in Ihrem Kurs noch einen Platz oder eine Probestunde für ein Kind gibt';
    },
    goalDe: (req, h) => {
      const a = childAge(req, h);
      const kid = a?.years ? `ein Kind von ${a.years === 1 && !a.half ? 'einem Jahr' : `${ageWord(a)} Jahren`}` : a?.months ? `ein Kind von ${a.months} Monaten` : 'ein Kind';
      return `Für ${kid} beim Kursanbieter nachfragen: Gibt es einen freien Platz oder eine Probestunde, sonst eine Warteliste? Dazu Kurszeiten, Preis und Unterrichtssprache erfragen.${h.hasWindows ? ' Eine Probestunde nur innerhalb der Zeitfenster zusagen.' : ''}`;
    },
    functions: req => withWindows(req, 'record_result'),
    success: 'booked',
    bookingKind: 'trial_lesson',
    bookingDetails: true,
    resultType: 'course_availability',
    resultHint: 'free_spot (true/false), trial_lesson (true/false), trial_slot_text, waiting_list (true/false), schedule_text, price_text, language_of_instruction, next_steps — booleans only if clearly said',
    keyterms: ['Probestunde', 'Schnupperstunde', 'Warteliste', 'Kurs'],
    rules: (req, h) => [
      'Frag nacheinander, immer nur eine Frage: Ist ein Platz frei? Ist eine Probestunde (Schnupperstunde) möglich? Wenn nicht: Gibt es eine Warteliste? Dann – falls noch nicht gesagt – Kurszeiten, Preis und Unterrichtssprache.',
      factBy(req, h, ['language_preference', 'preferred_language', 'wunschsprache', 'language'], /lang|sprache/)
        ? 'In den FAKTEN steht eine Wunschsprache: frag, ob der Kurs auch in dieser Sprache oder zweisprachig möglich ist.'
        : 'Frag, in welcher Sprache unterrichtet wird.',
      h.hasWindows
        ? 'Eine Probestunde sagst du NUR innerhalb der Zeitfenster zu. Liegt das Angebot außerhalb, frag nach einem anderen Termin. Passt ein Angebot: frag zuerst noch offene Punkte (Preis, Unterrichtssprache), dann Wochentag, Datum und Uhrzeit wiederholen und auf "Ja"/"Richtig" warten. Danach sagst du kurz "Wunderbar, ich notiere das." und rufst sofort confirm_booking auf – was mitzubringen ist (z. B. Sportsachen, Hausschuhe) in bring_items, alle weiteren Antworten (Platz, Warteliste, Kurszeiten, Preis, Sprache) in details. Nach confirm_booking KEIN record_result.'
        : 'Du sagst keinen Termin zu (es gibt keine Zeitfenster): notiere angebotene Probestunden als trial_slot_text.',
      'Gibt es keine passende Probestunde: fasse die Antworten zusammen und warte auf "Ja"/"Richtig". Danach sagst du kurz "Danke, ich notiere das." und rufst im selben Zug record_result mit result_type "course_availability" auf. free_spot, trial_lesson und waiting_list nur als true/false, wenn es klar gesagt wurde; alles andere als kurzer Text.',   // DEF-025 (closing turn of record_result)
      'free_spot (in details und record_result) nur, wenn ausdrücklich gesagt wurde, ob ein Platz frei ist. Ein "Ja, gern" vor einer Rückfrage ist keine Antwort, und eine angebotene Probestunde heißt NICHT, dass ein Platz frei ist – dann free_spot weglassen.',   // DEF-028
      'waiting_list nur, wenn die Frage nach der Warteliste selbst beantwortet wurde. "Kein Platz frei" oder "unter der Woche ist alles voll" heißt NICHT "keine Warteliste": dann noch einmal nach der Warteliste fragen oder waiting_list weglassen – und nichts Ungesagtes in die Zusammenfassung schreiben.',   // DEF-028 (RUN-016 verification)
      'Du meldest das Kind nicht verbindlich an, unterschreibst nichts und stimmst keinem Vertrag und keiner Zahlung zu. Wird eine feste Anmeldung oder ein Eintrag auf die Warteliste angeboten: "Danke, das macht {person} gern selbst. Wie geht das am besten?" und notiere es als next_steps.',
      'Vom Kind nennst du nur, was in den FAKTEN steht (z. B. das Alter). Sag "das Kind" oder den Vornamen aus den FAKTEN – "Tochter"/"Sohn" nur, wenn es in FAKTEN oder AUFGABE steht (nie aus dem Vornamen raten). Niemals Gesundheit, Allergien, Entwicklung oder Förderbedarf des Kindes. Wird danach gefragt: "Das bespricht {person} gern selbst mit Ihnen."'
    ]
  },
  kita_enquiry: {
    label: 'Kita place enquiry',
    mode: 'appointment',
    purposeDe: (req, h) => {
      const from = startMonth(req, h);
      return `wollte fragen, ob Sie${from ? ` ab ${from}` : ''} einen Betreuungsplatz für ${kitaChild(req, h)} haben und wie man auf die Warteliste kommt`;
    },
    goalDe: (req, h) => {
      const from = startMonth(req, h);
      return `Bei der Kita nachfragen, ob${from ? ` ab ${from}` : ''} ein Betreuungsplatz für ${kitaChild(req, h)} frei ist, wie man auf die Warteliste kommt bzw. wie die Plätze vergeben werden, und ob man die Kita besichtigen kann (Besichtigungstermin oder Tag der offenen Tür).${h.hasWindows ? ' Einen Besichtigungstermin nur innerhalb der Zeitfenster zusagen.' : ''}`;
    },
    functions: req => withWindows(req, 'record_result'),
    success: 'booked',
    bookingKind: 'kita_visit',
    bookingDetails: true,
    resultType: 'kita_availability',
    resultHint: 'places_available (true/false), from_month, waiting_list_possible (true/false), how_to_apply, visit_possible (true/false), visit_text, languages, next_steps — booleans only if clearly said',
    keyterms: ['Betreuungsplatz', 'Warteliste', 'Kita-Portal', 'Besichtigung'],
    rules: (req, h) => [
      `Reihenfolge, immer nur eine Frage: 1. Gibt es ab dem Wunschmonat einen Platz (sonst ab wann)? 2. Wie kommt man auf die Warteliste bzw. wie werden die Plätze vergeben? ${factBy(req, h, ['language_preference', 'preferred_language', 'wunschsprache', 'language'], /lang|sprache/) ? '3. Welche Sprachen werden im Kita-Alltag gesprochen (Wunschsprache siehe FAKTEN)? 4.' : '3.'} Zuletzt: Kann man die Kita besichtigen?`,
      'Du meldest das Kind am Telefon NICHT an, unterschreibst nichts und nimmst keinen Platz verbindlich an. Behaupte nie, dass eine Anmeldung erledigt ist. In Dresden läuft die Anmeldung meist über das Online-Portal der Stadt – erkläre das aber nicht der Kita, sondern frag, wie es bei ihnen läuft, und notiere die Antwort (how_to_apply).',
      h.hasWindows
        ? 'Einen Besichtigungstermin (oder Tag der offenen Tür) sagst du NUR innerhalb der Zeitfenster zu. Vor der Zusage: Wochentag, Datum und Uhrzeit wiederholen und auf "Ja"/"Richtig" warten. Danach sagst du kurz "Wunderbar, ich notiere das." und rufst sofort confirm_booking auf – alle anderen Antworten (Plätze, ab wann, Warteliste, Anmeldung, Sprachen) in details. Nach confirm_booking KEIN record_result. Liegt der Termin außerhalb, frag nach einer Alternative oder notiere ihn als visit_text.'
        : 'Du sagst keinen Termin zu (es gibt keine Zeitfenster): notiere Besichtigungstermine als visit_text.',
      'Gibt es keinen Besichtigungstermin im Zeitfenster: fasse die Antworten zusammen und warte auf "Ja"/"Richtig". Danach sagst du kurz "Danke, ich notiere das." und rufst im selben Zug record_result mit result_type "kita_availability" auf. places_available, waiting_list_possible und visit_possible nur als true/false, wenn es klar gesagt wurde; alles andere als kurzer Text. Eine mögliche Besichtigung heißt NICHT, dass ein Platz frei ist, und "kein Platz frei" heißt NICHT "keine Warteliste".',   // DEF-025 + DEF-028
      'Vom Kind nennst du nur, was in den FAKTEN steht (Alter oder Geburtsmonat, Wunschmonat). Sag "das Kind" oder den Vornamen aus den FAKTEN – "Tochter"/"Sohn" nur, wenn es in FAKTEN oder AUFGABE steht. Niemals Gesundheit, Allergien, Entwicklung, Förderbedarf oder Integrationsplatz. Wird danach gefragt: "Das bespricht {person} gern selbst mit Ihnen."'
    ]
  },
  other_call: {
    label: 'Other call',
    mode: 'information',
    purposeDe: () => 'hätte eine kurze Frage',
    goalDe: () => 'Die Frage klären und die Antwort notieren.',
    functions: req => withWindows(req, 'record_result'),
    success: 'completed',
    resultType: 'answer',
    resultHint: 'the answer to the question, as key/value pairs',
    rules: []
  }
};

export function templateFor(taskType) {
  return TASK_TEMPLATES[taskType] || TASK_TEMPLATES.other_call;
}
