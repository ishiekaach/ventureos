from modules.overlap_detector import detect_overlaps

def test_similar_agents_are_flagged():
    agents=[
        {"name":"Company Research Agent","description":"Summarizes company profiles and business models for investment research","category":"Research","inputs":"company profile","outputs":"company summary"},
        {"name":"Company Research Assistant","description":"Creates summaries of company profiles and business models for investment screening","category":"Research","inputs":"company profile","outputs":"company summary"},
        {"name":"Calendar Helper","description":"Schedules meetings and sends calendar reminders","category":"Admin","inputs":"meeting date","outputs":"calendar event"},
    ]
    result=detect_overlaps(agents,.1)
    assert result
    assert result[0]["similarity"] > 0
    assert result[0]["agent_a"] != result[0]["agent_b"]
