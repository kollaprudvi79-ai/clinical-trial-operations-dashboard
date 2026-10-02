#!/usr/bin/env python3
"""Synthetic clinical trial operations data — V2 (very complex edition).
Seeded and reproducible. 100% fake. No real patient data.
Reference 'today' = 2026-09-30."""
import csv, random, os
from datetime import date, timedelta

random.seed(2026)
REF = date(2026, 9, 30)
OUT = os.path.expanduser('~/workspace/your_files/clinical-trial-dashboard/data-v2')
os.makedirs(OUT, exist_ok=True)

FIRST = ['James','Mary','Robert','Patricia','John','Jennifer','Michael','Linda','David','Elizabeth','William','Barbara','Richard','Susan','Joseph','Jessica','Thomas','Sarah','Charles','Karen','Daniel','Nancy','Matthew','Lisa','Anthony','Betty','Mark','Margaret','Donald','Sandra','Kevin','Michelle','Brian','Ashley','Timothy','Kimberly','Jason','Deborah','Jeffrey','Dorothy']
LAST = ['Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis','Rodriguez','Martinez','Hernandez','Lopez','Gonzalez','Wilson','Anderson','Thomas','Taylor','Moore','Jackson','Martin','Lee','Perez','Thompson','White','Harris','Sanchez','Clark','Lewis','Robinson','Walker','Young','Allen','King','Wright','Scott','Green','Baker','Adams','Nelson','Hill','Ramirez']
COUNTRIES = [
    ('United States','North America'),('United States','North America'),('United States','North America'),
    ('United States','North America'),('United States','North America'),('Canada','North America'),
    ('Canada','North America'),('United Kingdom','Europe'),('United Kingdom','Europe'),
    ('Germany','Europe'),('Germany','Europe'),('France','Europe'),('France','Europe'),
    ('Spain','Europe'),('Poland','Europe'),('Italy','Europe'),('Netherlands','Europe'),
    ('India','Asia-Pacific'),('India','Asia-Pacific'),('Australia','Asia-Pacific'),
    ('Japan','Asia-Pacific'),('South Korea','Asia-Pacific'),('Brazil','Latin America'),
    ('Mexico','Latin America'),('Argentina','Latin America'),('South Africa','Africa'),
]
CITY = {'United States':['Houston','Chicago','New York','Los Angeles','Seattle','Denver','Boston','Phoenix','Dallas','Miami'],
        'Canada':['Toronto','Vancouver','Montreal'],'United Kingdom':['London','Manchester','Edinburgh'],
        'Germany':['Berlin','Munich','Hamburg'],'France':['Paris','Lyon','Marseille'],'Spain':['Madrid','Barcelona'],
        'Poland':['Warsaw','Krakow'],'Italy':['Rome','Milan'],'Netherlands':['Amsterdam','Rotterdam'],
        'India':['Mumbai','Delhi','Bangalore'],'Australia':['Sydney','Melbourne'],'Japan':['Tokyo','Osaka'],
        'South Korea':['Seoul','Busan'],'Brazil':['Sao Paulo','Rio de Janeiro'],'Mexico':['Mexico City','Guadalajara'],
        'Argentina':['Buenos Aires','Cordoba'],'South Africa':['Cape Town','Johannesburg']}

# ---------------- Sites (40) ----------------
sites = []
for i in range(1, 41):
    country, region = COUNTRIES[(i - 1) % len(COUNTRIES)]
    city = random.choice(CITY[country])
    sites.append({
        'SiteID': f'S{i:02d}', 'SiteName': f'Site {i:02d} - {city} Medical Center',
        'Country': country, 'Region': region, 'City': city,
        'PrincipalInvestigator': f'Dr. {random.choice(FIRST)} {random.choice(LAST)}',
        'SiteStatus': 'Active' if i % 13 else 'Closed to Enrollment',
        'ActivationDate': (date(2025, 1, 6) + timedelta(days=random.randint(0, 240))).isoformat(),
        'EnrollmentTarget': random.choice([45, 50, 55, 60]),
    })

