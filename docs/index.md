# Clinical Trial Operations Dashboard — Complete Power BI Build Guide

**What you are building:** a portfolio-grade, 5-page clinical trial operations dashboard in Power BI Desktop, driven by synthetic (fake) trial data. Every measure, relationship, and visual below is specified exactly — click-by-click steps and copy-paste DAX. No real patient data is used anywhere.

**▶ Live interactive preview (same data, works in your browser):** [Live dashboard](live.html) — slicers and tabs included, no Power BI needed. Use it to see the finished numbers before you build, or to sanity-check your .pbix against it.

**Skill level:** beginner-to-intermediate. You should already know how to open Power BI Desktop and drag a field onto a visual. Everything else is spelled out.

---

## Clinical terms, explained once (used throughout)

- **EDC (Electronic Data Capture):** the software system sites use to type trial data into electronic forms. Think "the trial's database app."
- **eCRF (electronic Case Report Form):** one electronic form inside the EDC for one subject's data — e.g., a Vital Signs form for subject SUB-0001's Week 4 visit.
- **Query:** a question the data management team raises inside the EDC when data looks wrong, missing, or inconsistent (e.g., "Systolic BP value appears out of range"). The site must answer it; until then the query is *open*.
- **Adverse Event (AE):** any unfavorable medical occurrence in a subject after enrollment (headache, nausea, etc.), whether or not the study drug caused it.
- **SAE (Serious Adverse Event):** an AE that is life-threatening, causes hospitalization, disability, or death. SAEs get expedited reporting to regulators and the sponsor.
- **Protocol deviation:** any departure from the approved study protocol (missed visit window, wrong dose, missed lab). *Major* deviations can affect subject safety or data integrity and are tracked aggressively.
- **CDASH:** the CDISC standard for how eCRF fields are designed and named at data *collection* time.
- **SDTM:** the CDISC standard for organizing collected data into analysis-ready *tabulation* datasets (e.g., one dataset per domain: demographics, AEs).
- **ADaM:** the CDISC standard for *analysis* datasets derived from SDTM, used by statisticians to produce tables/figures. (Your dashboard operates at the EDC/operations level, upstream of SDTM/ADaM — worth one line in a portfolio README.)

---

## Before you start — the data files

Use the seven synthetic CSVs that accompany this guide (folder: `clinical-trial-dashboard/data/`):

| File | Rows | What it is |
|---|---|---|
| Sites.csv | 12 | One row per clinical trial site |
| Subjects.csv | 549 | One row per screened subject |
| Visits.csv | 3,075 | One row per subject visit |
| Forms.csv | 16,254 | One row per eCRF (all expected forms, completed or missing) |
| Queries.csv | 1,620 | One row per EDC data query |
| AdverseEvents.csv | 316 | One row per adverse event |
| Deviations.csv | 158 | One row per protocol deviation |

### Data dictionary (columns you will actually use)

**Sites** — `SiteID` (S01–S12), `SiteName`, `Country`, `Region`, `PrincipalInvestigator` (fake names), `SiteStatus`, `ActivationDate`, `EnrollmentTarget` (40 per site).

**Subjects** — `SubjectID` (SUB-0001…), `SiteID` (→ Sites), `ScreenDate`, `RandomizationDate` (blank if never randomized), `Status` (`Screen Failure`, `Screened`, `Randomized`, `Completed`, `Withdrawn`), `AgeGroup`, `Sex`, `TreatmentArm` (blank until randomized).

**Visits** — `VisitID`, `SubjectID` (→ Subjects), `VisitName` (Screening, Baseline, Week 2/4/8/12/24), `PlannedDate`, `ActualDate` (blank if not done), `VisitStatus` (`Completed`, `Overdue`, `Missed`, `Scheduled`), `WindowStatus` (`In Window` / `Out of Window` / blank).

**Forms** — `FormID`, `SubjectID` (→ Subjects), `VisitName`, `FormName` (Demographics, Vital Signs, Laboratory Results, ECG, Concomitant Medications, Efficacy Assessment), `FormStatus` (`Completed` / `Missing`), `DueDate`, `CompletionDate` (blank while missing).

