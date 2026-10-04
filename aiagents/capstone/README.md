# Supportdesk

An AI customer support assistant that shows its work. A crew of CrewAI agents reads the
customer's account data and the product docs, writes a reply, and the reply is checked
against what the agents actually found before it is sent. When a person has to act, the
ticket is opened for one.

The demo company is fictional and the docs are Supabase's public docs. Every customer and
record is made up.

There are three screens:

| Route | What it is |
|---|---|
| `/` | Landing page. Its demos are real components replaying a recorded ticket |
| `/desk` | Customer view: a chat with a live trace of what the assistant is doing |
| `/team` | Team view: ticket queue, the findings and evidence behind each reply, and a reply form |

## How a message is handled

```text
message ──► router ──┬─ greeting, thanks or too vague ──► immediate reply asking for details
                     ├─ out of scope (legal, abuse, feature request) ──► handed to a person
                     └─ billing / account / technical
                              │
              specialists run (independent ones in parallel), using
              database tools and a hybrid search over the docs
                              │
                       responder writes a draft
                              │
        evaluator lists every claim with a quote from the findings;
        code checks that each quote exists, and that the reply's promises
        about a person match what will really happen
                              │
              pass ──► reply         fail ──► rewrite (twice at most) ──► hand to a person
```

Things worth knowing about how it decides:

- **A person is needed when** the router sees a request for an action (refund, cancel,
  change) or the database shows a duplicate charge that has not been refunded. This is
  decided from facts before the reply is written, and the reply must say so.
- **If nobody will follow up, the reply may not say anyone will.** Code enforces it.
- **The customer's own numbers are checked.** If they say "$50 extra" and the data shows
  $25, the reply says so instead of agreeing.
- **Conversations continue.** The router and responder see the last three turns as
  context only, never as evidence.

## Setup

You need Python 3.13, Node 22 or newer, and API keys for Gemini and Pinecone. Groq is
optional.

### 1. Backend

```bash
cd aiagents/capstone/backend
python -m venv .venv
.venv\Scripts\activate          # macOS and Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
```

Then fill in `.env`:

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Runs the agents and the embeddings |
| `PINECONE_API_KEY`, `PINECONE_INDEX_NAME` | The vector database for the docs |
| `GROQ_API_KEY` | Leave empty unless `AGENT_LLM=groq`. The name has to exist |
| `AGENT_LLM` | `gemini` (default) or `groq` |
| `CORS_ORIGINS` | Frontend addresses allowed to call the API |

### 2. Pinecone index (once)

The index must use **3072 dimensions** (what `gemini-embedding-001` produces) and cosine:

```python
from pinecone import Pinecone, ServerlessSpec

Pinecone(api_key="YOUR_KEY").create_index(
    name="customer-support",
    dimension=3072,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
)
```

### 3. The knowledge base

Fetch the support-relevant parts of the Supabase docs (Apache-2.0). Run this from the
`backend` folder. The commands use `cp` and `mkdir -p`, so on Windows run them in Git
Bash:

```bash
git clone -c core.longpaths=true --depth 1 --filter=blob:none --sparse https://github.com/supabase/supabase.git _supabase
cd _supabase && git sparse-checkout set apps/docs/content && cd ..

mkdir -p data/docs/supabase/guides
cp -r _supabase/apps/docs/content/guides/platform data/docs/supabase/guides/platform
cp -r _supabase/apps/docs/content/guides/auth data/docs/supabase/guides/auth
cp -r _supabase/apps/docs/content/troubleshooting data/docs/supabase/troubleshooting
cp _supabase/LICENSE data/docs/supabase/LICENSE
```

The `core.longpaths` option matters on Windows: some troubleshooting files have names so
long that git cannot create them otherwise, and the checkout fails with "Filename too
long". You should end up with 395 `.mdx` files.

Then index them:

```bash
python scripts/ingest_docs.py --kb-id supabase --docs-dir data/docs/supabase --base-url https://supabase.com/docs
```

This embeds 2,764 chunks. **On Gemini's free tier that is slow:** embeddings are capped at
100 per minute and 1,000 per day. The script saves progress after every batch, so if it
stops, run the same command again and it resumes. Turning on billing for the project
removes the limits.

### 4. Demo data

```bash
python scripts/seed_db.py
```

This creates `data/support.db` with six fictional customers. Running it again wipes the
database, including any tickets.

### 5. Run

```bash
uvicorn main:app --port 8000
```

The first start can take up to a minute because it loads the reranking model.

### 6. Frontend

```bash
cd ../frontend
npm install
cp .env.example .env            # Windows: copy .env.example .env
npm run dev
```

Open http://localhost:5173. Set `VITE_MOCK=true` in `.env` to run the customer view against
a built-in simulated stream, with no backend and no API quota.

## What to try

Pick a customer on the right of `/desk`. Each has different data behind them:

| Customer | Situation | Try asking |
|---|---|---|
| Alice | Charged twice, subscription inactive, auth errors | Her sample ticket |
| Bob | Healthy account | "Why was I charged $500 yesterday?" |
| Carol | Card declined, project paused | Why her project is paused |
| Dan | Invoice higher than the plan price | Why the invoice was $61.40 |
| Eve | Login redirect errors | Her sample ticket, then "it's still not working" |
| Frank | Duplicate charge already refunded | "Was I charged twice?" |

Then open `/team` to see the ticket, the evidence behind each sentence, and the reply form
for tickets that need a person.

## API

| Method and path | Purpose |
|---|---|
| `POST /tickets/stream` | Handle a message and stream progress as server-sent events |
| `POST /tickets` | The same, returning only the final reply |
| `GET /conversations/{id}?customer_id=` | A customer's own thread |
| `GET /team/tickets` | Ticket list |
| `GET /team/tickets/{id}` | Full ticket: findings, drafts, evidence |
| `GET /team/conversations/{id}` | A whole conversation |
| `POST /team/tickets/{id}/resolve` | Record a person's reply |
| `GET /health` | Liveness |

## Limits

- **Gemini's free tier allows 15 requests per minute** for the model used here, and one
  ticket takes roughly 10 to 15 calls. Expect about one full ticket per minute. Real
  traffic needs billing.
- **The team view and its API have no login.** They expose the assistant's internal work
  and are open for the demo. They need authentication before any real use.
- **The customer id comes from the request.** Fine for a demo with no sign-in. A real
  deployment must take it from the authenticated session.
- **There is no automated test suite yet.** The project was checked with throwaway scripts
  and live runs, which are not committed.
- **Not deployed.** Nothing here is set up for hosting yet.
- A reply's "confirmed" or "I can see" language still depends on the model following its
  instructions. Code verifies quotes, numbers and promises, but cannot judge whether a real
  quote truly supports a claim.

## Layout

```text
backend/
  main.py                 API
  support_pipeline.py     the process above
  agents.py, tasks.py     agent roles and their instructions
  crew_tools.py           what each agent may call, locked to one customer
  services/
    customer_data_service.py   database lookups
    knowledge_service.py       document search (hybrid retrieval and reranking)
    reply_verifier.py          quote, number and promise checks
    handoff.py                 does a person need to see this?
    ticket_store.py, conversation_store.py, conversation_context.py
  scripts/seed_db.py, ingest_docs.py
frontend/
  src/pages/              Landing, Desk, Queue, TicketPage
  src/components/         crew map, activity trace, evidence receipts, messages
  src/lib/                stream client, reducer, conversation helpers
```
