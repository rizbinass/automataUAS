class TuringMachine:
    def __init__(self):
        self.blank_symbol = "B"
        self.reset()

    def reset(self):
        self.tape = [self.blank_symbol]
        self.head = 0
        self.state = "q0"
        self.step = 0
        self.status = "RUNNING"
        self.history = []

    def load_input(self, input_string):
        self.tape = []

        for symbol in input_string:
            self.tape.append(symbol)

        self.tape.append(self.blank_symbol)
        self.head = 0
        self.state = "q0"
        self.step = 0
        self.status = "RUNNING"
        self.history = []

    def get_tape_text(self):
        return "".join(self.tape)

    def get_head_position(self):
        return self.head

    def get_state(self):
        return self.state

    def is_halted(self):
        return self.state == "qaccept" or self.state == "qreject"

    def step_once(self):
        current_tape = self.get_tape_text()
        current_head = self.head
        current_state = self.state

        if self.is_halted():
            return {
                "step": self.step,
                "tape_before": current_tape,
                "head_before": current_head,
                "state_before": current_state,
                "read": self.tape[self.head],
                "write": self.tape[self.head],
                "move": "Stay",
                "state_after": self.state,
                "tape_after": current_tape,
                "head_after": current_head,
                "status": self.status,
            }

        read_symbol = self.tape[self.head]
        write_symbol = read_symbol
        move = "Stay"
        next_state = "qreject"

        if self.state == "q0":
            if read_symbol == "d":
                write_symbol = "X"
                move = "Right"
                next_state = "q1"
            else:
                next_state = "qreject"

        elif self.state == "q1":
            if read_symbol == "o":
                write_symbol = "X"
                move = "Right"
                next_state = "q2"
            else:
                next_state = "qreject"

        elif self.state == "q2":
            if read_symbol == "p":
                write_symbol = "X"
                move = "Right"
                next_state = "q3"
            else:
                next_state = "qreject"

        elif self.state == "q3":
            if read_symbol == "c":
                write_symbol = "X"
                move = "Right"
                next_state = "q4"
            else:
                next_state = "qreject"

        elif self.state == "q4":
            if read_symbol == "d":
                write_symbol = "X"
                move = "Right"
                next_state = "q1"
            elif read_symbol == "B":
                write_symbol = "B"
                move = "Stay"
                next_state = "qaccept"
            else:
                next_state = "qreject"

        self.tape[self.head] = write_symbol

        if move == "Right":
            self.head += 1
            if self.head >= len(self.tape):
                self.tape.append(self.blank_symbol)

        self.state = next_state

        if self.state == "qaccept":
            self.status = "DITERIMA"
        elif self.state == "qreject":
            self.status = "DITOLAK"

        result = {
            "step": self.step,
            "tape_before": current_tape,
            "head_before": current_head,
            "state_before": current_state,
            "read": read_symbol,
            "write": write_symbol,
            "move": move,
            "state_after": self.state,
            "tape_after": self.get_tape_text(),
            "head_after": self.head,
            "status": self.status,
        }

        self.history.append(result)
        self.step += 1
        return result

    def run_all(self):
        results = []

        while not self.is_halted():
            results.append(self.step_once())

        return results


def print_trace(input_string):
    machine = TuringMachine()
    machine.load_input(input_string)

    print("=================================")
    print("TRACE TURING MACHINE")
    print("=================================")
    print()

    while not machine.is_halted():
        print("Step", machine.step)
        print()
        print("Tape :")
        print()
        print(machine.get_tape_text())
        print()
        print("Head :")
        print()
        print(" " * machine.get_head_position() + "^")
        print()
        print("State :")
        print()
        print(machine.get_state())
        print()
        print("---------------------------------")
        print()
        machine.step_once()

    print("Step", machine.step)
    print()
    print("Tape :")
    print()
    print(machine.get_tape_text())
    print()
    print("Head :")
    print()
    print(" " * machine.get_head_position() + "^")
    print()
    print("State :")
    print()
    print(machine.get_state())
    print()
    print("---------------------------------")
    print()
    print("=================================")
    print()
    print("Final Tape :")
    print()
    print(machine.get_tape_text())
    print()
    print("Final State :")
    print()
    print(machine.get_state())
    print()
    print("Status :")
    print()
    print(machine.status)
    print()
    print("=================================")


if __name__ == "__main__":
    print("Masukkan string :")
    user_input = input()
    print()
    print_trace(user_input)
