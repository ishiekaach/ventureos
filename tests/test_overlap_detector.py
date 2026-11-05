from modules.overlap_detector import detect_overlaps

def test_similar_agent_descriptions_are_flagged():
    agents = [
        {"name":"Research Agent","description":"Summarizes company profiles and business models","category":"Research","inputs":"company profile","outputs":"company summary"},
        {"name":"Research Assistant","description":"Creates summaries of company profiles and business models","category":"Research","inputs":"company profile","outputs":"company summary"},
    ]
    result = detect_overlaps(agents, 0.1)
    assert len(result) == 1
    assert result[0]["similarity"] > 0