**Queries** — `QueryID`, `SubjectID` (→ Subjects), `FormName`, `QueryText`, `QueryOpenDate`, `QueryCloseDate` (blank while open), `QueryStatus` (`Open`, `Answered`, `Closed`).

**AdverseEvents** — `AEID`, `SubjectID` (→ Subjects), `AETerm`, `StartDate`, `SeverityGrade` (CTCAE 1–5), `Serious` (`Yes` = SAE / `No`), `Outcome`, `RelatedToStudyDrug`.

**Deviations** — `DeviationID`, `SubjectID` (→ Subjects), `DeviationDate`, `Category`, `Severity` (`Major` / `Minor`), `DeviationStatus` (`Open` / `Closed`).

---

## Part 1 — Import the CSVs into Power BI Desktop

Do this for **each of the seven files**:

1. Open Power BI Desktop → **Home** tab → **Get data** → **Text/CSV**.
2. Browse to the CSV (start with `Sites.csv`) → **Open**.
3. In the preview window, confirm the delimiter shows **Comma** and the first row is detected as headers. Click **Load** (not Transform — the synthetic data is already clean).
4. Repeat for `Subjects.csv`, `Visits.csv`, `Forms.csv`, `Queries.csv`, `AdverseEvents.csv`, `Deviations.csv`.

**Verify data types** (do this once, right after loading):

5. Click the **Data view** icon (table icon, left rail) → select **Subjects**. Confirm: `ScreenDate` and `RandomizationDate` show a calendar icon (Date type). If they show `ABC` (text), select the column → **Column tools** tab → **Data type** → **Date**.
6. Check these type assignments across all tables:
   - All `*Date` columns → **Date**
   - `SeverityGrade` (AdverseEvents), `EnrollmentTarget` (Sites) → **Whole number**
   - Everything else → **Text**
7. In Queries, confirm `QueryCloseDate` blanks load as empty (blank is correct for open queries — do not fill them).

**Name check:** In the Fields pane (Report view), tables must be named exactly `Sites`, `Subjects`, `Visits`, `Forms`, `Queries`, `AdverseEvents`, `Deviations`. If Power BI imported a table with a different name, right-click it → **Rename**.

---

## Part 2 — Build the star schema

Go to **Model view** (third icon, left rail). Power BI may have auto-created relationships — delete any it created automatically first (right-click a relationship line → **Delete**) so the model is exactly as specified.

### Create these six relationships

Create each by **dragging** the source column onto the target column (or **Modeling** tab → **Manage relationships** → **New**):

| # | From (many side) | To (one side) | Cardinality | Cross-filter |
|---|---|---|---|---|
| 1 | Subjects[SiteID] | Sites[SiteID] | Many-to-one (*:1) | Single |
| 2 | Visits[SubjectID] | Subjects[SubjectID] | Many-to-one (*:1) | Single |
| 3 | Forms[SubjectID] | Subjects[SubjectID] | Many-to-one (*:1) | Single |
| 4 | Queries[SubjectID] | Subjects[SubjectID] | Many-to-one (*:1) | Single |
| 5 | AdverseEvents[SubjectID] | Subjects[SubjectID] | Many-to-one (*:1) | Single |
| 6 | Deviations[SubjectID] | Subjects[SubjectID] | Many-to-one (*:1) | Single |

Sites and Subjects form the "spine": Sites → Subjects → everything else. Every fact table (Visits, Forms, Queries, AEs, Deviations) filters through Subjects, which filters through Sites. Leave cross-filter direction on **Single** everywhere — do not use bidirectional here.

### Create the Calendar table

1. **Modeling** tab → **New table**.
2. Paste this DAX and press Enter:

```DAX
Calendar =
VAR MinDate = DATE ( 2025, 1, 1 )
VAR MaxDate = TODAY ()
RETURN
ADDCOLUMNS (
    CALENDAR ( MinDate, MaxDate ),
    "Year", YEAR ( [Date] ),
    "MonthNumber", MONTH ( [Date] ),
    "Month", FORMAT ( [Date], "MMM" ),
    "MonthYear", FORMAT ( [Date], "MMM YYYY" ),
    "YearMonthSort", YEAR ( [Date] ) * 100 + MONTH ( [Date] ),
    "Quarter", "Q" & FORMAT ( [Date], "Q" ),
    "Weekday", FORMAT ( [Date], "ddd" )
)
```

