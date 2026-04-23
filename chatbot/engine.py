"""
engine.py — orchestrates routing, LLM calls, and memory.
"""

from chatbot import router, llm, domains
from chatbot.memory import Memory


class Engine:
    def __init__(self, memory: Memory, force_domain: str | None = None):
        self.memory = memory
        self.force_domain = force_domain
        self.current_domain = force_domain or "general"

    def respond(self, user_message: str) -> tuple[str, str]:
        # 1. Classify intent
        domain = self.force_domain or router.classify(user_message)
        self.current_domain = domain

        # 2. Get domain system prompt
        system_prompt = domains.get_system_prompt(domain)

        # 3. Save user message
        self.memory.add("user", user_message, domain=domain)

        # 4. Call LLM
        try:
            response = llm.chat(
                messages=self.memory.get_messages(),
                system_prompt=system_prompt,
            )
        except Exception as e:
            response = f"I ran into an issue: {e}\nPlease check your API key and try again."

        # 5. Run code review pass for programming domain
        if domain == "programming":
            try:
                from chatbot.domains.programming import review_and_fix
                print("\n[review] Running code review pass...")
                response = review_and_fix(response)
                print("[review] Done.\n")
            except Exception as e:
                print(f"\n[review] Review pass failed, using original response. Reason: {e}\n")

        # 6. Post-process (disclaimers, emergency notices)
        response = domains.post_process(domain, response, user_message)

        # 7. Save assistant response
        self.memory.add("assistant", response, domain=domain)

        return response, domain