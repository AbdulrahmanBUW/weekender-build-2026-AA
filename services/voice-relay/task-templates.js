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
//   rules        extra German rules for this type
// h = helpers passed in by server.js: { reason, fact(key), party(), hasWindows }

const withWindows = (req, ...fns) => (req.time_windows?.length ? ['confirm_booking', ...fns] : fns.length ? fns : ['record_result']);

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
