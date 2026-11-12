# content.json

Full example — `assets/example-content.json` (a fictional candidate).

```jsonc
{
  "lang": "en",                 // uk | ru | en | de | pl | cs | es | fr — section labels and <html lang>
  "theme": "a",                 // a | b | c, can be overridden with --theme
  "name": "Alex Morgan",
  "role": "Senior Backend Engineer · PHP · Laravel · payments",
  "contacts": [                 // header lines; items of a line are joined with " · "
    ["Berlin, Germany", "+49 30 0000 0000"],
    ["alex.morgan@example.com", "linkedin.com/in/alex-morgan-example", "github.com/alex-morgan-example"]
  ],
  "photo": "photo.jpg",         // path relative to content.json; null — no photo
  "summary": "Text, <strong> and &nbsp; allowed",
  "experience": [
    {
      "title": "Senior Backend Engineer",
      "org": "Northwind Pay, fintech, remote",
      "dates": "Aug 2023 — present",
      "bullets": ["<strong>Repository maintainer</strong>: …", "…"]
    }
  ],
  "skills": [                   // group → comma-separated line
    {"group": "Backend", "items": "PHP 8, Laravel, …"}
  ],
  "education": [
    {"school": "Technical University of Munich", "detail": "B.Sc. Computer Science", "years": "2012 — 2016"}
  ],
  "languages": "English — C1 · German — B2 · Spanish — native",
  "labels": {}                  // optional: override section labels
}
```

Text fields are inserted as HTML (you write the content yourself, it is not external input): `<strong>`, `&nbsp;` and `'` are fine. Escape `<` and `&` in plain text.

Default labels:
- uk: Досвід роботи / Ключові навички / Освіта / Мови
- ru: Опыт работы / Ключевые навыки / Образование / Языки
- en: Experience / Core skills / Education / Languages
- de: Berufserfahrung / Kernkompetenzen / Ausbildung / Sprachen
- pl: Doświadczenie zawodowe / Kluczowe umiejętności / Wykształcenie / Języki
- cs: Pracovní zkušenosti / Klíčové dovednosti / Vzdělání / Jazyky
- es: Experiencia / Habilidades clave / Formación / Idiomas
- fr: Expérience / Compétences clés / Formation / Langues

Any other language: set `"lang"` to its code and pass all four labels in `"labels"`.
