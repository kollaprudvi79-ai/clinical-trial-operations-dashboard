#!/usr/bin/env python3
"""Synthetic clinical trial operations data generator (seeded, reproducible).
No real or identifiable patient data. Reference 'today' = 2026-09-30."""
import csv, random, os
from datetime import date, timedelta

random.seed(42)
REF = date(2026, 9, 30)
OUT = os.path.expanduser('~/workspace/your_files/clinical-trial-dashboard/data')
os.makedirs(OUT, exist_ok=True)

FIRST = ['James','Mary','Robert','Patricia','John','Jennifer','Michael','Linda','David','Elizabeth','William','Barbara','Richard','Susan','Joseph','Jessica','Thomas','Sarah','Charles','Karen','Daniel','Nancy','Matthew','Lisa','Anthony','Betty','Mark','Margaret','Donald','Sandra']
LAST = ['Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis','Rodriguez','Martinez','Hernandez','Lopez','Gonzalez','Wilson','Anderson','Thomas','Taylor','Moore','Jackson','Martin','Lee','Perez','Thompson','White','Harris','Sanchez','Clark','Lewis','Robinson','Walker']
COUNTRIES = [('United States','North America'),('United States','North America'),('Canada','North America'),
             ('United Kingdom','Europe'),('Germany','Europe'),('France','Europe'),('Spain','Europe'),
             ('Poland','Europe'),('India','Asia-Pacific'),('Australia','Asia-Pacific')]

# ---------------- Sites ----------------
n_sites = 12
sites = []
for i in range(1, n_sites + 1):
    country, region = COUNTRIES[(i - 1) % len(COUNTRIES)]
    sites.append({
        'SiteID': f'S{i:02d}',
        'SiteName': f'Site {i:02d} - {country} Medical Center {i}',
        'Country': country, 'Region': region,
        'PrincipalInvestigator': f'Dr. {random.choice(FIRST)} {random.choice(LAST)}',
        'SiteStatus': 'Active',
        'ActivationDate': (date(2025,1,6) + timedelta(days=random.randint(0,120))).isoformat(),
        'EnrollmentTarget': 40,
    })

# ---------------- Subjects ----------------
subjects = []
sub_seq = 0
for site in sites:
    screened = 35 + random.randint(8, 16)          # screened per site, independent of display target
    act = date.fromisoformat(site['ActivationDate'])
    for _ in range(screened):
        sub_seq += 1
        scr = act + timedelta(days=random.randint(5, 520))
        if scr > REF: scr = REF - timedelta(days=random.randint(1, 30))
        r = random.random()
        if r < 0.22:                                    # screen failure ~22%
            status, rdate, arm = 'Screen Failure', '', ''
        elif r < 0.26:                                  # screened, awaiting randomization
            status, rdate, arm = 'Screened', '', ''
        else:
            rdate = scr + timedelta(days=random.randint(3, 21))
            if rdate > REF: rdate = REF - timedelta(days=random.randint(1, 10))
            arm = random.choice(['Treatment A','Treatment B'])
            s2 = random.random()
            status = 'Randomized' if s2 < 0.78 else ('Completed' if s2 < 0.90 else 'Withdrawn')
        subjects.append({
            'SubjectID': f'SUB-{sub_seq:04d}', 'SiteID': site['SiteID'],
            'ScreenDate': scr.isoformat(), 'RandomizationDate': rdate if isinstance(rdate,str) else (rdate.isoformat() if rdate else ''),
            'Status': status,
            'AgeGroup': random.choice(['18-40','41-55','56-65','65+']),
            'Sex': random.choice(['Female','Male']),
            'TreatmentArm': arm,
        })
by_id = {s['SubjectID']: s for s in subjects}
randomized = [s for s in subjects if s['RandomizationDate']]
screened_all = subjects[:]

