import os
import json
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

NOTES_PATH = "data/notes.txt"

# Load default notes from file
with open(NOTES_PATH, "r", encoding="utf-8") as f:
    default_notes = f.read()


def split_chunks(text, chunk_size=350):
    words = text.split()
    chunks = []
    current = []
    length = 0

    for w in words:
        current.append(w)
        length += len(w) + 1

        if length >= chunk_size:
            chunks.append(" ".join(current))
            current = []
            length = 0

    if current:
        chunks.append(" ".join(current))

    return chunks


def embed(text):
    if not text or text.strip() == "":
        return None

    res = genai.embed_content(
        model="text-embedding-004",  
        content=text,
    )
    return res["embedding"]


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_rag_answer(question, user_notes="", mode="general"):
    """
    Small RAG helper:
      - Pulls useful chunks from the notes (default or user input).
      - Sends those chunks + your question to Gemini.
      - Gemini replies depending on the mode you choose 
        (general answer, summary, quiz style or explain like I'm five).

    Returns:
        answer_text, tokens_used, from_cache
    """

    cache_path = "cache/answers.json"
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
    else:
        cache = {}

    cache_key = f"{mode}::{question}"
    if cache_key in cache:
        return cache[cache_key], 0, True

    source_text = user_notes.strip() if user_notes.strip() else default_notes

    chunks = split_chunks(source_text)
    chunk_embeddings = []

    for c in chunks:
        emb = embed(c)
        chunk_embeddings.append(emb)

    q_emb = embed(question)

    scored = []
    for i, c_emb in enumerate(chunk_embeddings):
        if c_emb is not None and q_emb is not None:
            score = cosine(q_emb, c_emb)
            scored.append((score, chunks[i]))

    if not scored:
        top_sections = [source_text[:500]]
    else:
        scored.sort(reverse=True, key=lambda x: x[0])
        top_sections = [s[1] for s in scored[:2]]

    context_text = "\n\n".join(top_sections)

    if mode == "summary":
        task_instruction = (
            "Summarize the key points from the notes in EXACTLY 3–5 bullet points.\n"
            "IMPORTANT RULES:\n"
            "• Every bullet MUST start with '•'.\n"
            "• Each bullet MUST be on its own line.\n"
            "• Never use paragraphs.\n"
            "• Never use '-' or '*' — ONLY '•'."
        )
    elif mode == "quiz":
        task_instruction = (
            "Create 3–5 short quiz questions WITH answers based on these notes "
            "to help the student review."
        )
    else:  
        task_instruction = (
            "Answer the question using the notes as the main source. "
            "Keep it short, clear, and focused on healthy eating."
        )

    # ---- Build the final prompt for Gemini ----
    prompt = f"""
    You are a friendly, normal-sounding study buddy helping a student with their healthy eating notes.

    Here are the notes (they can be default or pasted by the user):
    {context_text}

    Task: {task_instruction}

    Student's question:
    {question}

    FORMAT RULES:
    • Use short bullet points whenever possible.
    • Put EACH bullet on its own line.
    • Add a blank line between major ideas.
    • Keep the answer clean, simple, and organized.
    • Do NOT write long paragraphs.
    • Do NOT put bullets into a single line.
    • Output should be visually easy to read.

    Now write your answer in a warm, human tone please.
    """
    model = genai.GenerativeModel("gemini-2.0-flash-001")
    response = model.generate_content(prompt)
    answer = response.text

    tokens_used = 0 

    cache[cache_key] = answer
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

    return answer, tokens_used, False