# ---------------- Subjects (~2,400) ----------------
STATUSES_RAND = ['Randomized', 'On Treatment', 'Completed', 'Withdrawn']
subjects = []
sub_seq = 0
for site in sites:
    screened = random.randint(52, 68)
    act = date.fromisoformat(site['ActivationDate'])
    for _ in range(screened):
        sub_seq += 1
        scr = act + timedelta(days=random.randint(5, 560))
        if scr > REF: scr = REF - timedelta(days=random.randint(1, 45))
        r = random.random()
        if r < 0.205:
            status, rdate, arm = 'Screen Failure', '', ''
        elif r < 0.235:
            status, rdate, arm = 'Screened', '', ''
        else:
            rdate = scr + timedelta(days=random.randint(3, 21))
            if isinstance(rdate, date) and rdate > REF: rdate = REF - timedelta(days=random.randint(1, 10))
            arm = random.choices(['Placebo', 'Dose Low', 'Dose High'], weights=[34, 33, 33])[0]
            s2 = random.random()
            if s2 < 0.55: status = 'On Treatment'
            elif s2 < 0.68: status = 'Randomized'
            elif s2 < 0.88: status = 'Completed'
            else: status = 'Withdrawn'
        age = random.randint(18, 82)
        subjects.append({
            'SubjectID': f'SUB-{sub_seq:04d}', 'SiteID': site['SiteID'],
            'ScreenDate': scr.isoformat(),
            'RandomizationDate': rdate.isoformat() if isinstance(rdate, date) else '',
            'Status': status,
            'Age': age,
            'AgeGroup': '18-40' if age <= 40 else '41-55' if age <= 55 else '56-65' if age <= 65 else '65+',
            'Sex': random.choice(['Female', 'Male']),
            'Race': random.choices(['White', 'Black or African American', 'Asian', 'Other', 'Not Reported'], weights=[58, 16, 14, 6, 6])[0],
            'Ethnicity': random.choices(['Not Hispanic or Latino', 'Hispanic or Latino', 'Not Reported'], weights=[78, 16, 6])[0],
            'BMICategory': random.choices(['Underweight', 'Normal', 'Overweight', 'Obese'], weights=[3, 38, 33, 26])[0],
            'DiseaseStage': random.choice(['Stage II', 'Stage III', 'Stage IV']),
            'PriorTherapyLines': random.choices([0, 1, 2, 3], weights=[42, 33, 18, 7])[0],
            'TreatmentArm': arm,
            'WithdrawalReason': random.choice(['Adverse Event', 'Consent Withdrawn', 'Protocol Violation', 'Lost to Follow-up', 'Physician Decision']) if status == 'Withdrawn' else '',
        })
randomized = [s for s in subjects if s['RandomizationDate']]

# ---------------- Visits (10) ----------------
VISIT_PLAN = [('Screening', -14), ('Baseline', 0), ('Week 2', 14), ('Week 4', 28), ('Week 8', 56),
              ('Week 12', 84), ('Week 16', 112), ('Week 24', 168), ('Week 36', 252), ('Week 52 / EOT', 364)]
visits = []
v_seq = 0
for s in subjects:
    anchor = date.fromisoformat(s['RandomizationDate']) if s['RandomizationDate'] else date.fromisoformat(s['ScreenDate'])
    for idx, (vname, offset) in enumerate(VISIT_PLAN):
        if vname != 'Screening' and not s['RandomizationDate']:
            continue
        v_seq += 1
        planned = anchor + timedelta(days=offset)
        if planned > REF + timedelta(days=21):
            vstatus, actual, window = 'Scheduled', '', ''
        else:
            rr = random.random()
            if rr < 0.87:
                vstatus = 'Completed'; delta = random.randint(-3, 4); actual = planned + timedelta(days=delta)
                window = 'In Window' if abs(delta) <= 3 else 'Out of Window'
            elif rr < 0.93: vstatus, actual, window = 'Overdue', '', ''
            else: vstatus, actual, window = 'Missed', '', ''
            if planned > REF and vstatus != 'Completed':
                vstatus, actual, window = 'Scheduled', '', ''
        visits.append({'VisitID': f'V{v_seq:05d}', 'SubjectID': s['SubjectID'], 'SiteID': s['SiteID'],
                       'VisitName': vname, 'VisitOrder': idx + 1,
                       'PlannedDate': planned.isoformat(),
                       'ActualDate': actual.isoformat() if isinstance(actual, date) else '',
                       'VisitStatus': vstatus, 'WindowStatus': window})

