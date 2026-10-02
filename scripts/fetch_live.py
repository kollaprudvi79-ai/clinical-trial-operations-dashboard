#!/usr/bin/env python3
"""Fetch LIVE clinical trial data from ClinicalTrials.gov (public API, no key)
and write an aggregated dashboard payload to docs/live-data.json.
Runs in GitHub Actions every few hours; also runnable locally."""
import json, os, statistics, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta
from collections import Counter

API = "https://clinicaltrials.gov/api/v2"
UA = {"User-Agent": "clinical-trial-dashboard-live-fetcher/1.0"}

def get(path, params):
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)

def total(term):
    d = get("/studies", {"query.term": term, "pageSize": 1, "countTotal": "true", "format": "json"})
    return d.get("totalCount", 0)

def main():
    now = datetime.now(timezone.utc)
    today = now.date()
    d30 = (today - timedelta(days=30)).isoformat()
    d365 = (today - timedelta(days=365)).isoformat()

    size = get("/stats/size", {})
    kpis = {
        "totalStudies": size.get("totalStudies"),
        "recruiting": total("AREA[OverallStatus]RECRUITING"),
        "updated30d": total(f"AREA[LastUpdatePostDate]RANGE[{d30},{today}]"),
        "started365d": total(f"AREA[StartDate]RANGE[{d365},{today}]"),
        "completed": total("AREA[OverallStatus]COMPLETED"),
        "terminated": total("AREA[OverallStatus]TERMINATED"),
        "withResults": total("AREA[HasResults]true"),
    }
    phases = {}
    for label, term in [("Phase 1", "PHASE1"), ("Phase 2", "PHASE2"), ("Phase 3", "PHASE3"),
                        ("Phase 4", "PHASE4"), ("Not Applicable", "NA")]:
        phases[label] = total(f"AREA[Phase]{term}")
    statuses = {}
    for st in ["RECRUITING", "NOT_YET_RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION",
               "COMPLETED", "SUSPENDED", "TERMINATED", "WITHDRAWN", "UNKNOWN"]:
        statuses[st.replace("_", " ").title()] = total(f"AREA[OverallStatus]{st}")
    sponsor_class = {}
    for cls in ["INDUSTRY", "NIH", "FED", "OTHER", "NETWORK", "INDIV", "AMBIG"]:
        n = total(f"AREA[LeadSponsorClass]{cls}")
        if n: sponsor_class[cls.title()] = n
    trials_by_year = {}
    for y in range(2014, today.year + 1):
        trials_by_year[str(y)] = total(f"AREA[StartDate]RANGE[{y}-01-01,{y}-12-31]")

    records, token = [], None
    for _ in range(3):
        params = {"query.term": f"AREA[LastUpdatePostDate]RANGE[{d30},{today}]",
                  "pageSize": 1000, "countTotal": "true", "format": "json",
                  "sort": "LastUpdatePostDate:desc"}
        if token: params["pageToken"] = token
        d = get("/studies", params)
        records.extend(d.get("studies", []))
        token = d.get("nextPageToken")
        if not token: break

    def mod(study, name): return study.get("protocolSection", {}).get(name, {})
    conditions, countries, phases_s, inter, sponsors = Counter(), Counter(), Counter(), Counter(), Counter()
    phase_status, elig_sex, min_age_bucket, study_type, enrollment_vals, keywords, interventions_full = {}, Counter(), Counter(), Counter(), [], Counter(), Counter()
    enrollment_sum = 0
    recent, largest = [], []
    for s in records:
        idm = mod(s, "identificationModule"); stm = mod(s, "statusModule")
        des = mod(s, "designModule"); cond = mod(s, "conditionsModule")
        loc = mod(s, "contactsLocationsModule"); arm = mod(s, "armsInterventionsModule")
        sp = mod(s, "sponsorCollaboratorsModule"); elig = mod(s, "eligibilityModule")
        ph = (des.get("phases") or ["Not Specified"])[0]
        phases_s[ph] += 1
        phase_status.setdefault(ph, Counter())[stm.get("overallStatus", "")] += 1
        ec = (des.get("enrollmentInfo", {}) or {}).get("count")
        if ec: enrollment_sum += ec; enrollment_vals.append(ec)
        elig_sex[elig.get("sex", "Unknown")] += 1
        ma = (elig.get("minimumAge") or "").lower()
        first = ma.split()[0] if ma.split() else ""
        if "month" in ma or "week" in ma or (first.isdigit() and int(first) < 18): min_age_bucket["<18 allowed"] += 1
        elif ma: min_age_bucket["18+ only"] += 1
        else: min_age_bucket["Unspecified"] += 1
        study_type[des.get("studyType", "Unknown")] += 1
        for c in cond.get("conditions", [])[:2]: conditions[c] += 1
        for k in cond.get("keywords", [])[:1]: keywords[k] += 1
        for l in loc.get("locations", []):
            if l.get("country"): countries[l["country"]] += 1
        for i in arm.get("interventions", []):
            t = i.get("type")
            if t: interventions_full[t] += 1
        lead = sp.get("leadSponsor", {}).get("name")
        if lead: sponsors[lead] += 1
        row = {"nct": idm.get("nctId", ""), "title": (idm.get("briefTitle") or "")[:110],
               "status": stm.get("overallStatus", ""), "phase": ph, "sponsor": lead or "",
               "updated": stm.get("lastUpdatePostDateStruct", {}).get("date", ""), "enrollment": ec}
        if len(recent) < 40: recent.append(row)
        largest.append(row)
    largest = sorted([r for r in largest if r["enrollment"]], key=lambda r: -r["enrollment"])[:15]

    bins = {"1–50": 0, "51–200": 0, "201–500": 0, "501–1k": 0, "1k–5k": 0, "5k+": 0}
    for v in enrollment_vals:
        if v <= 50: bins["1–50"] += 1
        elif v <= 200: bins["51–200"] += 1
        elif v <= 500: bins["201–500"] += 1
        elif v <= 1000: bins["501–1k"] += 1
        elif v <= 5000: bins["1k–5k"] += 1
        else: bins["5k+"] += 1
    payload = {
        "generatedAt": now.isoformat(timespec="seconds"),
        "source": "ClinicalTrials.gov API v2 (public, no key)",
        "kpis": {**kpis, "sampledRecords": len(records), "sampleEnrollment": enrollment_sum,
                 "medianEnrollment": int(statistics.median(enrollment_vals)) if enrollment_vals else None},
        "byPhase": dict(phases),
        "byStatus": dict(statuses),
        "bySponsorClass": dict(sponsor_class),
        "startedByYear": trials_by_year,
        "sample": {
            "byPhase": dict(phases_s.most_common()),
            "topConditions": conditions.most_common(15),
            "topCountries": countries.most_common(15),
            "topInterventions": interventions_full.most_common(10),
            "topSponsors": sponsors.most_common(15),
            "phaseStatus": {k: dict(v) for k, v in phase_status.items()},
            "eligSex": dict(elig_sex), "minAge": dict(min_age_bucket),
            "studyType": dict(study_type), "enrollmentBins": bins,
        },
        "recent": recent, "largest": largest,
    }
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "live-data.json")
    with open(out, "w") as fh:
        json.dump(payload, fh, separators=(",", ":"))
    print("wrote", out, os.path.getsize(out), "bytes | total", kpis["totalStudies"], "| sample", len(records))

if __name__ == "__main__":
    main()
