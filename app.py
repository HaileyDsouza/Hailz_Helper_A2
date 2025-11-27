from flask import Flask, request, jsonify, render_template
from rag import get_rag_answer
from safety import is_safe_input
from telemetry import log_request
import time

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "").strip()
    notes = data.get("notes", "").strip()
    mode = data.get("mode", "general")

    start = time.time()  # latency timer

    # Safety check
    if not is_safe_input(question):
        return jsonify({
            "answer": "Sorry!! Unsafe input. Please rephrase your question."
        })

    # Empty input guard
    if question == "":
        return jsonify({
            "answer": "Please enter a question "
        })

    try:
        # Try generating the answer
        answer, tokens, cache_hit = get_rag_answer(question, notes, mode)
    except Exception as e:
        answer = "Sorry, something went wrong generating your answer. Please try again."

        latency = time.time() - start
        log_request(question, mode, cache_hit=False, latency=latency)

        return jsonify({
            "answer": answer
        })

    latency = time.time() - start
    log_request(question, mode, cache_hit, latency)

    return jsonify({
        "answer": answer
    })


if __name__ == "__main__":
    app.run(debug=True)