# ---------------- Forms (14 eCRFs) ----------------
FORM_SET = [('Informed Consent', 1), ('Eligibility', 1), ('Demographics', 1), ('Medical History', 1),
            ('Vital Signs', 2), ('Physical Exam', 2), ('ECG', 2), ('Laboratory Hematology', 2),
            ('Laboratory Chemistry', 2), ('Efficacy Assessment', 2), ('Patient Diary', 2),
            ('Concomitant Medications', 2), ('Study Drug Exposure', 2), ('Adverse Events Log', 2)]
forms = []
f_seq = 0
visit_by_subj = {}
for v in visits:
    visit_by_subj.setdefault(v['SubjectID'], []).append(v)
for s in subjects:
    for v in visit_by_subj.get(s['SubjectID'], []):
        planned = date.fromisoformat(v['PlannedDate'])
        for fname, tier in FORM_SET:
            if tier == 1 and v['VisitName'] != 'Screening':
                continue
            if fname == 'Adverse Events Log' and random.random() < 0.45:
                continue
            f_seq += 1
            if v['VisitStatus'] == 'Completed':
                fr = random.random()
                fstatus = 'Completed' if fr < 0.90 else ('Missing' if fr < 0.96 else 'In Progress')
            elif v['VisitStatus'] in ('Overdue', 'Missed'):
                fr = random.random()
                fstatus = 'Missing' if fr < 0.72 else ('Completed' if fr < 0.88 else 'Not Started')
            else:
                fstatus = 'Not Started' if random.random() < 0.6 else 'In Progress'
            comp = lag = ''
            if fstatus == 'Completed':
                lag = random.randint(0, 9); comp = (planned + timedelta(days=lag)).isoformat()
            forms.append({'FormID': f'F{f_seq:06d}', 'SubjectID': s['SubjectID'], 'SiteID': s['SiteID'],
                          'VisitName': v['VisitName'], 'FormName': fname, 'FormStatus': fstatus,
                          'DueDate': planned.isoformat(), 'CompletionDate': comp, 'EntryLagDays': lag})

# ---------------- Labs (panel-level rows) ----------------
LAB_TESTS = [('Hematology', ['Hemoglobin', 'WBC', 'Platelets', 'Neutrophils']),
             ('Chemistry', ['ALT', 'AST', 'Creatinine', 'Bilirubin', 'Sodium', 'Potassium', 'Glucose']),
             ('Urinalysis', ['Protein', 'Blood', 'Leukocytes'])]
labs = []
l_seq = 0
for s in randomized:
    if random.random() < 0.12:
        continue
    anchor = date.fromisoformat(s['RandomizationDate'])
    for vname, offset in [('Baseline', 0), ('Week 4', 28), ('Week 12', 84), ('Week 24', 168)]:
        d = anchor + timedelta(days=offset)
        if d > REF: continue
        for panel, tests in LAB_TESTS:
            for t in tests:
                l_seq += 1
                fr = random.random()
                flag = 'Normal' if fr < 0.82 else ('High' if fr < 0.91 else 'Low')
                crit = 'Yes' if flag != 'Normal' and random.random() < 0.06 else 'No'
                labs.append({'LabID': f'L{l_seq:06d}', 'SubjectID': s['SubjectID'], 'SiteID': s['SiteID'],
                             'VisitName': vname, 'Panel': panel, 'Test': t, 'ResultFlag': flag,
                             'CriticalFlag': crit, 'CollectionDate': d.isoformat()})

