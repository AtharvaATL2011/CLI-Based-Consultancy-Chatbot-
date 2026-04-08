"""
cli.py — entry point and terminal UI.
"""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from chatbot.memory import Memory, init_db
from chatbot.engine import Engine
from chatbot.router import domain_label
from chatbot.config import VALID_DOMAINS

console = Console()

WELCOME_BANNER = """
[bold]MultiMind[/bold] — your AI companion for learning, health, and finance.

Type your question naturally — I'll detect what kind of help you need.
Type [bold cyan]help[/bold cyan] for commands · [bold cyan]quit[/bold cyan] to exit.
"""

HELP_TEXT = """
[bold]Commands:[/bold]

  [cyan]help[/cyan]        Show this message
  [cyan]clear[/cyan]       Clear conversation history
  [cyan]history[/cyan]     Show message count
  [cyan]domain[/cyan]      Show active domain
  [cyan]quit[/cyan]        Exit
"""


def _print_response(response: str, domain: str) -> None:
    label = domain_label(domain)
    console.print(
        Panel(
            Markdown(response),
            title=f"[bold]{label}[/bold]",
            title_align="left",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def _handle_command(command: str, engine: Engine) -> bool:
    cmd = command.strip().lower()
    if cmd in ("quit", "exit", "q"):
        console.print("\n[dim]Goodbye! 👋[/dim]\n")
        sys.exit(0)
    elif cmd == "help":
        console.print(Panel(HELP_TEXT, title="Help", border_style="dim"))
        return True
    elif cmd == "clear":
        engine.memory.clear()
        console.print("[dim]Session history cleared.[/dim]")
        return True
    elif cmd == "history":
        console.print(f"[dim]{engine.memory.message_count()} message(s) in this session.[/dim]")
        return True
    elif cmd == "domain":
        console.print(f"[dim]Active domain: {domain_label(engine.current_domain)}[/dim]")
        return True
    return False


@click.command()
@click.option("--user", default="default", help="Username for saving conversation history.")
@click.option("--domain", default=None,
              type=click.Choice(list(VALID_DOMAINS), case_sensitive=False),
              help="Force a specific domain.")
@click.option("--no-memory", is_flag=True, default=False, help="Don't save this session.")
def main(user: str, domain: str | None, no_memory: bool) -> None:
    """MultiMind — Education · Healthcare · Finance CLI chatbot."""

    init_db()
    memory = Memory(user=user, resume=not no_memory)
    engine = Engine(memory=memory, force_domain=domain)

    console.print()
    console.print(Panel(WELCOME_BANNER.strip(), border_style="cyan", padding=(1, 2)))

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye! 👋[/dim]\n")
            break

        if not user_input:
            continue
        if _handle_command(user_input, engine):
            continue

        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            response, active_domain = engine.respond(user_input)

        console.print()
        _print_response(response, active_domain)


if __name__ == "__main__":
    main()