from typing import List, Tuple
from TuringTable import TuringTable
from Tape import Tape
#ANSI COLORS 
RESET = "\033[0m"
BOLD = "\033[1m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"

class TuringMachine:

    def __init__(self, tt:TuringTable, max_steps:int=500):
        self.tt= tt
        self.max_steps=max_steps
        self.global_state=None
        self.tapes=[]

    def _parse_input_line(self, line: str) -> Tuple[str, ...]:
        # Strip off inline comments
        line = line.split("#", 1)[0].strip()

        if not line:
            return None
        if self.tt.tapes == 1:
            return (line,)
        #Multi-tape initialization splits on '|'
        parts = [p.strip() for p in line.split("|")]
        if len(parts) > self.tt.tapes:
            raise ValueError(f"Expected at most {self.tt.tapes} tape segments separated by '|', got {len(parts)}: {line!r}")
        while len(parts) < self.tt.tapes:
            parts.append("") #start other tapes with blank
        return tuple(parts)

        
    def step(self, step_index) -> bool:
        assert self.global_state is not None
        state_before = self.global_state

        # Halting check before doing anything
        if state_before == self.tt.accept_state or state_before == self.tt.reject_state:
            return False

        # Read tuple BEFORE the transition
        read_tuple_before = tuple(t.read() for t in self.tapes)

        key = (state_before, read_tuple_before)
        trans = self.tt.transitions.get(key)
        if trans is None:
            # No transition defined: treat as reject or "stuck"
            next_state = self.tt.reject_state
            self.global_state = next_state

            # After this, the heads have not moved; show current symbols
            read_tuple_after = tuple(t.read() for t in self.tapes)
            self._print_step_trace(
                step_index=step_index,
                state=next_state,
                read_tuple=read_tuple_after,
            )
            return False

        next_state, actions = trans

        # Apply writes and moves
        for tape, (write_sym, direction) in zip(self.tapes, actions):
            tape.write(write_sym)
            tape.move(direction)

        # Update state
        self.global_state = next_state

        # Now read tuple AFTER the transition (matching the professor's trace style)
        read_tuple_after = tuple(t.read() for t in self.tapes)

        # Print this step's configuration
        self._print_step_trace(
            step_index=step_index,
            state=next_state,
            read_tuple=read_tuple_after,
        )

        # Final halting check
        if next_state == self.tt.accept_state or next_state == self.tt.reject_state:
            return False

        return True
    
    def run(self, inputs:str, inputs_as_path:bool=True)->None:
        if inputs_as_path:
            raw_lines=[]
            with open(inputs, "r", encoding="utf-8") as f:
               raw_lines=[raw_line for raw_line in f]
        else:
            raw_lines = [raw_line for raw_line in inputs.split("\n")]
        
        test_cases=[]
        for raw_line in raw_lines:
            stripped= raw_line.split("#", 1)[0].strip()
            if not stripped:
                continue
            test_cases.append(stripped)

        for idx, line in enumerate(test_cases, start=1):
            print(f"=== Input {idx}: {line!r} ===")
            tape_strings = self._parse_input_line(line)
            self.global_state=0
            self.tapes = [Tape(s, blank='_') for s in tape_strings]

            initial_read = tuple(t.read() for t in self.tapes)
            self._print_step_trace(step_index=0, state=self.global_state, read_tuple=initial_read)
            
            steps = 0
            while steps < self.max_steps and self.step(steps+1):
                steps += 1

            final_tapes = tuple(t.render() for t in self.tapes)
            print(f"Final state: {self.global_state}")
            print(f"Final tapes: {final_tapes}")
            print(f"Steps taken: {steps}")
            print()
        
    def _print_step_trace(self, step_index, state, read_tuple):
        blank = '_'

        # ---------- Print the TM state line once ----------
        if state == self.tt.accept_state:
            state_str = f"{GREEN}{state}{RESET}"
        elif state == self.tt.reject_state:
            state_str = f"{RED}{state}{RESET}"
        else:
            state_str = f"{state}"

        display_syms = []
        for sym in read_tuple:
            display_char = " " if sym == blank else sym
            display_syms.append(f"{BOLD}'{display_char}'{RESET}")

        state_tuple_str = ", ".join([str(state_str)] + display_syms)
        print(f"Turing machine state: ( {state_tuple_str} )")

        # ---------- Collect tape lines first ----------
        tape_infos: list[tuple[str, str, str]] = []

        for tape_idx, tape in enumerate(self.tapes):
            head_pos_display = tape.head + 1  # 1-based
            word_display = tape.render_with_head(blank=blank)  # keeps your red head

            plain_prefix = f"tape {tape_idx}: I:{head_pos_display} S:{step_index}"
            colored_prefix = (
                f"{CYAN}tape {tape_idx}{RESET}: "
                f"{YELLOW}I:{head_pos_display} S:{step_index}{RESET}"
            )

            tape_infos.append((plain_prefix, colored_prefix, word_display))

        # ---------- Compute alignment width ----------
        max_prefix_len = max(len(info[0]) for info in tape_infos) if tape_infos else 0

        # ---------- Print each tape line with aligned "Word:" ----------
        for plain_prefix, colored_prefix, word_display in tape_infos:
            pad_len = max_prefix_len - len(plain_prefix)
            pad = " " * pad_len
            print(f"{colored_prefix}{pad} Word: {word_display}")

        print()  # blank line between steps