# ---------------- Dosing / Exposure ----------------
DOSE_VISITS = ['Baseline', 'Week 2', 'Week 4', 'Week 8', 'Week 12', 'Week 16', 'Week 24', 'Week 36', 'Week 52 / EOT']
dosing = []
for s in randomized:
    if s['TreatmentArm'] == 'Placebo':
        continue
    anchor = date.fromisoformat(s['RandomizationDate'])
    for i, vn in enumerate(DOSE_VISITS):
        d = anchor + timedelta(days=[0, 14, 28, 56, 84, 112, 168, 252, 364][i])
        if d > REF: break
        r = random.random()
        event = 'Dose Taken' if r < 0.90 else ('Dose Held (AE)' if r < 0.95 else ('Dose Reduced' if r < 0.98 else 'Dose Missed'))
        dosing.append({'SubjectID': s['SubjectID'], 'SiteID': s['SiteID'], 'TreatmentArm': s['TreatmentArm'],
                       'VisitName': vn, 'DoseDate': d.isoformat(), 'DoseEvent': event})

# ---------------- Queries ----------------
QTEXT = {
    'Vital Signs': ['Systolic BP out of plausible range - please verify', 'Heart rate missing at this visit - confirm not done or enter'],
    'Laboratory Hematology': ['Hemoglobin drop >2 g/dL from baseline - please confirm repeat', 'Lab date differs from visit date - please clarify'],
    'Laboratory Chemistry': ['ALT above 3x ULN flagged - confirm adverse event reported', 'Creatinine missing - please enter or mark not done'],
    'Demographics': ['Date of birth inconsistent with age at screening - verify', 'Race field not reported and no reason given - clarify'],
    'ECG': ['ECG interpretation not recorded - please complete', 'QTc value missing - please enter'],
    'Concomitant Medications': ['Medication start date after stop date - please correct', 'Prohibited medication flagged - confirm with medical monitor'],
    'Efficacy Assessment': ['Primary endpoint score missing - please enter', 'Score unchanged across 3 visits - confirm correct'],
    'Study Drug Exposure': ['Dose date does not match visit date - please clarify', 'Dose held reason not documented - please add'],
    'Informed Consent': ['Consent version signed is not the current IRB-approved version', 'Consent signature date after screening procedures - escalate'],
    'Medical History': ['Ongoing condition missing from AE log - cross-check', 'Diagnosis date after randomization - verify'],
    'Eligibility': ['Inclusion criterion #4 lab value outside window - confirm eligibility', 'Exclusion labs not filed - please upload'],
    'Patient Diary': ['Diary compliance below 70% this period - site to retrain subject', 'Diary entries missing for 5 consecutive days'],
    'Physical Exam': ['Abnormal finding without corresponding AE - please reconcile', 'Exam not performed but form marked complete'],
    'Adverse Events Log': ['AE start date before first dose date - please verify', 'Serious AE not reported within 24h window - escalate'],
}
QCAT = ['Missing Data', 'Inconsistent Data', 'Out-of-Range Value', 'Clarification', 'Eligibility Check', 'Safety Escalation']
queries = []
q_seq = 0
for f in forms:
    if random.random() < 0.075:
        q_seq += 1
        opened = date.fromisoformat(f['DueDate']) + timedelta(days=random.randint(1, 25))
        if opened > REF: opened = REF - timedelta(days=random.randint(0, 6))
        r = random.random()
        if r < 0.42: qstatus, closed = 'Open', ''
        elif r < 0.68: qstatus, closed = 'Answered', opened + timedelta(days=random.randint(1, 18))
        else: qstatus, closed = 'Closed', opened + timedelta(days=random.randint(1, 30))
        if isinstance(closed, date) and closed > REF: qstatus, closed = 'Open', ''
        if qstatus == 'Open': opened = REF - timedelta(days=random.randint(1, 130))
        texts = QTEXT.get(f['FormName'], ['Value requires clarification - please review source'])
        queries.append({'QueryID': f'Q{q_seq:06d}', 'SubjectID': f['SubjectID'], 'SiteID': f['SiteID'],
                        'VisitName': f['VisitName'], 'FormName': f['FormName'], 'Category': random.choice(QCAT),
                        'QueryText': random.choice(texts), 'QueryOpenDate': opened.isoformat(),
                        'QueryCloseDate': closed.isoformat() if isinstance(closed, date) else '', 'QueryStatus': qstatus})

