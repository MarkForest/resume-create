#!/usr/bin/env python3
"""Build a one-page A4 resume PDF from content.json via headless Chrome.

Usage:
  build_resume.py content.json --out resume.pdf [--theme a|b|c] [--preview preview.png] [--html out.html]

The script renders at scale 1.0 and steps the scale down until the PDF fits on one page,
then prints the scale it used. Layout: one column, header with photo on the right.
Needs only Python 3 and Google Chrome / Chromium / Edge (set CHROME_PATH if it is not found).
Section labels: uk, ru, en, de, pl, cs, es, fr (override with "labels" in content.json).
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

THEMES = {
    "a": dict(font='Arial, "Helvetica Neue", sans-serif', accent="#1f3a5f",
              ink="#1d2329", body="#2b3137", muted="#5d6670"),
    "b": dict(font='Georgia, "PT Serif", serif', accent="#2e5a4c",
              ink="#1f2523", body="#2c3331", muted="#5f6a66"),
    "c": dict(font='Helvetica, Arial, sans-serif', accent="#333333",
              ink="#111111", body="#262626", muted="#666666"),
}

LABELS = {
    "uk": dict(experience="Досвід роботи", skills="Ключові навички", education="Освіта", languages="Мови"),
    "ru": dict(experience="Опыт работы", skills="Ключевые навыки", education="Образование", languages="Языки"),
    "en": dict(experience="Experience", skills="Core skills", education="Education", languages="Languages"),
    "de": dict(experience="Berufserfahrung", skills="Kernkompetenzen", education="Ausbildung", languages="Sprachen"),
    "pl": dict(experience="Doświadczenie zawodowe", skills="Kluczowe umiejętności", education="Wykształcenie", languages="Języki"),
    "cs": dict(experience="Pracovní zkušenosti", skills="Klíčové dovednosti", education="Vzdělání", languages="Jazyky"),
    "es": dict(experience="Experiencia", skills="Habilidades clave", education="Formación", languages="Idiomas"),
    "fr": dict(experience="Expérience", skills="Compétences clés", education="Formation", languages="Langues"),
}

SCALES = [1.0, 0.97, 0.94, 0.91, 0.88, 0.85, 0.82]

CHROME_CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chromium-browser") or "",
    shutil.which("google-chrome-stable") or "", shutil.which("microsoft-edge") or "",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def css(t, s):
    pt = lambda v: f"{v * s:.2f}pt"
    mm = lambda v: f"{v * s:.2f}mm"
    return f"""
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #fff; }}
body {{ font-family: {t['font']}; color: {t['body']}; font-size: {pt(9.5)}; line-height: 1.34;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.page {{ width: 210mm; padding: {mm(10)} 13mm {mm(8)} 13mm; }}
header {{ display: flex; justify-content: space-between; align-items: center; gap: 8mm;
         padding-bottom: {mm(3.2)}; border-bottom: 1.4pt solid {t['accent']}; margin-bottom: {mm(3.6)}; }}
h1 {{ font-size: {pt(22)}; line-height: 1.1; color: {t['ink']}; font-weight: 700; }}
.role {{ font-size: {pt(11.5)}; color: {t['accent']}; font-weight: 700; margin: {mm(1)} 0 {mm(2)}; }}
.contacts {{ font-size: {pt(9.2)}; color: {t['muted']}; line-height: 1.5; }}
.contacts b {{ color: {t['ink']}; font-weight: 400; }}
.photo {{ width: {mm(26)}; height: {mm(30)}; border-radius: 2.5mm; overflow: hidden; flex: none; }}
.photo img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 30%; display: block; }}
h2 {{ font-size: {pt(12)}; font-weight: 700; color: {t['accent']};
     margin: {mm(3.4)} 0 {mm(1.6)}; padding-bottom: .7mm; border-bottom: .6pt solid #d6d9dc; }}
.summary {{ font-size: {pt(9.6)}; }}
.job {{ margin-bottom: {mm(2)}; break-inside: avoid; }}
.job-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 4mm; }}
.job-title {{ font-weight: 700; color: {t['ink']}; font-size: {pt(10.2)}; }}
.job-title span {{ font-weight: 400; color: {t['muted']}; }}
.dates {{ color: {t['muted']}; font-size: {pt(9)}; white-space: nowrap; }}
ul {{ margin: .5mm 0 0 4.2mm; }}
li {{ margin-bottom: .3mm; padding-left: .6mm; }}
li::marker {{ color: {t['accent']}; }}
li strong {{ color: {t['ink']}; }}
.skills {{ display: grid; grid-template-columns: 30mm 1fr; row-gap: .6mm; column-gap: 3mm; }}
.skills dt {{ font-weight: 700; color: {t['ink']}; }}
.two {{ display: grid; grid-template-columns: 1.35fr 1fr; gap: 8mm; }}
.two p {{ margin-bottom: .6mm; }}
.muted {{ color: {t['muted']}; white-space: nowrap; }}
"""


def html(c, theme, scale, photo_name):
    lab = dict(LABELS.get(c.get("lang", "en"), LABELS["en"]))
    lab.update(c.get("labels") or {})
    contacts = "<br>".join(" · ".join(f"<b>{x}</b>" for x in row) for row in c.get("contacts", []))
    photo = f'<div class="photo"><img src="{photo_name}" alt=""></div>' if photo_name else ""
    jobs = []
    for j in c.get("experience", []):
        org = f' <span>· {j["org"]}</span>' if j.get("org") else ""
        lis = "".join(f"<li>{b}</li>" for b in j.get("bullets", []))
        jobs.append(f'<div class="job"><div class="job-head"><div class="job-title">{j["title"]}{org}</div>'
                    f'<div class="dates">{j.get("dates", "")}</div></div><ul>{lis}</ul></div>')
    skills = "".join(f'<dt>{g["group"]}</dt><dd>{g["items"]}</dd>' for g in c.get("skills", []))
    edu = "".join(
        f'<p><strong>{e["school"]}</strong>' + (f' — {e["detail"]}' if e.get("detail") else "")
        + (f' <span class="muted">· {e["years"]}</span>' if e.get("years") else "") + "</p>"
        for e in c.get("education", []))
    langs = c.get("languages", "")
    bottom = ""
    if edu or langs:
        bottom = (f'<div class="two"><div><h2>{lab["education"]}</h2>{edu}</div>'
                  f'<div><h2>{lab["languages"]}</h2><p>{langs}</p></div></div>')
    return f"""<!doctype html><html lang="{c.get('lang', 'en')}"><head><meta charset="utf-8">
