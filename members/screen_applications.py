"""
Joining-application screener.

1. In Google Forms → Responses → the green Sheets icon → File → Download → CSV.
2. Save it as members/applications.csv
3. Run:  python members/screen_applications.py

It writes members/shortlist.csv with a score and a suggestion
(Approve / Review / Hold) for every applicant. You make the final call.
Keep applications.csv and shortlist.csv OUT of GitHub (they hold people's data);
the .gitignore already blocks them.
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IN_FILE = HERE / "applications.csv"
OUT_FILE = HERE / "shortlist.csv"

# Words are matched in lower case inside the answer to each question.
SENIOR = ["head", "director", "vp", "vice president", "gm", "general manager", "senior manager",
          "manager", "lead", "chief", "coo", "cxo", "founder", "principal"]
OPS_FIELDS = ["logistics", "last mile", "last-mile", "delivery", "warehouse", "warehousing", "supply chain",
              "fulfilment", "fulfillment", "operations", "ops", "quick commerce", "3pl", "freight", "e-commerce",
              "ecommerce", "courier", "transport", "fleet"]
RED_FLAGS = ["recruiter", "hiring agency", "consultancy services", "sales executive", "selling",
             "investment", "crypto", "mlm", "student"]


def find_col(headers, *names):
    """Finds a column whose header contains one of the names (case-insensitive)."""
    for h in headers:
        hl = h.lower()
        if any(n in hl for n in names):
            return h
    return None


def score(row, cols):
    text = " ".join(str(row.get(c) or "") for c in cols.values() if c).lower()
    role = str(row.get(cols["role"]) or "").lower()
    years_raw = str(row.get(cols["years"]) or "")
    s, why = 0, []
    if any(w in role for w in SENIOR):
        s += 40; why.append("senior role")
    if any(w in text for w in OPS_FIELDS):
        s += 35; why.append("ops field")
    digits = "".join(ch for ch in years_raw if ch.isdigit() or ch == ".")
    try:
        years = float(digits) if digits else 0
    except ValueError:
        years = 0
    if years >= 8:
        s += 25; why.append(f"{years:g} yrs")
    elif years >= 4:
        s += 12; why.append(f"{years:g} yrs")
    flags = [w for w in RED_FLAGS if w in text]
    if flags:
        s -= 50; why.append("flag: " + ", ".join(flags))
    verdict = "Approve" if s >= 75 else "Review" if s >= 40 else "Hold"
    return s, verdict, "; ".join(why)


def main() -> int:
    if not IN_FILE.exists():
        print(f"Put the Google Form export at {IN_FILE} first.")
        return 1
    with IN_FILE.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []
    cols = {
        "name": find_col(headers, "name"),
        "role": find_col(headers, "role", "designation", "title"),
        "company": find_col(headers, "company", "organisation", "organization"),
        "industry": find_col(headers, "industry", "sector", "field"),
        "years": find_col(headers, "years", "experience"),
        "city": find_col(headers, "city", "country", "location"),
        "why": find_col(headers, "why", "join", "expect"),
    }
    if not cols["role"]:
        print("Could not find a Role/Designation column. Headers found:", headers)
        return 1
    out = []
    for r in rows:
        s, verdict, why = score(r, cols)
        out.append({
            "Name": r.get(cols["name"], "") if cols["name"] else "",
            "Role": r.get(cols["role"], ""),
            "Company": r.get(cols["company"], "") if cols["company"] else "",
            "Location": r.get(cols["city"], "") if cols["city"] else "",
            "Score": s, "Suggestion": verdict, "Why": why,
        })
    out.sort(key=lambda x: x["Score"], reverse=True)
    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()) if out else ["Name"])
        w.writeheader(); w.writerows(out)
    counts = {v: sum(1 for o in out if o["Suggestion"] == v) for v in ("Approve", "Review", "Hold")}
    print(f"{len(out)} applications → {counts}. Saved {OUT_FILE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
