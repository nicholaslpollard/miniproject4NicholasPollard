# INF601 - Advanced Programming in Python
# Nicholas Pollard
# Mini Project 4

"""buildhub CLI.  Implement so:  python -m buildhub summarize <file> --group-by G --value V --agg A
and:  python -m buildhub top <file> --key K --n N   both work (see SPEC.md)."""
import argparse
import sys

from buildhub.datakit import load_records, summarize, to_report, top_n


def build_parser():
    parser = argparse.ArgumentParser(prog="buildhub")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summarize_parser = subparsers.add_parser(
        "summarize", help="group and aggregate rows from a file"
    )
    summarize_parser.add_argument("file")
    summarize_parser.add_argument("--group-by", required=True)
    summarize_parser.add_argument("--value", required=True)
    summarize_parser.add_argument("--agg", required=True)
    summarize_parser.add_argument("--decimals", type=int, default=2)

    top_parser = subparsers.add_parser(
        "top", help="show the n rows with the largest value for a key"
    )
    top_parser.add_argument("file")
    top_parser.add_argument("--key", required=True)
    top_parser.add_argument("--n", type=int, required=True)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    records = load_records(args.file)

    if args.command == "summarize":
        result = summarize(
            records, args.group_by, args.value, args.agg, decimals=args.decimals
        )
        print(to_report(result))
    elif args.command == "top":
        for row in top_n(records, args.key, args.n):
            print(row)

    return 0


if __name__ == "__main__":
    sys.exit(main())
