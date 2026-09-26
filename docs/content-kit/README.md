# Adding providers and events from a spreadsheet

This kit lets you add Dresden family **providers** (courses, Kitas, libraries, playgrounds, family places, communities) and **events** to the app from a Google Sheet. You don't need to write any SQL.

It has two templates:

- `providers-template.csv`: one row per place, course or group
- `events-template.csv`: one row per dated event

Each template has 2 rows marked **EXAMPLE**. They show you how to fill things in. The script always skips them.

---

## One-time setup

1. **Google Sheet.** Create a sheet with two tabs, "Providers" and "Events". In each tab, go to *File → Import → Upload*, pick the matching template, and choose *Replace current sheet*. Keep the first row (the column names) exactly as it is.
2. **The computer that runs the script** needs:
   - **Python 3** from python.org. During install, tick "Add python.exe to PATH".
   - This project folder (`Weekender Build`).
   - For step 5 only (publishing): **Node.js** from nodejs.org, plus access to the live database. That access is set up once with `npx supabase login` and then `npx supabase link --project-ref ycyrtlzympxzlfcocazh`. If you don't have access, stop after step 4 and send your CSV to Abdul.

---

## Step by step

### 1. Fill in the sheet
- Use one row per provider or event, and delete the two EXAMPLE rows.
- For lists (languages, activity categories), separate the items with a semicolon, e.g. `de;en;ar`.
- Only a few columns are required (see the column guide below). You can leave the rest empty.
- Only add **public information about organisations and public events**. Never add private people's phone numbers, home addresses or names.

### 2. Download the tab as CSV
In Google Sheets, open the tab and go to *File → Download → Comma-separated values (.csv)*. This only downloads the tab that is open, so do it once for Providers and once for Events. The file lands in your Downloads folder.

### 3. Run the check
Open the `Weekender Build` folder in File Explorer. Right-click an empty spot and choose **Open in Terminal**. Then type:

```
python scripts/import_content.py "C:\Users\YOU\Downloads\Family hub - Providers.csv"
```

Tip: type `python scripts/import_content.py ` (with a space at the end), then drag the CSV file into the terminal window. That pastes its path for you. Press Enter.

If `python` isn't found, try `py` instead.

**Nothing changes in the app during this step.** The script only checks your rows and saves a `.import.sql` file next to your CSV.

### 4. Read the report
Every row gets one line:

| You see | Meaning | What to do |
|---|---|---|
| `OK` | Row is fine | Nothing |
| `OK (with warnings)` | Row is fine, but the script fixed something small (e.g. "German" became `de`, or it added `https://`) or something useful is missing (e.g. no description) | Read the warnings. You can continue. |
| `ERROR - not imported` | Something is wrong, and the message says what (e.g. age 25, unknown category, description too long) | Fix it in the Google Sheet, download the CSV again and run step 3 again |
| `SKIPPED (example row)` | An EXAMPLE row | Delete it from your sheet |

Repeat steps 2 to 4 until every row says OK.

### 5. Publish with `--apply`
Run the same command again with `--apply` at the end:

```
python scripts/import_content.py "C:\Users\YOU\Downloads\Family hub - Providers.csv" --apply
```

The script asks you to type `yes`, and then it writes your rows to the live database. It shows each row as `added` (new) or `updated` (it was already there). For events, `"provider_found": false` means the *Provider name* didn't exactly match any provider in the app. The event is still saved, just not linked to a provider.

If anything goes wrong, **nothing is saved**, because the whole file goes in as one step. Copy the output and send it to the team.

---

## Review and improve what is already in the app

The research agents have already filled the app with public places and events. The fastest way to make them better is to **review** them, not to type everything again.

1. **Get the review sheets.** They are in `docs/content-kit/review/`: `providers-review.csv` (every family place in the app) and `events-review.csv` (all upcoming events). To get a fresh copy of what is live right now, run:
   ```
   python scripts/export_review.py
   ```
2. **Open them in Google Sheets.** Make a new sheet, then go to *File → Import → Upload* and choose *Insert new sheet(s)*. Import each file once.
3. **Review row by row.** Use the two columns on the left:
   - **Review** empty or `ok`: the row is fine, and nothing happens to it.
   - **Review** `fix`: you changed something in this row. Correct any cell: a wrong phone number, missing ages, a better description, the translations in *Description (ru)*, *(uk)*, *(ar)* and so on. **Only rows marked `fix` are saved**, so always write `fix` when you change a row.
   - **Review** `remove`: the place is closed, wrong or not for families. Say why in **Review note**. It is **not** deleted automatically. The team checks it first.
   - **Review note**: anything for the team. It is never shown in the app.
4. **Add new places at the bottom** of the same sheet, and leave **ID** empty. Places from your own network are the most valuable part: the Russian-speaking music teacher, the Saturday school, the parent group.
5. **Never change the ID column.** It tells the script which entry to update. With an ID, you *can* change the name or address, and the same entry is updated.
6. **Download each tab as CSV and run the same check as above** (step 3), then `--apply` (step 5). The report shows `unchanged` for rows without `fix`. Rows marked `remove` go into a separate file ending in `.remove.sql` for the team.

Empty translation cells never delete a translation that is already there. Translations you write for one language never touch the other languages.

---

## Good to know