# ---------------- Visits & Forms ----------------
VISIT_PLAN = [('Screening', -14), ('Baseline', 0), ('Week 2', 14), ('Week 4', 28), ('Week 8', 56), ('Week 12', 84), ('Week 24', 168)]
FORM_NAMES = ['Demographics','Vital Signs','Laboratory Results','ECG','Concomitant Medications','Efficacy Assessment']
visits, forms = [], []
v_seq = f_seq = 0
for s in subjects:
    anchor = date.fromisoformat(s['RandomizationDate']) if s['RandomizationDate'] else date.fromisoformat(s['ScreenDate'])
    for vname, offset in VISIT_PLAN:
        if vname != 'Screening' and not s['RandomizationDate']:
            continue
        v_seq += 1
        planned = anchor + timedelta(days=offset)
        if planned > REF + timedelta(days=30):
            vstatus, actual = 'Scheduled', ''
        else:
            rr = random.random()
            if rr < 0.86:
                vstatus = 'Completed'; actual = planned + timedelta(days=random.randint(-2, 3))
            elif rr < 0.93:
                vstatus, actual = 'Overdue', ''
            else:
                vstatus, actual = 'Missed', ''
            if planned > REF and vstatus != 'Completed':
                vstatus, actual = 'Scheduled', ''
        vid = f'V{v_seq:05d}'
        window = ''
        if vstatus == 'Completed':
            delta = (actual - planned).days
            window = 'In Window' if abs(delta) <= 3 else 'Out of Window'
        visits.append({'VisitID': vid, 'SubjectID': s['SubjectID'], 'VisitName': vname,
                       'PlannedDate': planned.isoformat(), 'ActualDate': (actual.isoformat() if isinstance(actual, date) else actual),
                       'VisitStatus': vstatus, 'WindowStatus': window})
        # Forms: Screening visit has 2 forms; others carry full set
        vforms = FORM_NAMES[:2] if vname == 'Screening' else FORM_NAMES
        for fname in vforms:
            f_seq += 1
            if vstatus == 'Completed':
                fstatus = 'Completed' if random.random() < 0.93 else 'Missing'
            elif vstatus in ('Overdue','Missed'):
                fstatus = 'Missing' if random.random() < 0.7 else 'Completed'
            else:
                fstatus = 'Missing' if random.random() < 0.5 else 'Completed'
            comp = ''
            if fstatus == 'Completed':
                comp = (planned + timedelta(days=random.randint(0, 5))).isoformat()
            forms.append({'FormID': f'F{f_seq:05d}', 'SubjectID': s['SubjectID'], 'VisitName': vname, 'FormName': fname,
                          'FormStatus': fstatus, 'DueDate': planned.isoformat(), 'CompletionDate': comp})

# ---------------- Queries ----------------
QTEXT = {
    'Vital Signs': ['Systolic BP value appears out of plausible range - please verify',
                    'Heart rate missing at this visit - please enter or confirm not done'],
    'Laboratory Results': ['Lab value flagged critical - please confirm repeat test performed',
                           'Lab sample date differs from visit date - please clarify'],
    'Demographics': ['Year of birth inconsistent with age at screening - please verify',
                     'Sex field blank - please complete'],
    'ECG': ['ECG interpretation not recorded - please complete',
            'ECG date is before visit date - please clarify'],
    'Concomitant Medications': ['Medication start date after stop date - please correct',
                                 'Indication for medication not specified - please add'],
    'Efficacy Assessment': ['Primary endpoint score missing - please enter',
                            'Score inconsistent with previous visit - please confirm'],
}
queries = []
q_seq = 0
for f in forms:
    if random.random() < 0.10:
        q_seq += 1
        opened = date.fromisoformat(f['DueDate']) + timedelta(days=random.randint(1, 20))
        if opened > REF: opened = REF - timedelta(days=random.randint(0, 5))
        r = random.random()
        if r < 0.45:
            qstatus, closed = 'Open', ''
        elif r < 0.70:
            qstatus, closed = 'Answered', (opened + timedelta(days=random.randint(1, 15))).isoformat()
        else:
            qstatus, closed = 'Closed', (opened + timedelta(days=random.randint(1, 20))).isoformat()
        if closed and closed > REF.isoformat(): qstatus, closed = 'Open', ''
        if qstatus == 'Open':
            opened = REF - timedelta(days=random.randint(1, 120))
        queries.append({'QueryID': f'Q{q_seq:05d}', 'SubjectID': f['SubjectID'], 'FormName': f['FormName'],
                        'QueryText': random.choice(QTEXT[f['FormName']]),
                        'QueryOpenDate': opened.isoformat(),
                        'QueryCloseDate': closed if isinstance(closed, str) else '',
                        'QueryStatus': qstatus})

