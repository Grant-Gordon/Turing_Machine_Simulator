import os
import argparse
from TuringTable import TuringTable
from TuringMachine import TuringMachine


def main():
    parser = argparse.ArgumentParser(description="Compile and optionally run CVAE C++ backend.")
    parser.add_argument("--tt", type=str, required=True, help="Path to an Algorithms TuringTable txt file")
    parser.add_argument("--input", type=str, required=True, help="Path to input txt file correspinging to --tt Algorithm. Set --in_as_file=False to directly pass input Strings")
    parser.add_argument("--in_as_file", type=bool, default=True, help="Set=False to pass input string directly; default = True")
    args = parser.parse_args()

    turing_table = TuringTable(args.tt)
    turing_machine = TuringMachine(turing_table)

    turing_machine.run(args.input, args.in_as_file)


if __name__ == "__main__":
    main()