3. Right-click **Calendar** → **Mark as date table** → select the `Date` column → OK.
4. Select the `MonthYear` column → **Column tools** → **Sort by column** → `YearMonthSort`. (This is what makes Jan→Dec chart axes sort chronologically instead of alphabetically.)

### Connect the Calendar

Drag `Calendar[Date]` onto `Subjects[RandomizationDate]`, cardinality Many-to-one from Subjects to Calendar (Subjects is many, Calendar is one), cross-filter Single, **"Make this relationship active" checked** → this powers the enrollment trend.

Then create two **inactive** relationships for the other date lenses (you will use them in measures with USERELATIONSHIP — DAX that temporarily activates a relationship for one calculation):

- Drag `Calendar[Date]` → `Subjects[ScreenDate]` → in the dialog, **uncheck** "Make this relationship active" → OK.
- Drag `Calendar[Date]` → `Queries[QueryOpenDate]` → leave it active if Power BI insists on one; actually make Queries relationship **inactive too** (uncheck active). Queries still join to Subjects normally for site filtering; the Calendar link is only for trend charts.

Your model should now show: Sites → Subjects → 5 fact tables, plus Calendar connected to Subjects (1 active + 1 inactive) and Queries (inactive).

**Layout tip:** In Model view, drag Sites top-center, Subjects directly under it, the five fact tables in a row beneath Subjects, Calendar to the left of Subjects. Portfolio reviewers notice a tidy model.

---

## Part 3 — DAX measures (exact code)

Create a dedicated measure table first so all measures live in one place:

1. **Modeling** tab → **New table** → type `Measures = {0}` → Enter. (A dummy 1-row table that exists only to hold measures.)
2. For each measure below: right-click the **Measures** table → **New measure** → replace the formula with the exact DAX → Enter.
3. After creating each measure, set its format: select the measure → **Measure tools** tab → set **Format** (each measure below notes its format).

```DAX
Total Subjects =
COUNTROWS ( Subjects )
```
Format: Whole number.

```DAX
Randomized Subjects =
CALCULATE (
    COUNTROWS ( Subjects ),
    NOT ( ISBLANK ( Subjects[RandomizationDate] ) )
)
```
Format: Whole number.

```DAX
Screen Failures =
CALCULATE (
    COUNTROWS ( Subjects ),
    Subjects[Status] = "Screen Failure"
)
```
Format: Whole number.

```DAX
Screened Subjects =
CALCULATE (
    COUNTROWS ( Subjects ),
    NOT ( ISBLANK ( Subjects[ScreenDate] ) )
)
```
Format: Whole number. (Supporting measure — every subject in this dataset has a ScreenDate, so this equals Total Subjects; it is the correct screening denominator.)

```DAX
Screen Failure Rate =
DIVIDE ( [Screen Failures], [Screened Subjects] )
```
Format: Percentage, 1 decimal place.

```DAX
Enrollment Target =
SUM ( Sites[EnrollmentTarget] )
```
Format: Whole number. (This reads the target from Sites — 40 per site × 12 sites = 480. Filters still work: if you slice to 3 sites, the target correctly shows 120.)

```DAX
Enrollment Achievement % =
DIVIDE ( [Randomized Subjects], [Enrollment Target] )
```
Format: Percentage, 1 decimal place.

```DAX
Open Queries =
CALCULATE (
    COUNTROWS ( Queries ),
    Queries[QueryStatus] = "Open"
)
```
Format: Whole number.

```DAX
Average Open Query Age =
AVERAGEX (
    FILTER ( Queries, Queries[QueryStatus] = "Open" ),
    DATEDIFF ( Queries[QueryOpenDate], TODAY (), DAY )
)
```
Format: Decimal number, 1 decimal place. Shows days. (DATEDIFF counts whole days between the date the data-cleaning query was opened and today.)

```DAX
Overdue Visits =
CALCULATE (
    COUNTROWS ( Visits ),
    Visits[VisitStatus] = "Overdue"
)
```
Format: Whole number.

```DAX
Missing Forms =
CALCULATE (
    COUNTROWS ( Forms ),
    Forms[FormStatus] = "Missing"
)
```
Format: Whole number.