<title>{c.get('name', 'Resume')}</title><style>{css(THEMES[theme], scale)}</style></head><body><div class="page">
<header><div><h1>{c['name']}</h1><div class="role">{c.get('role', '')}</div><div class="contacts">{contacts}</div></div>{photo}</header>
<div class="summary">{c.get('summary', '')}</div>
<h2>{lab['experience']}</h2>{''.join(jobs)}
<h2>{lab['skills']}</h2><dl class="skills">{skills}</dl>
{bottom}
</div></body></html>"""


def pages(pdf):
    return len(re.findall(rb"/Type\s*/Page[^s]", Path(pdf).read_bytes()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content")
    ap.add_argument("--out", required=True)
    ap.add_argument("--theme", choices=THEMES)
    ap.add_argument("--preview")
    ap.add_argument("--html")
    a = ap.parse_args()

    chrome = next((p for p in CHROME_CANDIDATES if p and os.path.exists(p)), None)
    if not chrome:
        sys.exit("Chrome, Chromium or Edge not found — install one or set CHROME_PATH")
    src = Path(a.content).resolve()
    c = json.loads(src.read_text(encoding="utf-8"))
    theme = a.theme or c.get("theme", "a")

    work = Path(tempfile.mkdtemp(prefix="resume-build-"))
    try:
        photo_name = None
        if c.get("photo"):
            p = (src.parent / c["photo"]).resolve()
            if not p.exists():
                sys.exit(f"photo not found: {p}")
            photo_name = "photo" + p.suffix.lower()
            shutil.copy(p, work / photo_name)
        prof = work / "chrome-profile"
        run = lambda *args: subprocess.run([chrome, "--headless", "--disable-gpu", f"--user-data-dir={prof}", *args],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        page = work / "resume.html"
        tmp_pdf = work / "out.pdf"
        used = None
        for s in SCALES:
            page.write_text(html(c, theme, s, photo_name), encoding="utf-8")
            run("--no-pdf-header-footer", f"--print-to-pdf={tmp_pdf}", page.as_uri())
            if tmp_pdf.exists() and pages(tmp_pdf) == 1:
                used = s
                break
        if used is None:
            print(f"WARNING: does not fit on one page even at scale {SCALES[-1]} — shorten the text", file=sys.stderr)
            used = SCALES[-1]
        out = Path(a.out).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(tmp_pdf, out)
        if a.html:
            h = Path(a.html).expanduser().resolve()
            h.write_text(page.read_text(encoding="utf-8").replace(f'src="{photo_name}"', f'src="{(src.parent / c["photo"]).resolve()}"') if photo_name else page.read_text(encoding="utf-8"), encoding="utf-8")
        if a.preview:
            prev = Path(a.preview).expanduser().resolve()
            run("--hide-scrollbars", "--window-size=794,1123", "--force-device-scale-factor=1.5",
                f"--screenshot={prev}", page.as_uri())
        print(json.dumps({"pdf": str(out), "pages": pages(out), "scale": used, "theme": theme,
                          "preview": a.preview and str(Path(a.preview).expanduser().resolve())}, ensure_ascii=False))
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
