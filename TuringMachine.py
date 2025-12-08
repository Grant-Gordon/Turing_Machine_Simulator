from typing import List, Tuple
from TuringTable import TuringTable
from Tape import Tape
class TuringMachine:

    def __init__(self, tt:TuringTable, max_steps:int=500):
        self.tt= tt
        self.max_steps=max_steps
        self.global_state=None
        self.tapes=[]

    def _parse_input_line(self, line: str) -> Tuple[str, ...]:
        line= line.strip()
        if not line:
              raise ValueError("Empty input line.")
        if self.tt.tapes == 1:
            return (line,)
        parts = [p.strip() for p in line.split("\n")]
        if len(parts) != self.tt.tapes:
            raise ValueError(f"Expected {self.tt.tapes} tape segments separated by '|', got {len(parts)}: {line!r}")
        return tuple(parts)

        
    def step(self) -> bool:

        assert self.global_state is not None
        state = self.global_state

        if state == self.tt.accept_state or state == self.tt.reject_state:
            return False
        
        read_tuple = tuple(t.read() for t in self.tapes)

        key = (state, read_tuple)
        transition= self.tt.transitions.get(key)
        if transition is None:
            self.global_state=self.tt.reject_state
            return False
        
        next_state, actions = transition
        for tape, (write_symbol, direction) in zip(self.tapes, actions):
            tape.write(write_symbol)
            tape.move(direction)

        self.global_state = next_state

        if next_state == self.tt.accept_state or next_state==self.tt.reject_state:
            return False
        
        return True
    
    def run(self, inputs:str, inputs_as_path:bool=True)->None:
        if inputs_as_path:
            with open(inputs, "r", encoding="utf-8") as f:
                raw_lines = f.readlines()
        else:
            raw_lines = inputs.split("\n")

        test_cases = [ln.strip() for ln in raw_lines if ln.strip()]

        for idx, line in enumerate(test_cases, start=1):
            print(f"=== Input {idx}: {line!r} ===")
            tape_strings = self._parse_input_line(line)
            self.global_state=0
            self.tapes = [Tape(s, blank='_') for s in tape_strings]
            
            steps = 0
            while steps < self.max_steps and self.step():
                steps += 1

            final_tapes = tuple(t.render() for t in self.tapes)
            print(f"Final state: {self.global_state}")
            print(f"Final tapes: {final_tapes}")
            print(f"Steps taken: {steps}")
            print()
        