```DAX
Completed Forms =
CALCULATE (
    COUNTROWS ( Forms ),
    Forms[FormStatus] = "Completed"
)
```
Format: Whole number. (Supporting measure for the completion rate.)

```DAX
Form Completion % =
DIVIDE ( [Completed Forms], COUNTROWS ( Forms ) )
```
Format: Percentage, 1 decimal place.

```DAX
Total AEs =
COUNTROWS ( AdverseEvents )
```
Format: Whole number.

```DAX
Total SAEs =
CALCULATE (
    COUNTROWS ( AdverseEvents ),
    AdverseEvents[Serious] = "Yes"
)
```
Format: Whole number.

```DAX
Open Major Deviations =
CALCULATE (
    COUNTROWS ( Deviations ),
    Deviations[Severity] = "Major",
    Deviations[DeviationStatus] = "Open"
)
```
Format: Whole number.

### Two helper items (create both — pages use them)

**Calculated column** on the Queries table (Data view → Queries → **Table tools** → **New column**):

```DAX
Age Bucket =
VAR Age = DATEDIFF ( Queries[QueryOpenDate], TODAY (), DAY )
RETURN
SWITCH (
    TRUE (),
    Queries[QueryStatus] <> "Open", "Closed/Answered",
    Age <= 7, "0-7 days",
    Age <= 14, "8-14 days",
    Age <= 30, "15-30 days",
    "30+ days"
)
```

**Ordering for Age Bucket:** select the Age Bucket column → Column tools → **Sort by column** → you need a numeric helper; simplest fix: accept text sort but rename buckets `1) 0-7 days`, `2) 8-14 days`, `3) 15-30 days`, `4) 30+ days`, `5) Closed/Answered` in the SWITCH above. Do that rename if sorted order matters to you (recommended for the chart).

**Site risk flag measure** (in the Measures table):

```DAX
Site Risk =
IF (
    [Screen Failure Rate] > 0.30
        || [Open Queries] > 25
        || [Overdue Visits] > 10
        || [Open Major Deviations] > 2,
    "High",
    "Normal"
)
```
Format: Text (General). This returns "High" for any site breaching a risk threshold, evaluated in the current filter context — so in a per-site matrix row it flags that row's site.

---

## Part 4 — Build the five report pages

### Global page setup (do once, applies everywhere)

- **Page size:** View tab → Page view → Fit to page. Each page: right-click canvas → **Page information** / Format page → Canvas settings → Type **16:9** (1280 × 720).
- **Background:** Format page → Canvas background → Color `#F4F6F8`, Transparency 0%.
- **Header band (build once, then copy to every page):** Insert → Shapes → Rectangle at the top (full width, ~60px tall), fill `#0F2B46`, no outline. On top of it: Insert → Text box, page title in white, Segoe UI 20pt bold; right-aligned second text box with the study label `PROTOCOL XYZ-101 · SYNTHETIC DATA` in white 9pt.
- **Slicer rail:** put all slicers in a vertical stack on the left ~180px wide; give each slicer a header (Format visual → Slicer header on, title set).
- **Card style baseline:** KPI cards: callout value Segoe UI 28pt bold, color `#0F2B46`; category label 10pt gray `#5A6C7D`; card background white with a subtle border (`#D9E2EC`, 1px) via Format visual → Style / border.

**Theme (matches the palette used below):** View tab → Themes → **Customize current theme** → set: Name `Clinical Ops`; Colors: Data colors in order — `#0F2B46` (navy), `#12808A` (teal), `#F2A93B` (amber), `#C0392B` (red), then `#5A6C7D`, `#8FA6B8`, `#D9E2EC`, `#37B6A2`. Background `#FFFFFF`, Foreground `#0F2B46`, Table accent `#12808A`. Text: Title 20pt Segoe UI, heading 12pt. Then Apply. (Exact colors: navy `#0F2B46`, teal `#12808A`, amber `#F2A93B`, red `#C0392B`.)

For every visual: after building, open **Format visual** → General → **Title** (set the title text exactly as given), and turn **Background** on (white) with a border for chart visuals.

---

### Page 1 — Study Overview (landing page)

