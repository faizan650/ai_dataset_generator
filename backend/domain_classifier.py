
def classify_domain(domain_name: str) -> str:
    domain_name = (domain_name or "").lower()
    domain_map = {
        "sql": "text_to_sql",
        "text-to-sql": "text_to_sql",
        "sports": "consulting",
        "fitness": "consulting",
        "finance": "consulting",
        "legal": "consulting",
        "education": "tutoring",
        "code": "code_generation",
        "sentiment": "classification",
        "chatbot": "dialogue",
    }
    for key, value in domain_map.items():
        if key in domain_name:
            return value
    return "generic"
