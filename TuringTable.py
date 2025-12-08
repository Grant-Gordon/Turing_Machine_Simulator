from tt_parser import parse_turing_table
class TuringTable:
    def __init__(self, tt_path:str):
        parsed_vals = parse_turing_table(tt_path)
        TuringTable.validate_table(parsed_vals)
        self.tapes = parsed_vals["tapes"]
        self.states = parsed_vals["states"]
        self.alphabet = parsed_vals["alphabet"]
        ...

    @staticmethod
    def validate_table(parsed_vals):
        pass

    def get_transition(self):
        pass