**Slicers (left rail):** Sites[Region] (dropdown) · Sites[SiteName] (dropdown) · Subjects[TreatmentArm] (dropdown) · Calendar[Date] (Between date range).

**KPI cards (top row, six cards left→right):**
1. Card → [Randomized Subjects] — Title: "Randomized"
2. Card → [Total Subjects] — Title: "Total Screened"
3. Card → [Screen Failure Rate] — Title: "Screen Failure Rate"
4. Card → [Enrollment Achievement %] — Title: "Enrollment Achievement"
5. Card → [Open Queries] — Title: "Open Queries"
6. Card → [Total SAEs] — Title: "SAEs"

**Visual A — Enrollment trend (middle left, wide).**
- Visual: **Line chart**. 
- X-axis: Calendar[MonthYear]. Y-axis: [Randomized Subjects].
- Add second line: drag Calendar-axis again? Instead: add measure **Screened Subjects** to Y-axis as second series. 
- Format: data labels off; Y-axis title off; legend position Top center; line colors: series 1 teal `#12808A`, series 2 navy `#0F2B46` (Format → Lines → per-series color). Title: "Enrollment by Month".

Wait — screened uses ScreenDate, and the active relationship is RandomizationDate, so Screened Subjects on this axis would show the wrong dates. Create this measure and use it instead of [Screened Subjects] in Visual A:

```DAX
Screened Subjects (Screen Date) =
CALCULATE (
    [Screened Subjects],
    USERELATIONSHIP ( Calendar[Date], Subjects[ScreenDate] )
)
```

**Visual B — Subjects by status (middle right).**
- Visual: **Donut chart**. Legend: Subjects[Status]. Values: [Total Subjects].
- Format: Detail labels = Category + percentage; colors: Randomized teal, Completed navy, Screen Failure amber, Withdrawn red, Screened gray `#8FA6B8` (Format → Slices → per-category colors). Title: "Subjects by Status".

**Visual C — Enrollment by site (bottom, full width).**
- Visual: **Clustered bar chart**. Y-axis: Sites[SiteName]. X-axis: [Randomized Subjects]. 
- Add target line: Format → Analytics pane (magnifier icon) → **Constant line** → value = average target per site (40) — set Value 40, color amber dashed. Title: "Randomized Subjects by Site (amber line = per-site target 40)".

**Filters on this page (Filters pane → Filters on this page):** none mandatory; optional Subjects[Status] exclusion of nothing. Leave empty.

---

### Page 2 — Site Performance (risk page)

**Slicers:** Sites[Region] (dropdown) · Sites[SiteStatus] (dropdown).

**Matrix — the centerpiece (top, full width).**
- Visual: **Matrix**. Rows: Sites[SiteName]. Values (in this order): [Randomized Subjects], [Screen Failure Rate], [Open Queries], [Overdue Visits], [Missing Forms], [Open Major Deviations], [Site Risk].
- Format: Format visual → Style presets default; Row headers left-align; Values → set number formats (Screen Failure Rate shows as % automatically from measure format). Title: "Site Performance & Risk".
- Conditional formatting (Part 5 has the full rule list — apply the Site matrix rules here).

**Visual A — Screen failure rate by site (bottom left).**
- Visual: **Clustered column chart**. Axis: Sites[SiteName]. Values: [Screen Failure Rate].
- Format: Y-axis as percentage; data labels on, Outside end; add Analytics **constant line** at 0.30 (30%) red dashed, name it "Risk threshold 30%". Title: "Screen Failure Rate by Site".

**Visual B — Open queries & overdue visits by site (bottom right).**
- Visual: **Clustered bar chart**. Y-axis: Sites[SiteName]. X-axis: [Open Queries], then also drag [Overdue Visits] into X-axis (two series).
- Legend: turns on automatically (series names). Colors: Open Queries teal, Overdue Visits amber. Data labels on. Title: "Workload by Site — Open Queries & Overdue Visits".

**Filters on this page:** Sites[SiteStatus] = "Active" (pre-set in Filters pane) so closed sites never pollute risk views.

---

### Page 3 — Visit & Form Completion

**Slicers:** Visits[VisitName] (dropdown) · Sites[SiteName] (dropdown) · Visits[WindowStatus] (dropdown).

