# Hailz Helper – Tech Note 

## Overview

```
Haliz Helper is an AI powered study tool that helps users learn healthy eating concepts in a simple and supportive way. 
Users are able to paste notes or use the default notes, ask a question and pick a mode:
GENERAL QUESTION - SUMMARY - QUIZ - EXPLAIN LIKE I'M FIVE

The App runs through a RAG pipeline so the answers are always created based on the notes. 
My goal was to build an App that is fun to use, efficent and educational.
The deisgn mkaes sure to use notes instead of the model making it's own assumptions.
```


## System Architecture

```
┌──────────────────────────────┐
│          Frontend            │
│  index.html + style.css      │
│  User enters: notes,         │
│  question, mode              │
└───────────────┬──────────────┘
                │ POST /api/ask
                ▼
┌─────────────────────────────────────────┐
│               Flask API                 │
│            (app.py: /api/ask)           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│ Safety Layer (safety.py)                 │
│ • Input length guard                     │
│ • Prompt-injection checks                │
│ • System instructions for safe output    │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│      RAG Pipeline (rag.py)               │
│ 1. Load notes                            │
│ 2. Chunk into ~350-word sections         │
│ 3. Embed with text-embedding-004         │
│ 4. Cosine similarity scoring             │
│ 5. Pick top 2 chunks                     │
│ 6. Build structured Gemini prompt        │
│ 7. Generate answer                       │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│ Telemetry (telemetry.py)                 │
│ • timestamp                              │
│ • mode & RAG pathway                     │
│ • latency                                │
│ • whether answer came from cache         │
│ → logged to requests.log                 │
└──────────────────────────────────────────┘
```

## Saftey and Guardrails

In order to keep the model predictable, I implemented:

  - Prompt injection protection
    - Rejects attemps like "ignore previous instructions"
    - Return safe messages like "I cannot do that"

  - Input Length Guard
    - If the question is too long of an input [ a friendly error message comes, instead of crashing]

  - System Rules
    - The model is instructed to:
      - be based on the notes
      - avoid medical claims
      - avoid harmful advice
      - use bullet points for formatting

  - UI stability
    - The front end won't break and errors return nice messages

## Eval Methods

I created:
  - tests.json with 16 evaluation cases
  - run_tests.py as the automated test runner

Each test checks if the expected patterns like "protien", "?" or "•" are in the output

Results:

  The Model passes 12/16 tests consisently becasue:
  - LLM outputs vary slightly between the runs
  - summary formatting sometimes produces bullets in different ways
  - the overall correctness is still good

<img width="725" height="534" alt="image" src="https://github.com/user-attachments/assets/1d0b8e56-75a7-4d1a-b9c5-593c5ed9054d" />

## Known Limits

The limits I noticed are:
- LLM variability
  - the model Gemini occasionally formats bullets in ways that break strict tests
  
- Small context
  - There are only 2 chuncks that are retrieved for simplicity

- Local Browser UI
  - There are no user accounts or authentication
  - Also may look different on mobile

- Output Variations
  - Some outputs don't fully match the test expectations

## Nice to Haves

1. Caching
   - Responsible caching is implemented in the rag.py using answers.json
   - The app includes a lightweight response caching using the json file.
   - Where repeated questions return instantly wihtout re using Gemini.

2. UX
   - I added small UI touches like a centered layout, clean spacing, a loading message
   - Making the app more personal and easy to use

3. Embedding Caching (chunk embedding)

4. Readibility of output
   - Have bullet points in the prompt
   - Replaced \n with <br> for cleaner rendering

5. Optional Notes Input
   - UX flexibility where users can paste custom notes or leave it empty
  
## Conclusion

Hailz Helper ended up being a cute study app that I really had fun creating and using. It is also a fully functional RAG app that is fast, safe, simple and grounded. This assignment helped me understand chuncking, embeddings, prompt structure and how to use a LLM based system.


