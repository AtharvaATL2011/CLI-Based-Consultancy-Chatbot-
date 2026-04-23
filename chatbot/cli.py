"""
cli.py — entry point and terminal UI with multiline paste support.
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
  [cyan]paste[/cyan]       Enter multiline/long prompt mode (for long prompts)
  [cyan]file <path>[/cyan] Load prompt from a text file
  [cyan]quit[/cyan]        Exit

[bold]Paste mode usage:[/bold]
  Type [bold cyan]/paste[/bold cyan] → paste your long prompt → type [bold cyan]END[/bold cyan] on a new line → press Enter
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


def _get_multiline_input() -> str:
    """
    Multiline input mode — handles long prompts without terminal cutoff.
    User enters /paste, pastes content, then types END to submit.
    """
    console.print(
        Panel(
            "[dim]Paste your prompt below.\n"
            "When finished, type [bold]END[/bold] on a new line and press Enter.\n"
            "To cancel, press [bold]Ctrl+C[/bold].[/dim]",
            title="[bold cyan]📋 Paste Mode[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Paste mode cancelled.[/dim]")
            return ""

    result = "\n".join(lines).strip()

    if result:
        preview = result[:80] + "..." if len(result) > 80 else result
        console.print(
            f"\n[dim]✅ Captured {len(result)} characters — submitting...[/dim]"
        )
        console.print(f"[dim]Preview: {preview}[/dim]\n")

    return result


def _get_file_input(filepath: str) -> str:
    """Load prompt from a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        console.print(
            f"\n[dim]✅ Loaded {len(content)} characters from [bold]{filepath}[/bold][/dim]\n"
        )
        return content
    except FileNotFoundError:
        console.print(f"[red]❌ File not found: {filepath}[/red]")
        return ""
    except Exception as e:
        console.print(f"[red]❌ Error reading file: {e}[/red]")
        return ""


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
        console.print(
            f"[dim]{engine.memory.message_count()} message(s) in this session.[/dim]"
        )
        return True

    elif cmd == "domain":
        console.print(
            f"[dim]Active domain: {domain_label(engine.current_domain)}[/dim]"
        )
        return True

    return False


@click.command()
@click.option("--user", default="default", help="Username for saving conversation history.")
@click.option(
    "--domain",
    default=None,
    type=click.Choice(list(VALID_DOMAINS), case_sensitive=False),
    help="Force a specific domain.",
)
@click.option("--no-memory", is_flag=True, default=False, help="Don't save this session.")
def main(user: str, domain: str | None, no_memory: bool) -> None:
    """MultiMind — Education · Healthcare · Finance · Programming CLI chatbot."""

    init_db()
    memory = Memory(user=user, resume=not no_memory)
    engine = Engine(memory=memory, force_domain=domain)

    console.print()
    console.print(Panel(WELCOME_BANNER.strip(), border_style="cyan", padding=(1, 2)))

    if domain:
        console.print(f"[dim]Domain locked to: {domain_label(domain)}[/dim]\n")
    if no_memory:
        console.print("[dim]Running in no-memory mode.[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye! 👋[/dim]\n")
            break

        if not user_input:
            continue

        # Handle /paste command
        if user_input.lower() in ("/paste", "paste"):
            user_input = _get_multiline_input()
            if not user_input:
                continue

        # Handle /file command
        elif user_input.lower().startswith("/file ") or user_input.lower().startswith("file "):
            filepath = user_input.split(" ", 1)[1].strip()
            user_input = _get_file_input(filepath)
            if not user_input:
                continue

        # Handle other commands
        elif _handle_command(user_input, engine):
            continue

        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            response, active_domain = engine.respond(user_input)

        console.print()
        _print_response(response, active_domain)


if __name__ == "__main__":
    main()