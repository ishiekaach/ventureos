from itertools import combinations
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

STOPWORDS = {"agent", "tool", "workflow", "the", "and", "for", "with", "from", "into", "using", "that", "this"}

def _document(agent: dict) -> str:
    fields = [agent.get("name", ""), agent.get("description", ""), agent.get("category", ""),
              agent.get("inputs", ""), agent.get("outputs", "")]
    return " ".join(str(x) for x in fields if x)

def detect_overlaps(agents: list[dict], threshold: float = 0.25):
    if len(agents) < 2:
        return []
    docs = [_document(a) for a in agents]
    matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(docs)
    scores = cosine_similarity(matrix)
    results = []
    for i, j in combinations(range(len(agents)), 2):
        score = float(scores[i, j])
        if score >= threshold:
            a, b = agents[i], agents[j]
            shared = sorted(set(re.findall(r"[a-zA-Z]{3,}", docs[i].lower())) &
                            set(re.findall(r"[a-zA-Z]{3,}", docs[j].lower())) - STOPWORDS)
            if score >= 0.55:
                recommendation = "Review for consolidation"
            elif score >= 0.35:
                recommendation = "Investigate partial overlap"
            else:
                recommendation = "Monitor; overlap may be limited"
            results.append({"agent_a": a.get("name"), "agent_b": b.get("name"),
                            "similarity": score, "shared_terms": shared[:8],
                            "recommendation": recommendation,
                            "caveat": "Text similarity is a triage signal, not proof of duplicate functionality."})
    return sorted(results, key=lambda x: x["similarity"], reverse=True)
