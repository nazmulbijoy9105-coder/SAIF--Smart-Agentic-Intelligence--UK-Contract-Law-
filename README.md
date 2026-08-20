# SAIF LexQuintet — ILRMF v3.1 Production Bundle

This ZIP contains the final production patch set prepared for the SAIF repository.

## Production architecture

Vercel frontend → Render FastAPI backend → Gemini + Supabase.

There is no localhost fallback in the production frontend configuration and no Groq dependency in this v3.1 bundle.

## Key engine model

The legal-analysis flow is:

FACTS → EVIDENCE → LEGAL PREDICATE → DEPENDENCY → REMEDY

Material unresolved predicates remain `CONDITIONAL` or `DISPUTED` rather than being converted automatically into a definitive legal conclusion.

FJR is an analytical layer. It does not independently establish that a clause is valid or void.

## Included production files

- backend/app/ilrmf/engine.py
- backend/app/ilrmf/fjr_engine.py
- backend/app/corpus/phase1_cases.py
- backend/app/corpus/statutes.py
- backend/app/routers/assess.py
- backend/app/validators/citation_checker.py
- backend/app/utils/pii_masker.py
- backend/app/tests/test_saif.py
- backend/main.py
- backend/build.sh
- backend/requirements.txt
- backend/runtime.txt
- backend/render.yaml
- backend/schema.sql
- backend/.env.example
- frontend/lib/api.ts
- frontend/app/assess/page.tsx
- frontend/app/result/page.tsx
- frontend/next.config.js
- frontend/vercel.json
- frontend/.env.example
- frontend/package.json
- frontend/tsconfig.json
- frontend/next-env.d.ts

## Deployment

### Vercel
Set:

`NEXT_PUBLIC_API_URL=https://YOUR-RENDER-SERVICE.onrender.com`

### Render
Set:

`AI_PROVIDER=gemini`

`GEMINI_API_KEY=...`

`GEMINI_MODEL=...`

`DATABASE_URL=...`

`SUPABASE_URL=...`

`SUPABASE_KEY=...`

`JWT_SECRET=...`

`CORS_ORIGINS=https://YOUR-VERCEL-DOMAIN.vercel.app`

Do not expose Gemini, database or JWT secrets through `NEXT_PUBLIC_*` variables.

## Integration note

This bundle is the final **production patch set for the files discussed in this conversation**. It is not a byte-for-byte export of every unchanged file already present in the GitHub repository. Merge/replace these files in the existing repository while retaining unchanged modules such as authentication, health, payment, database connector, styling and dashboard code.

## Validation

Backend:

```bash
cd backend
pytest -q
```

Frontend:

```bash
cd frontend
npm install
npm run build
```

## Legal disclaimer

SAIF is an AI-assisted legal research and analysis system. Output is not legal advice and requires independent professional verification.