# ---------------- Adverse Events (MedDRA-style SOC) ----------------
SOC_TERMS = {
    'Nervous system disorders': ['Headache', 'Dizziness', 'Insomnia', 'Peripheral neuropathy'],
    'Gastrointestinal disorders': ['Nausea', 'Diarrhea', 'Vomiting', 'Constipation', 'Abdominal pain'],
    'General disorders': ['Fatigue', 'Pyrexia', 'Injection site pain', 'Edema peripheral'],
    'Musculoskeletal disorders': ['Back pain', 'Myalgia', 'Arthralgia'],
    'Skin disorders': ['Rash', 'Pruritus', 'Dry skin'],
    'Infections': ['Upper respiratory tract infection', 'Urinary tract infection', 'Nasopharyngitis'],
    'Investigations': ['ALT increased', 'AST increased', 'Neutrophil count decreased', 'Weight decreased'],
    'Vascular disorders': ['Hypertension', 'Hypotension'],
    'Metabolism disorders': ['Decreased appetite', 'Hyperglycemia'],
    'Respiratory disorders': ['Cough', 'Dyspnea'],
}
OUTCOMES = ['Recovered', 'Recovering', 'Ongoing', 'Recovered with sequelae', 'Fatal']
ACTIONS = ['None', 'Dose Held', 'Dose Reduced', 'Drug Withdrawn', 'Concomitant Treatment Given']
aes = []
a_seq = 0
for s in randomized:
    n_ae = random.choices([0, 1, 2, 3, 4], weights=[48, 27, 15, 7, 3])[0]
    for _ in range(n_ae):
        a_seq += 1
        start = date.fromisoformat(s['RandomizationDate']) + timedelta(days=random.randint(1, 320))
        if start > REF: start = REF - timedelta(days=random.randint(1, 20))
        soc = random.choice(list(SOC_TERMS.keys()))
        serious = 'Yes' if random.random() < 0.085 else 'No'
        grade = random.choices([1, 2, 3, 4, 5], weights=[42, 35, 16, 5, 2])[0]
        if serious == 'Yes' and grade < 3: grade = 3
        outcome = random.choices(OUTCOMES, weights=[52, 20, 22, 5, 1])[0]
        aes.append({'AEID': f'AE{a_seq:05d}', 'SubjectID': s['SubjectID'], 'SiteID': s['SiteID'],
                    'SystemOrganClass': soc, 'AETerm': random.choice(SOC_TERMS[soc]),
                    'StartDate': start.isoformat(),
                    'OnsetDayFromFirstDose': (start - date.fromisoformat(s['RandomizationDate'])).days,
                    'SeverityGrade': grade, 'Serious': serious, 'Outcome': outcome,
                    'ActionTaken': random.choice(ACTIONS),
                    'RelatedToStudyDrug': random.choices(['Yes', 'No'], weights=[46, 54])[0]})
    # (remove accidental duplicate line artifact)

# fix: remove the accidental invalid row if created
aes = [a for a in aes if a['SubjectID'] in {s['SubjectID'] for s in randomized}]

# ---------------- Deviations (richer) ----------------
DEV_CATS = ['Visit Window', 'Inclusion/Exclusion Criteria', 'Study Drug Dosing', 'Laboratory Procedure',
            'Informed Consent', 'Prohibited Medication', 'Randomization Error', 'Source Document Missing']
ROOT_CAUSE = ['Site Staff Error', 'Subject Non-compliance', 'Equipment Failure', 'Scheduling Conflict', 'Protocol Ambiguity', 'Lab Processing Delay']
devs = []
d_seq = 0
for s in randomized:
    if random.random() < 0.42:
        for _ in range(random.choices([1, 2, 3], weights=[76, 19, 5])[0]):
            d_seq += 1
            ddate = date.fromisoformat(s['RandomizationDate']) + timedelta(days=random.randint(3, 300))
            if ddate > REF: ddate = REF - timedelta(days=random.randint(1, 30))
            sev = 'Major' if random.random() < 0.30 else 'Minor'
            dstatus = 'Open' if random.random() < 0.46 else 'Closed'
            devs.append({'DeviationID': f'DEV{d_seq:04d}', 'SubjectID': s['SubjectID'], 'SiteID': s['SiteID'],
                         'DeviationDate': ddate.isoformat(), 'Category': random.choice(DEV_CATS),
                         'Severity': sev, 'DeviationStatus': dstatus, 'RootCause': random.choice(ROOT_CAUSE),
                         'DaysOpen': (REF - ddate).days if dstatus == 'Open' else random.randint(3, 60)})

