# Why the design looks like this

Summary of open-source research (collected November 2026). Reliable primary data is scarce: most "percentages" online are retellings without a source, and they contradict each other. Only what is at least somewhat confirmed is listed here.

## Fonts

| Source | Finding | Reliability |
|---|---|---|
| Survey of 1,003 hiring managers, September 2024 (Creative Fabrica, Resumly) | 25 fonts, top 3: **Times New Roman, Arial, Helvetica**; worst — Consolas, Roboto Mono, Comfortaa | Largest survey, author not firmly established |
| CareerBuilder, 2017 (retellings) | Arial, Calibri and Times New Roman are used most | Secondary sources only |
| Errol Morris experiment in the NYT, 2012, ~45k readers | Text set in **Baskerville** was believed more often, Comic Sans least | Real experiment, small effect |
| Guides consensus (Indeed, Seek, Enhancv) | Body 10–12 pt, headings 14–16 pt, one font family | Consensus |

## Colour and layout

| Source | Finding |
|---|---|
| TheLadders, 2018, eye-tracking | First pass takes about **7.4 s**. Worse: **multiple columns**, dense text, little white space. Better: bold job titles, clear section headings, bullet points |
| Canva and Sago, 2025, 5,000 managers in 8 countries | 55–62% prefer resumes with colour |
| Another recruiter survey (Yahoo) | 73% want fully black and white — contradicts Canva |
| MWAIS, 2007, pilot | **Blue** as the main colour inspires the most trust, black the least |

Conclusion: one restrained accent on headings, dark text on white, dark blue works best. One column.

## Themes in build_resume.py

| Theme | Font | Accent | When to offer |
|---|---|---|---|
| `a` (default) | Arial | `#1f3a5f` dark blue | always first |
| `b` | Georgia | `#2e5a4c` dark green | when a warmer, more formal look is wanted; a serif close to Baskerville |
| `c` | Helvetica | `#333333` graphite | conservative companies, finance and law |

All three fonts ship with macOS and Windows and cover Cyrillic. Calibri is missing on macOS by default. Times New Roman tops the survey but looks dated on screen, so it is not used.

## Sources

- https://www.creativefabrica.com/the-artistry/fonts-and-digital-designs/study-hiring-managers-rank-popular-resume-fonts/
- https://www.resumly.ai/blog/psychology-of-resume-design
- https://thejournal.ie/is-baskerville-the-most-convincing-typeface-565049-Aug2012
- https://www.archpaper.com/2015/05/typography-truth-a-conversation-with-errol-morris/
- https://www.hrdive.com/news/eye-tracking-study-shows-recruiters-look-at-resumes-for-7-seconds/
- https://csuglobal.edu/sites/default/files/blog-files/theladders-eyetracking-studyc2.pdf
- https://www.hrkatha.com/features/research/want-to-get-hired-try-visual-resumes-in-colour-survey/
- https://news.yahoo.com/craft-perfect-resume-according-recruiters-110019114.html
- https://aisel.aisnet.org/mwais2007/16
- https://www.indeed.com/career-advice/resumes-cover-letters/color-in-resume
- https://enhancv.com/blog/ats-friendly-fonts