# ---------------- Adverse Events ----------------
AE_TERMS = ['Headache','Nausea','Fatigue','Dizziness','Injection site pain','Diarrhea','Rash','Insomnia',
            'Back pain','Hypertension','Upper respiratory tract infection','Decreased appetite',
            'Myalgia','Constipation','Vomiting','Pyrexia','Anemia','Elevated liver enzymes']
OUTCOMES = ['Recovered','Recovering','Ongoing','Recovered with sequelae']
aes = []
a_seq = 0
for s in randomized:
    n_ae = random.choices([0, 1, 2, 3], weights=[55, 25, 13, 7])[0]
    for _ in range(n_ae):
        a_seq += 1
        start = date.fromisoformat(s['RandomizationDate']) + timedelta(days=random.randint(1, 160))
        if start > REF: start = REF - timedelta(days=random.randint(1, 15))
        serious = 'Yes' if random.random() < 0.08 else 'No'
        grade = random.choices([1,2,3,4,5], weights=[45,35,14,4,2])[0]
        if serious == 'Yes' and grade < 3: grade = 3
        aes.append({'AEID': f'AE{a_seq:05d}', 'SubjectID': s['SubjectID'],
                    'AETerm': random.choice(AE_TERMS),
                    'StartDate': start.isoformat(), 'SeverityGrade': grade,
                    'Serious': serious, 'Outcome': random.choice(OUTCOMES),
                    'RelatedToStudyDrug': random.choice(['Yes','No'])})

# ---------------- Deviations ----------------
DEV_CATS = ['Visit Window','Inclusion/Exclusion Criteria','Study Drug Dosing','Laboratory Procedure','Informed Consent','Prohibited Medication']
devs = []
d_seq = 0
for s in randomized:
    if random.random() < 0.35:
        for _ in range(random.choices([1,2], weights=[80,20])[0]):
            d_seq += 1
            ddate = date.fromisoformat(s['RandomizationDate']) + timedelta(days=random.randint(5, 150))
            if ddate > REF: ddate = REF - timedelta(days=random.randint(1, 20))
            sev = 'Major' if random.random() < 0.28 else 'Minor'
            dstatus = 'Open' if random.random() < 0.45 else 'Closed'
            devs.append({'DeviationID': f'DEV{d_seq:04d}', 'SubjectID': s['SubjectID'],
                         'DeviationDate': ddate.isoformat(), 'Category': random.choice(DEV_CATS),
                         'Severity': sev, 'DeviationStatus': dstatus})

def dump(name, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(name, len(rows))

dump('Sites.csv', sites); dump('Subjects.csv', subjects); dump('Visits.csv', visits)
dump('Forms.csv', forms); dump('Queries.csv', queries)
dump('AdverseEvents.csv', aes); dump('Deviations.csv', devs)

# Validation stats for the guide
print('---VALIDATION---')
print('TotalSubjects', len(subjects))
print('Randomized', len(randomized))
sf = sum(1 for s in subjects if s['Status'] == 'Screen Failure')
print('ScreenFailures', sf, 'rate', round(sf/len(subjects)*100, 1))
print('OpenQueries', sum(1 for q in queries if q['QueryStatus'] == 'Open'))
ages = [(REF - date.fromisoformat(q['QueryOpenDate'])).days for q in queries if q['QueryStatus'] == 'Open']
print('AvgOpenQueryAge', round(sum(ages)/len(ages), 1))
print('OverdueVisits', sum(1 for v in visits if v['VisitStatus'] == 'Overdue'))
mf = sum(1 for f in forms if f['FormStatus'] == 'Missing')
cf = sum(1 for f in forms if f['FormStatus'] == 'Completed')
print('MissingForms', mf, 'FormCompletion%', round(cf/len(forms)*100, 1))
print('TotalAEs', len(aes), 'SAEs', sum(1 for a in aes if a['Serious'] == 'Yes'))
print('OpenMajorDevs', sum(1 for d in devs if d['Severity'] == 'Major' and d['DeviationStatus'] == 'Open'))
