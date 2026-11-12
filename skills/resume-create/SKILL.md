---
name: resume-create
description: Tailors a resume to one specific job posting and writes a short cover letter for it. Output is a one-page PDF in a research-backed design (single column, Arial, dark-blue accent, photo) plus the letter text, both in the language of the posting. Input is a resume (PDF, DOCX, text or a file path) and the job posting (text or a link). Use this skill whenever the user wants to apply for a job, adapt / rewrite / rephrase a resume or CV for a vacancy, write a cover letter, translate a resume into the language of a posting, or change the photo or look of a resume — even if they never say "resume" (for example "here's the job, here's my CV, make an application", "help me apply to company X", "CV under this job", "вот вакансия, вот моё резюме, сделай отклик", "адаптуй резюме під вакансію", "напиши супровідний лист"). Also for /resume-create.
argument-hint: "[resume path] [job link or text]"
---

# resume-create

Goal: an application a recruiter reads in 7 seconds and believes. A resume in the language of the posting where every bullet answers one of its requirements, plus a short cover letter. Everything comes from the user's real experience — nothing is invented.

This order of steps was shaped on real applications, and almost every step answers a correction a real user made. Do not skip the "ask" and "show" steps: they save rework.

`<skill-dir>` below is the directory containing this SKILL.md (Claude Code shows it as "Base directory for this skill").

## 1. Inputs

Two texts are needed: the **resume** and the **job posting**.

- The resume may come as a path to a PDF/DOCX, an attachment or plain text. If there is no path, look for it yourself:
  `find ~/Downloads ~/Documents ~/Desktop -maxdepth 3 \( -iname '*resume*' -o -iname '*cv*' -o -iname '*резюме*' \) 2>/dev/null`, sort by date (`ls -lt`). Offer the newest one as the base and name the alternatives.
- Read a PDF with the Read tool: you see both the text and the layout. `<skill-dir>/scripts/extract_pdf_photo.py resume.pdf <out_dir>` pulls the photo out of a PDF.
- Take the posting as text or by link (WebFetch). If the paste is cut off (no posting, a sentence ends mid-word), ask what is missing in one message with a list.
- Ask for the acceptance criterion only if the user hinted at one. Default: a resume PDF plus the cover letter text.

## 2. Analyse the posting

Write down for yourself:
- **the language of the posting** — the resume and the letter will be in it (a Ukrainian posting means everything in Ukrainian, an English one — in English, a German one — in German);
- stack and requirements (must-have and nice-to-have), responsibilities, goals for the first months;
- level (junior / middle / senior), work format and city;
- words the company repeats ("network of sites", "24/7", "technical SEO"): mirror them in the text.

For deep company research or a match score you may additionally use a skill like `resume-tailoring` if it is installed. Usually the posting itself is enough.

## 3. Gaps: ask, never invent

Compare the requirements with the resume. Do not add anything the resume lacks. Ask in one AskUserQuestion with `multiSelect: true` which of the missing items the user really did (for example: "Linux / Bash / Nginx", "Technical SEO", "Plain PHP", "Vue or another framework — say which"). In the same call clarify:
- AI tools, if the posting asks for them: daily or occasionally;
- location or format mismatch: ready for the office, remote only, or don't mention.

Add only what was confirmed. If you tie a confirmed skill to a specific job, say so in the report so the user can check the placement.

## 4. Resume text

Tone rules (details and examples in `references/writing-guide.md`):
- **Role or result first, active voice.** Not "My team lead appointed me maintainer of the repository", but "**Repository maintainer**: owned code review…". Phrases where a boss "gave" or "appointed" something read as subordinate; users ask to remove them.
- Every bullet: what you did → how → what changed. Numbers, dates and company names only from the source.
- The headline under the name names the role from the posting: "Full-stack PHP developer · Laravel · Vue · payment integrations".
- Summary: 4–6 lines that answer the main question of the posting.
- Remove or shorten what is irrelevant (e.g. .NET for a PHP role). Keep teaching and mentoring shorter.
- Jobs in strict reverse chronological order by end date.
- Keep technologies and established terms in Latin script (Laravel, code review, Maintainer); abbreviate months the way the language does.

## 5. Build the PDF

Put the content into JSON (schema — `references/content-schema.md`, full example — `assets/example-content.json`) in a working folder, e.g. `~/Documents/resume-src/<company>-<YYYY-MM>/content.json`, with the photo next to it. Then:

```bash
python3 <skill-dir>/scripts/build_resume.py <content.json> --out ~/Downloads/<Name>_<Role>_<Company>_<LANG>.pdf --preview <workdir>/preview.png
```

Needs only Python 3 and Google Chrome, Chromium or Edge (set `CHROME_PATH` if it is not found). The script shrinks the scale step by step until the resume fits on one page and reports the scale it used. After the build **always look at** `preview.png` with the Read tool: a single word on the last line, a cropped photo, an empty third of the page. If the scale fell below 0.9, shorten the text rather than shrink the font.

Default design — theme `a`: one column, Arial, dark blue `#1f3a5f`, white background, photo on the right of the header. It won a side-by-side comparison with two alternatives; the reasons (recruiter surveys, TheLadders eye-tracking, a study on trust in blue) are in `references/design-research.md`. Fallback themes: `b` (Georgia and dark green, warmer and more formal) and `c` (Helvetica and graphite, nearly black and white). If the user asks for "a different look", show these first instead of inventing a new style.

Rejected in testing (do not offer unless asked):
- a dark sidebar with Inter and letter-spaced capitals — "spiky letters, artificial, cold";
- a cream background with Lora + Source Sans and terracotta — "too red"; coffee and olive variants did not work either.

**Photo.** If the user gave a new photo, crop to face and shoulders, ratio about 0.87 (width to height), face at about a third of the height: on macOS `sips -c <h> <w> --cropOffset <y> <x> in.jpg --out photo.jpg`, elsewhere ImageMagick `magick in.jpg -crop <w>x<h>+<x>+<y> photo.jpg`. Check the crop with Read. Without a new photo, take the one from the source PDF (`scripts/extract_pdf_photo.py`). `"photo": null` builds without a photo — suggest that for markets where photos are not expected (US, UK).

File names: ASCII, no spaces — they survive job portals, email clients and Cmd/Ctrl+click in terminals.

## 6. Cover letter

In the language of the posting, 120–200 words, no filler. Structure and an example are in `references/writing-guide.md`:
1. Greeting.
2. Who you are, years of experience, one sentence on why the posting matches your experience.
3. "What I can bring": 3–4 bullets, each closing a specific requirement of the posting.
4. What resonates in the company's tasks: retell their goal in your own words, no flattery.
5. Call to talk and a signature with contacts.

Mention location and format the way the user decided in step 3. Save the letter to `~/Downloads/<company>_cover_letter_<lang>.txt` and put the full text in the answer as a code block so it can be copied.

## 7. Hand-off

In the answer:
- full absolute paths to the PDF and the letter;
- what changed compared to the source resume (short, as bullets);
- what the user must check personally: skills tied to jobs, translated job titles, the photo;
- a request to reply "checked" or send edits. Treat the hand-off as final only after that reply.

Keep the sources (content.json, photo, HTML) in `~/Documents/resume-src/<company>-<YYYY-MM>/` so the next edit takes minutes. Clean up after yourself: the script deletes its temporary Chrome profile itself; leave no background processes.
