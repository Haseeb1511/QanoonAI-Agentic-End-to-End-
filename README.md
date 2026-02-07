# Currently in progress  -- Not yet completed

# How to run Backend
```bash

uv run uvicorn backend.app:app --reload  # to run fast api
uv run python -m backend.app # same as above but(not recomeneded with fastAPI)

```

# FronEnd
```bash
npm install
# how to run froned
npm run frontend

```

---
# TOOl used
```bash
React v19
vite 
tailwand css v4
javascript

# Backend 
Fastpai

langchain
langgraph


```



# From:
response = self.llm.invoke(prompt_messages)

# To:
response = self.llm.with_config(tags=["response"]).invoke(prompt_messages)




# upload
fix issue of rewritten query being printed 111
imporve ui    2222 
jwt authenticaiton   6666
docker trest  3333
urdu translation   5555
modulat fastapi   4444
docker fast api ---> aws
frontend  ---> vercel



# Google OAuth 2.0 login + JWT-based authentication/authorization



# How summary Generation work
```bash

User Q1 → Q2 → Q3 (3rd message triggers summarizer)
                    ↓
              Creates summary
                    ↓
              Saved to Supabase
                    ↓
User Q4 → Loads summary from DB
              ↓
        Query Rewriter uses summary
              ↓
        Agent Response uses summary
              ↓
        Summary extended (if messages ≥3 again)

```