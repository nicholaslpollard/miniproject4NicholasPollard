"""buildhub CLI.  Implement so:  python -m buildhub summarize <file> --group-by G --value V --agg A
and:  python -m buildhub top <file> --key K --n N   both work (see SPEC.md)."""
import sys

# TODO: build an argparse CLI with two subcommands, "summarize" and "top",
# that load the file and print the result (summarize -> to_report(...), top -> each row).


def main(argv=None):
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
