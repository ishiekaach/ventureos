import json
from config import OPENAI_API_KEY, OPENAI_MODEL

def generate_research(company_name, company_context):
    if not OPENAI_API_KEY:
        return {"mode": "Offline template", "summary": f"Research workspace created for {company_name}. No LLM API key is configured, so no factual claims have been generated.", "investment_questions": ["What evidence supports customer demand and willingness to pay?", "What is the company's differentiated advantage versus alternatives?", "What are the revenue, gross margin, retention, and growth trends?", "What assumptions are missing or unverified?", "What milestones would materially change the investment case?"], "risks": ["Insufficient source information", "Financial and market claims require independent verification"]}
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = f"Use ONLY the context below. Do not invent facts, metrics, sources, market sizes, customers, or funding. Explicitly label missing information. Return JSON with summary, business_model, potential_risks, diligence_questions, missing_information. Company: {company_name}. Context: {company_context}"
        response = client.chat.completions.create(model=OPENAI_MODEL, messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"}, temperature=0.2)
        return {"mode": "LLM-assisted draft; verify every claim", **json.loads(response.choices[0].message.content)}
    except Exception as exc:
        return {"mode": "Offline fallback", "error": str(exc), "summary": "AI service was unavailable. No claims were generated.", "investment_questions": ["What information is still missing?"]}