- **No duplicates.** If you import a provider with the same *Category + Name + Address* again, the existing entry is updated. The same goes for an event with the same *Title + Start time*. You can safely import the whole sheet again after adding new rows.
- **Changing a name, address or start time creates a new entry**, and the old one stays, unless the row has an **ID** (review sheets). Without an ID, tell the team so they can remove the old one.
- **An empty cell never deletes anything** that is already in the app. To remove information or a whole entry, ask the team.
- **Every entry needs a source link**, meaning a page where the information can be checked. For providers, the Website is used if the Source link is empty. For events, the Event link is used.
- **Notes:** if you leave Notes empty, the app automatically shows "Times, prices, age groups and languages can change: please check with the provider before you go."
- Everything you import is marked as added by the team (`source = manual`) and as a family entry (`audience = family`).

---

## Column guide: Providers

| Column | Required? | What to write |
|---|---|---|
| Category | **yes** | One of: `course`, `kita`, `school`, `library`, `playground`, `family_place`, `community` (also allowed: `doctor`, `pharmacy`, `bank`, `auslaenderbehoerde`, `other`) |
| Subcategory | no | A short word of your choice, e.g. `music`, `swimming`, `parent group` |
| Name | **yes** | Name of the place or course |
| Address | recommended | Street and number, postcode Dresden |
| District | no | e.g. `Neustadt`, `Südvorstadt`, `Pieschen` |
| Phone | no | Public phone number, e.g. `+49 351 1234567` |
| Website | no | `https://…` |
| Languages | recommended | Languages spoken or taught, as codes separated by `;` (see list below) |
| Activity categories | no | One or more of the activity list below, separated by `;` |
| Min age (years) / Max age (years) | no | Age range from 0 to 18. Use `0.5` for 6 months. |
| Price type | no | `free`, `per_session`, `subscription`, `trial_available` or `unknown` (empty means unknown) |
| Format | no | `recurring_course`, `workshop`, `one_off`, `community_group`, `place` or `service` |
| Opening hours | no | Free text, e.g. `Tue 10:00-10:45` |
| Description (English) | recommended | What families can expect, **max 600 characters** |
| Translations (JSON) | no | Leave empty. The team fills this in. |
| Source link | **yes** | Where you found or can check the information |
| Notes | no | Anything useful, e.g. "bring indoor shoes" |

## Column guide: Events

| Column | Required? | What to write |
|---|---|---|
| Title | **yes** | Max 160 characters |
| Starts at | **yes** | Dresden time, as `2026-10-17 10:00` or `17.10.2026 10:00`. A date with no time means an all-day event. |
| Ends at | no | Same format as Starts at. It can't be before the start. |
| All day | no | `yes` or `no`. If empty, the script decides from Starts at. |
| Place name | no | e.g. `Alaunpark`, `Städtische Bibliothek Neustadt` |
| Address, District | no | As for providers |
| Provider name | no | The exact **Name** of a provider already in the app. This links the event to it. |
| Min age (years) / Max age (years) | no | 0 to 18 |
| Languages | no | Codes separated by `;`. If empty, German (`de`) is used. |
| Activity categories | no | Same list as for providers |
| Price type | no | `free`, `paid` or `unknown` |
| Price text | no | e.g. `5 EUR per child` |
| Event link | recommended | The event's own page |
| Description (English) | recommended | Max 600 characters |
| Translations (JSON) | no | Leave empty |
| Source link | **yes** | Where the event is announced. If empty, the Event link is used. |

## Language codes

`de` German · `en` English · `ar` Arabic · `uk` Ukrainian · `ru` Russian · `tr` Turkish · `fa` Persian/Farsi · `prs` Dari · `pl` Polish · `vi` Vietnamese · `zh` Chinese · `es` Spanish · `fr` French · `hi` Hindi · `it` Italian · `ku` Kurdish · `cs` Czech · `gsg` German Sign Language

Any other 2-letter ISO language code works too. If you type a full name like `German` or `Arabisch`, it is converted automatically, and the report shows a warning when that happens.

## Activity categories

`music` · `dance` · `sport` · `yoga` · `art` · `languages` · `stem` (science, tech, maths) · `swimming` · `theatre` · `nature` · `parent_baby` (parent-and-baby classes) · `parent_meetup` · `library` · `school_kita` · `family_cafe` · `playground`

---

## For the team

- The script is `scripts/import_content.py` (Python 3, standard library only). Run it with `--help` to see all options (`--type`, `-o`, `--skip-errors`, `--yes`, `--include-examples`).
- The allowed values mirror `supabase/migrations/20260926200000_merged_family_hub.sql`. When that schema changes, update the lists at the top of the script.
- The generated SQL is **one statement**: one `INSERT … ON CONFLICT (dedupe_key) DO UPDATE` CTE per row, plus a final `SELECT` that reports added or updated for each row. The Supabase CLI rejects files with several commands, and a single statement is atomic.
- To test locally (never on the cloud DB), run:
  1. `python scripts/import_content.py docs/content-kit/providers-template.csv --include-examples -o x.import.sql`
  2. `npx supabase db query --local -f x.import.sql`
  3. Delete the rows again with `delete from public.resources where name like 'EXAMPLE - %';` (and the same on `family_events` by `title`).

  `--include-examples` together with `--apply` is refused.
- `*.import.sql` files are git-ignored.
