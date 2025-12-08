from typing import Dict, List, Tuple, Any


def parse_turing_table(tt_path):
    lines = _read_nonempty_noncomment_lines(tt_path)
    header_vals = _parse_header(lines)
    tapes = header_vals["tapes"]
    states = header_vals["states"]
    alphabet = header_vals["alphabet"]

    transitions={}
    for line in header_vals["remaining_lines"]:
        current_state, read_tuple, next_state, actions = _parse_transition_lines(line=line, tapes=tapes, alphabet=alphabet)
        
        if current_state < 0 or current_state >= states:
            raise  ValueError( f"Transition line uses current_state={current_state}, which is outside the non-halting state range [0, {states - 1}].")

        if not (0 <= next_state < states or next_state == -1 or next_state == -2):
            raise ValueError(f"Transition line uses next_state={next_state}, which is notin [0, {states - 1}] nor accept=-1 nor reject=-2.")
        
        key = (current_state, read_tuple)
        if key in transitions:
            raise ValueError(f"Duplicate transition for state={current_state}, read={read_tuple}.")
        transitions[key] = (next_state, actions)

    parsed = {
        "tapes": tapes,
        "states": states,
        "alphabet": alphabet,
        "transitions": transitions,
    }
    return parsed


def _read_nonempty_noncomment_lines(tt_path:str) ->List[str]:
    result=[]

    with open(tt_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            stripped = raw_line.split("#",1)[0].strip()
            if not stripped:
                continue
            result.append(stripped)
    return result


def _parse_header(lines:List[str])-> Dict[str, Any]:
    tapes = None
    states = None
    alphabet_str = None
    
    remaining_lines = []

    header_expected_keys = {"tapes", "states", "alphabet"}
    
    header_done=False
    for line in lines:
        if ":" not in line:
            header_done=True
        
        if not header_done:
            key, value = _split_key_value(line)
            key_lower = key.lower()
            if key_lower not in header_expected_keys:
                raise ValueError(f"Unknown header key '{key}' in line: {line}")
            if key_lower == "tapes":
                tapes = _parse_int(value, "tapes")
                if tapes<=0:
                    raise ValueError("tapes must be a positive integer")
            elif key_lower == "states":
                states = _parse_int(value, "states")
                if states <= 0:
                    raise ValueError("states must be a positive integer.")
            elif key_lower == "alphabet":
                alphabet_str= value.strip()
                if not alphabet_str:
                    raise ValueError("alphabet must not be empty.")
                #TODO: no blank guard
        else:
            remaining_lines.append(line)
    if tapes is None:
        raise ValueError("Missing 'tapes:' header.")
    if states is None:
        raise ValueError("Missing 'states:' header.")
    if alphabet_str is None:
        raise ValueError("Missing 'alphabet:' header.")

    alphabet_tuple: Tuple[str, ...] = tuple(alphabet_str)
    
    return {
        "tapes": tapes,
        "states": states,
        "alphabet": alphabet_tuple,
        "remaining_lines": remaining_lines,
    }

def _parse_int(text:str, field_name:str)->int:
    try:
        return int(text.strip())
    except ValueError as x:
        raise ValueError(f"Invalud integer fro '{field_name}': {text!r}") from x
    
def _split_key_value(line: str) -> Tuple[str, str]:

    key, value = line.splie(":",1)
    key_clean = key.strip()
    value_clean = value.strip()

    if not key_clean:
        raise ValueError(f"Invalid header line (missing key): {line}")
    if not value_clean:
        raise ValueError(f"Invalid header line (missing value): {line}")
    return key_clean, value_clean

def _parse_transition_lines(line:str, tapes:int, alphabet:Tuple[str,...]):
    if ":" not in line:
        raise ValueError(f"Transition line missing ':' separator: {line}")
    left_part, rest = line.split(":", 1)
    current_state = _parse_int(left_part, "current_state")

    second_colon_index = rest.find(":")
    if second_colon_index == -1:
        raise ValueError(
            f"Transition line must contain two ':' separators: {line}"
        )
    
    reads_part = rest[:second_colon_index].strip()
    right_part = rest[second_colon_index + 1 :].strip()

    read_symbols_tokens = reads_part.split()
    if len(read_symbols_tokens) != tapes:
        raise ValueError(
            f"Expected {tapes} read symbols in transition, got {len(read_symbols_tokens)} "
            f"in line: {line}"
        )
    read_tuple: Tuple[str, ...] = tuple(
        _parse_read_symbol(token, alphabet, line) for token in read_symbols_tokens
    )

    # right_part is "<next_state> <actions...>" but still has a colon removed;
    # we split once on whitespace to get next_state, then the remaining actions.
    if not right_part:
        raise ValueError(f"Missing next_state and actions in line: {line}")
    tokens = right_part.split()
    if len(tokens) < 1 + tapes:
        raise ValueError(
            f"Expected at least {1 + tapes} tokens (next_state + {tapes} actions), "
            f"got {len(tokens)} in line: {line}"
        )
    next_state = _parse_int(tokens[0], "next_state")
    action_tokens = tokens[1:]

    if len(action_tokens) != tapes:
        raise ValueError(f"Expected {tapes} action tokens, got {len(action_tokens)} in line: {line}")
    actions = [_parse_action_token(action_token, alphabet, line) for action_token in action_tokens]

    return current_state, read_tuple, next_state, tuple(actions)


                                                                                  

def _parse_read_symbol(token:str, alphabet:Tuple[str, ...], line:str) ->str:
    if len(token) !=1:
        raise ValueError( f"Read symbol '{token}' must be a single character; line: {line}")
    
    symbol = token
    if symbol not in alphabet: 
        raise ValueError(f"Read symbol '{symbol}' is not in the alphabet {alphabet}; line: {line}")
    return symbol


def _parse_action_token(token:str, alphabet: Tuple[str, ...], line: str,):
    if len(token)==1:
        direction =token
        if direction not in ("L", "R", "S"):
            raise ValueError(f"Single-character action '{token}' must be one of 'L', 'R', 'S'; line: {line}")
        return None, direction
    
    if len(token) ==2:
        symbol = token[0]
        direction=token[1]
        if symbol not in alphabet:
            raise ValueError(f"Write symbol '{symbol}' is not in the alphabet {alphabet}; line: {line}")
        if direction not in ("L", "R", "S"):
            raise ValueError(f"Direction '{direction}' in action '{token}' must be one of 'L', 'R', 'S'; line: {line}")
        return symbol, direction
    raise ValueError(f"Invalid action token '{token}'. Must be 'L','R','S' or '<symbol><direction>';line: {line}")