**KPI cards (top row, three):** [Overdue Visits] "Overdue Visits" · [Missing Forms] "Missing Forms" · [Form Completion %] "Form Completion".

**Visual A — Overdue visits by visit (left).**
- Visual: **Clustered bar chart**. Y-axis: Visits[VisitName]. X-axis: [Overdue Visits].
- Sort: Axis order Screening → Week 24 — select visual → **... (More options)** → Sort by VisitName. (Names don't sort perfectly naturally; acceptable. Or add a sort column in Visits with visit order 1-7 and sort VisitName by it — 2-minute fix in Power Query.)
- Data color red `#C0392B`. Data labels on. Title: "Overdue Visits by Study Visit".

**Visual B — Missing forms by form (middle).**
- Visual: **Clustered bar chart**. Y-axis: Forms[FormName]. X-axis: [Missing Forms]. Data color amber `#F2A93B`. Data labels on. Title: "Missing eCRFs by Form".

**Visual C — Form completion by site × visit (bottom, full width).**
- Visual: **Matrix**. Rows: Sites[SiteName]. Columns: Forms[VisitName]. Values: [Form Completion %].
- Format: Totals row/column on; set column width auto. Title: "Form Completion % by Site and Visit".
- Conditional formatting: color scale on the values (Part 5).

**Filters on this page:** Forms[FormStatus] — do NOT filter (completion % needs both states). Visits[PlannedDate] via Calendar won't work (no relationship); use Visits[VisitStatus] in Filters pane if you want to focus.

---

### Page 4 — Query Management

**Slicers:** Sites[SiteName] (dropdown) · Queries[FormName] (dropdown) · Queries[QueryStatus] (dropdown).

**KPI cards (top row, two big + two small):** [Open Queries] "Open Queries" · [Average Open Query Age] "Avg Open Query Age (days)".

**Visual A — Open query aging (left, wide).**
- Visual: **Clustered column chart**. Axis: Queries[Age Bucket]. Values: [Open Queries].
- Colors per bucket: 0-7 teal, 8-14 amber-light — per-category colors need single-series per-category coloring: Format → Columns → Colors → use the per-category color pickers after switching "Show all". 30+ days red `#C0392B`, 15-30 amber `#F2A93B`, 8-14 `#E8C547`-ish light amber, 0-7 teal. Data labels on. Title: "Open Queries by Age".

**Visual B — Open queries by form (right).**
- Visual: **Clustered bar chart**. Y-axis: Queries[FormName]. X-axis: [Open Queries]. Teal. Data labels on. Title: "Open Queries by eCRF".

**Visual C — Oldest open queries table (bottom, full width).**
- Visual: **Table**. Columns: Queries[QueryID], Subjects[SubjectID], Sites[SiteName] (drag from Sites — it resolves through Subjects), Queries[FormName], Queries[QueryOpenDate], Queries[QueryText]. 
- Page-level note: a table doesn't expose per-row age directly — add the Age Bucket column too.
- Sort: click QueryOpenDate header → ascending (oldest first). Visual-level Filters pane: QueryStatus is Open. Title: "Open Queries — Oldest First".

**Filters on this page:** Filters on this visual (Visual C): QueryStatus = Open.

---

### Page 5 — Safety & Deviations

**Slicers:** Sites[SiteName] (dropdown) · AdverseEvents[Serious] (dropdown) · AdverseEvents[SeverityGrade] (dropdown).

**KPI cards (top row):** [Total AEs] "Adverse Events" · [Total SAEs] "SAEs" · [Open Major Deviations] "Open Major Deviations".

**Visual A — AEs by term (left).**
- Visual: **Clustered bar chart**. Y-axis: AdverseEvents[AETerm]. X-axis: [Total AEs]. Sort descending by value (visual … → Sort by Total AEs). Show top 10 only: Filters on this visual → AETerm → Top N → Top 10 by Total AEs. Teal. Title: "Adverse Events by Term (Top 10)".

**Visual B — AEs by severity grade (middle).**
- Visual: **Stacked column chart**. Axis: AdverseEvents[SeverityGrade]. Legend: AdverseEvents[Serious]. Values: [Total AEs]. Colors: No → teal, Yes → red. Title: "AEs by CTCAE Grade (red = serious)".

**Visual C — Major deviations by site (right).**
- Visual: **Clustered bar chart**. Y-axis: Sites[SiteName]. X-axis: [Open Major Deviations]. Amber/red: use red `#C0392B` (these are risk items). Filters on this visual: Deviations[Severity] = Major and Deviations[DeviationStatus] = Open (visual-level, so the KPI/table interplay stays clean). Title: "Open Major Deviations by Site".

**Visual D — SAE detail table (bottom, full width).**
- Visual: **Table**. Columns: AdverseEvents[AEID], Subjects[SubjectID], Sites[SiteName], AdverseEvents[AETerm], AdverseEvents[StartDate], AdverseEvents[SeverityGrade], AdverseEvents[Outcome], AdverseEvents[RelatedToStudyDrug].
- Visual-level filter: AdverseEvents[Serious] = "Yes". Title: "Serious Adverse Events (detail)".

**Filters on this page:** none global.

---

## Part 5 — Conditional formatting rules (exact)

Apply these via: select visual → Format visual → Cells / Columns / specific element → **fx** (conditional formatting) → Format by **Rules**.

### Page 2 — Site matrix cell rules (apply per column)

**Screen Failure Rate column:**
- If value ≥ 0.30 → background `#C0392B`, font white (high risk)
- If value ≥ 0.25 and < 0.30 → background `#F2A93B`
- Else → no fill

**Open Queries column:**
- If value ≥ 25 → background `#C0392B`, font white
- If value ≥ 15 and < 25 → background `#F2A93B`

**Overdue Visits column:**
- If value ≥ 10 → background `#C0392B`, font white
- If value ≥ 5 and < 10 → background `#F2A93B`

**Missing Forms column:**
- If value ≥ 300 → background `#F2A93B` — calibrate your threshold to the site matrix's rough spread; note missing forms scale with site volume.

**Open Major Deviations column:**
- If value ≥ 2 → background `#C0392B`, font white
- If value = 1 → background `#F2A93B`

**Site Risk column (text):**
- If text = "High" → background `#C0392B`, font white bold
- If text = "Normal" → background `#E8F4F3`

### Page 3 — Form Completion % matrix (color scale)

Select values → conditional formatting → Background color → Format by **Color scale**: Minimum (0.70) `#C0392B` → Center (0.90) `#F2A93B` → Maximum (1.00) `#12808A`. Any site×visit cell under 70% complete draws the eye instantly.

### Page 3 — Overdue Visits bar chart

Format → Columns → Colors → fx → Rules on [Overdue Visits]: ≥ 40 red `#C0392B`; ≥ 25 amber `#F2A93B`; else teal (late-study visits naturally accumulate — this is a visit-level count, so thresholds are higher than site-level).

### Page 4 — Old open query table

Select the QueryOpenDate column in the table → conditional formatting on Age Bucket instead: switch the table's Age Bucket cells: "30+ days" → background `#C0392B` white font; "15-30 days" → `#F2A93B`. (Table columns support per-column conditional formatting via the column's fx in Format → Specific column.)

