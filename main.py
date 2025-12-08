import os
import argparse
from TuringTable import TuringTable
from TuringMachine import TuringMachine


def main(args):
    turing_table = TuringTable(args.tt)
    turing_machine = TuringMachine()

    turing_machine.run(turing_table, args.input, args.in_as_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile and optionally run CVAE C++ backend.")
    parser.add_argument("--tt", type=str, required=True, help="Path to an Algorithms TuringTable txt file")
    parser.add_argument("--in", type=str, required=True, help="Path to input txt file correspinging to --tt Algorithm. Set --in_as_str=True to directly pass input Strings")
    parser.add_argument("--in_as_str", type=bool, default=False, help="Set=True to pass input string directly; default = false")
    args = parser.parse_args()
    main(args)