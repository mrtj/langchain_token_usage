"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Langchain Token Usage."""


if __name__ == "__main__":
    main(prog_name="langchain-token-usage")  # pragma: no cover