### Page 5 — SAE table

Select AETerm column → rules: no fill needed; instead format SeverityGrade column: ≥ 4 → background `#C0392B`, font white; = 3 → background `#F2A93B`. Select RelatedToStudyDrug: "Yes" → font bold red `#C0392B` (via Font color rules: text = Yes → `#C0392B`).

---

## Part 6 — Theme & layout guide

**Palette (clinical, restrained):**
- Navy `#0F2B46` — headers, titles, primary text
- Teal `#12808A` — healthy/on-track data, primary series
- Amber `#F2A93B` — warnings, watch items, targets
- Red `#C0392B` — risk only: SAEs, major deviations, breached thresholds
- Page background `#F4F6F8`, card background white, muted text `#5A6C7D`

Rule of thumb for your portfolio: **red is reserved for safety/risk** (SAEs, major deviations, breached thresholds). Nothing decorative is red.

**Layout grid (every page):**
- Header band: 60px navy strip with page title + study label.
- Slicer rail: left 180px column, white background panel.
- KPI row: directly under header, each card ~180×90px, equal spacing.
- Charts: two-up middle row (~520×280 each), full-width table/matrix at the bottom (~1080×220).
- Footer strip (optional): "Synthetic data — portfolio demo" in 8pt gray bottom-right of every page.

