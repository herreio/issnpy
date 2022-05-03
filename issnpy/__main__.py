import json
import argparse

from . import record, record_link, find_link


def main():
    issnpy_cli = argparse.ArgumentParser("ISSN", description="")
    issnpy_cli.add_argument("id", type=str, help="ISSN of record to fetch")
    issnpy_cli.add_argument("--pretty", type=bool, help="Pretty print output (default: False)", nargs='?', const=True, default=False)
    issnpy_args = issnpy_cli.parse_args()
    if issnpy_args.id is None:
        issnpy_cli.print_help()
        return None
    rec = record(issnpy_args.id)
    if rec is not None:
        if issnpy_args.pretty:
            print(json.dumps(rec, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(rec, ensure_ascii=False))


def main_link():
    issnpy_cli = argparse.ArgumentParser("ISSN-L", description="")
    issnpy_cli.add_argument("id", type=str, help="ISSN-L of record to fetch")
    issnpy_cli.add_argument("--pretty", type=bool, help="Pretty print output (default: False)", nargs='?', const=True, default=False)
    issnpy_args = issnpy_cli.parse_args()
    if issnpy_args.id is None:
        issnpy_cli.print_help()
        return None
    link = find_link(issnpy_args.id)
    if link != issnpy_args.id:
        return None
    rec = record_link(issnpy_args.id)
    if rec is not None:
        if issnpy_args.pretty:
            print(json.dumps(rec, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(rec, ensure_ascii=False))


if __name__ == '__main__':
    main()