# ---------------- Concomitant Medications ----------------
MEDS = [('Analgesics', 'Paracetamol'), ('Analgesics', 'Ibuprofen'), ('Antihypertensives', 'Lisinopril'),
        ('Antihypertensives', 'Amlodipine'), ('Antidiabetics', 'Metformin'), ('Statins', 'Atorvastatin'),
        ('Antihistamines', 'Cetirizine'), ('Proton Pump Inhibitors', 'Omeprazole'),
        ('Antidepressants', 'Sertraline'), ('Vitamins', 'Cholecalciferol'),
        ('Antibiotics', 'Amoxicillin'), ('Corticosteroids', 'Prednisone')]
meds = []
m_seq = 0
for s in randomized:
    for _ in range(random.choices([0, 1, 2, 3, 4], weights=[30, 30, 22, 12, 6])[0]):
        m_seq += 1
        cls, drug = random.choice(MEDS)
        start = date.fromisoformat(s['RandomizationDate']) - timedelta(days=random.randint(0, 90))
        ongoing = random.random() < 0.55
        meds.append({'MedID': f'M{m_seq:05d}', 'SubjectID': s['SubjectID'], 'SiteID': s['SiteID'],
                     'DrugClass': cls, 'DrugName': drug, 'StartDate': start.isoformat(),
                     'Ongoing': 'Yes' if ongoing else 'No'})

def dump(name, rows):
    if not rows:
        print(name, 0); return
    with open(os.path.join(OUT, name), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(name, len(rows))

dump('Sites.csv', sites); dump('Subjects.csv', subjects); dump('Visits.csv', visits)
dump('Forms.csv', forms); dump('Labs.csv', labs); dump('Dosing.csv', dosing)
dump('Queries.csv', queries); dump('AdverseEvents.csv', aes); dump('Deviations.csv', devs)
dump('Medications.csv', meds)

# ---------------- Validation ----------------
print('---VALIDATION V2---')
print('TotalSubjects', len(subjects))
print('Randomized', len(randomized))
sf = sum(1 for s in subjects if s['Status'] == 'Screen Failure')
print('ScreenFailures', sf, f'{sf/len(subjects)*100:.1f}%')
print('Target', sum(s['EnrollmentTarget'] for s in sites), 'Achievement', f'{len(randomized)/sum(s["EnrollmentTarget"] for s in sites)*100:.1f}%')
oq = [q for q in queries if q['QueryStatus'] == 'Open']
print('OpenQueries', len(oq))
print('AvgOpenQueryAge', f"{sum((REF - date.fromisoformat(q['QueryOpenDate'])).days for q in oq)/len(oq):.1f}")
print('OverdueVisits', sum(1 for v in visits if v['VisitStatus'] == 'Overdue'))
wc = [v for v in visits if v['VisitStatus'] == 'Completed']
print('WindowCompliance', f"{sum(1 for v in wc if v['WindowStatus']=='In Window')/len(wc)*100:.1f}%")
mf = sum(1 for f in forms if f['FormStatus'] == 'Missing'); cf = sum(1 for f in forms if f['FormStatus'] == 'Completed')
print('MissingForms', mf, 'Completion', f'{cf/len(forms)*100:.1f}%')
print('TotalAEs', len(aes), 'SAEs', sum(1 for a in aes if a['Serious'] == 'Yes'))
print('OpenMajorDevs', sum(1 for d in devs if d['Severity'] == 'Major' and d['DeviationStatus'] == 'Open'))
print('CriticalLabs', sum(1 for l in labs if l['CriticalFlag'] == 'Yes'), 'of', len(labs))
dt = sum(1 for d in dosing if d['DoseEvent'] == 'Dose Taken')
print('DoseCompliance', f'{dt/len(dosing)*100:.1f}%', 'of', len(dosing))