**Navigation:** add page navigator buttons (Insert → Buttons → Page navigator) in the header of Page 1, or put a navy button strip under the header on every page linking to the other four pages.

---

## Part 7 — Validation checklist (confirm every measure manually)

With the provided synthetic CSVs loaded and **no slicers/filters applied**, your measures must read exactly:

| Measure | Expected | How to verify from the CSV |
|---|---|---|
| Total Subjects | **549** | Row count of Subjects.csv (minus header) |
| Screened Subjects | **549** | Count of non-blank ScreenDate in Subjects.csv |
| Randomized Subjects | **421** | Count of non-blank RandomizationDate in Subjects.csv |
| Screen Failures | **113** | Count rows where Status = "Screen Failure" |
| Screen Failure Rate | **20.6%** | 113 ÷ 549 |
| Enrollment Target | **480** | Sum of EnrollmentTarget in Sites.csv (40 × 12) |
| Enrollment Achievement % | **87.7%** | 421 ÷ 480 |
| Open Queries | **730** | Count Queries where QueryStatus = "Open" |
| Average Open Query Age | **≈61.1 days** | Average of (2026-09-30 − QueryOpenDate) over open queries. NOTE: the measure uses TODAY(), so drill this number the same day you validate it — your CSV check must subtract from *today's* date, not 2026-09-30. The number drifts up daily by design. |
| Overdue Visits | **205** | Count Visits where VisitStatus = "Overdue" |
| Missing Forms | **2,639** | Count Forms where FormStatus = "Missing" |
| Form Completion % | **83.8%** | Completed Forms (13,615) ÷ 16,254 |
| Total AEs | **316** | Row count of AdverseEvents.csv |
| Total SAEs | **26** | Count AdverseEvents where Serious = "Yes" |
| Open Major Deviations | **22** | Count Deviations where Severity = "Major" AND DeviationStatus = "Open" |

**Manual cross-checks (do these in Excel or with filters):**
1. In Excel, pivot Subjects by SiteID → each site shows 43–51 subjects. In Power BI Page 1 with SiteName slicer set to one site, [Total Subjects] must match that site's pivot count.
2. Filter Queries.csv to one SubjectID; count rows. In Power BI, set a report-level SubjectID filter to the same subject — [Open Queries] + answered/closed counts must sum to the same total.
3. Page 2 matrix grand total row must equal the KPI cards on Page 1 (randomized 421, open queries 730) with no filters applied.
4. Check one SAE by hand: pick any AdverseEvents row with Serious = "Yes", find its SubjectID → SiteID in Subjects → SiteName in Sites. That site must show that SAE under Page 5's SAE table when filtered to the site.
5. Calendar sanity: Page 1 enrollment line should start Jan 2025 and rise smoothly; if MonthYear sorts Feb, Jan, Mar (alphabetical), redo the Sort by column step on MonthYear.

**Known data caveat:** Query dates in the synthetic files are anchored to a 2026-09-30 reference date. Open-query aging therefore looks correct "today" (Oct 2026) and slowly inflates over real time — which the Average Open Query Age validation note above accounts for.

---

## Portfolio packaging checklist (last mile)

1. **Rename the file** `Clinical_Trial_Operations_Dashboard.pbix`.
2. File → Options → make sure all visuals load with **no filters pre-applied** except Page 2's SiteStatus = Active.
3. Bookmarks (optional but impressive): add a bookmark on Page 2 "High-risk sites only" with the Sites[SiteRisk]… filter applied via a Sites slicer — actually filter the matrix visual by Site Risk = High.
4. README for your portfolio: one paragraph on the star schema (Sites → Subjects → facts), one on the risk-flag logic (Part 5 thresholds), one line distinguishing this EDC operations view from downstream CDASH/SDTM/ADaM datasets.
5. Screenshots for the portfolio: Page 1 (overview) + Page 2 (risk matrix) are the two that read best at thumbnail size.

**You are done when:** all five pages render, every measure in Part 7 matches the table, and at least one site glows red on Page 2.
