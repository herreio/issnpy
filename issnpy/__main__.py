import json
import argparse

from . import fetch, find_link


def main():
    issnpy_cli = argparse.ArgumentParser("ISSN", description="")
    issnpy_cli.add_argument("id", type=str, help="ISSN of record to fetch")
    issnpy_cli.add_argument("--ld", type=bool, help="Get linked data (default: False)", nargs='?', const=True, default=False)
    issnpy_cli.add_argument("--pretty", type=bool, help="Pretty print output (default: False)", nargs='?', const=True, default=False)
    issnpy_args = issnpy_cli.parse_args()
    if issnpy_args.id is None:
        issnpy_cli.print_help()
        return None
    rec = fetch(issnpy_args.id, link=False, parse=False)
    if rec is not None:
        if issnpy_args.ld:
            output = rec.raw
        else:
            output = rec.parse()
        if issnpy_args.pretty:
            print(json.dumps(output, indent=2))
        else:
            print(json.dumps(output))


def main_link():
    issnpy_cli = argparse.ArgumentParser("ISSN-L", description="")
    issnpy_cli.add_argument("id", type=str, help="ISSN-L of record to fetch")
    issnpy_cli.add_argument("--ld", type=bool, help="Get linked data (default: False)", nargs='?', const=True, default=False)
    issnpy_cli.add_argument("--pretty", type=bool, help="Pretty print output (default: False)", nargs='?', const=True, default=False)
    issnpy_args = issnpy_cli.parse_args()
    if issnpy_args.id is None:
        issnpy_cli.print_help()
        return None
    link = find_link(issnpy_args.id)
    if link != issnpy_args.id:
        return None
    rec = fetch(issnpy_args.id, link=True, parse=False)
    if rec is not None:
        if issnpy_args.ld:
            output = rec.raw
        else:
            output = rec.parse()
        if issnpy_args.pretty:
            print(json.dumps(output, indent=2))
        else:
            print(json.dumps(output))


if __name__ == '__main__':
    main()
