"""Domain modules — education, healthcare, finance, programming."""

from chatbot.domains import education, healthcare, finance, programming

_DOMAIN_MAP = {
    "education":   education,
    "healthcare":  healthcare,
    "finance":     finance,
    "programming": programming,
}


def get_system_prompt(domain: str) -> str:
    module = _DOMAIN_MAP.get(domain)
    if module and hasattr(module, "get_system_prompt"):
        return module.get_system_prompt()
    return "You are a helpful, honest, and friendly assistant."


def post_process(domain: str, response: str, user_message: str = "") -> str:
    module = _DOMAIN_MAP.get(domain)
    if not module:
        return response
    if domain == "healthcare":
        if hasattr(module, "is_emergency") and module.is_emergency(user_message):
            response = module._EMERGENCY_RESPONSE + "\n\n" + response
        if hasattr(module, "add_disclaimer"):
            response = module.add_disclaimer(response)
    elif domain == "finance":
        if hasattr(module, "add_disclaimer"):
            response = module.add_disclaimer(response)
    return response