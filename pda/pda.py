def cetak_panduan():
    print("=================================")
    print("PANDUAN PROGRAM PDA")
    print("=================================")
    print("Program ini mensimulasikan Pushdown Automata untuk bahasa (dopc)+.")
    print()
    print("Arti simbol:")
    print("d = sensor mendeteksi user")
    print("o = pintu terbuka")
    print("p = user melewati pintu")
    print("c = pintu tertutup")
    print()
    print("Contoh string diterima:")
    print("dopc")
    print("dopcdopc")
    print("dopcdopcdopc")
    print()
    print("Contoh string ditolak:")
    print("docp")
    print("dpoc")
    print("dopo")
    print("dop")
    print()
    print("Cara membaca trace:")
    print("Current State menunjukkan state saat ini.")
    print("Current Input menunjukkan simbol yang sedang dibaca.")
    print("Stack selalu Z karena PDA ini tidak melakukan push atau pop.")
    print("Move To menunjukkan state tujuan setelah transisi.")
    print("Jika semua pola dopc lengkap, status akhir adalah DITERIMA.")
    print("Jika ada urutan simbol yang salah, status akhir adalah DITOLAK.")
    print("=================================")
    print()


def cetak_transisi(step, current_state, current_input, stack, move_to):
    print("Step", step)
    print()
    print("Current State :", current_state)
    print()
    print("Current Input :", current_input)
    print()
    print("Stack :", stack)
    print()
    print("Move To :", move_to)
    print()
    print("---------------------------------")
    print()


def simulasi_pda(input_string):
    state = "q0"
    stack = ["Z"]
    step = 0
    valid = True

    print("=================================")
    print("TRACE PDA")
    print("=================================")
    print()

    for symbol in input_string:
        current_state = state
        move_to = None

        if state == "q0" and symbol == "d" and stack[-1] == "Z":
            move_to = "q1"
        elif state == "q1" and symbol == "o" and stack[-1] == "Z":
            move_to = "q2"
        elif state == "q2" and symbol == "p" and stack[-1] == "Z":
            move_to = "q3"
        elif state == "q3" and symbol == "c" and stack[-1] == "Z":
            move_to = "q4"
        elif state == "q4" and symbol == "d" and stack[-1] == "Z":
            cetak_transisi(step, "q4", "epsilon", stack[-1], "q0")
            step += 1
            current_state = "q0"
            move_to = "q1"
        else:
            valid = False

        if not valid:
            cetak_transisi(step, current_state, symbol, stack[-1], "Tidak ada transisi")
            break

        cetak_transisi(step, current_state, symbol, stack[-1], move_to)
        state = move_to
        step += 1

    if valid and state == "q4":
        cetak_transisi(step, "q4", "epsilon", stack[-1], "q0")
        step += 1
        state = "q0"

        cetak_transisi(step, "q0", "epsilon", stack[-1], "qf")
        state = "qf"

    print("Status :", "DITERIMA" if state == "qf" else "DITOLAK")


def main():
    cetak_panduan()
    print("Masukkan string :")
    input_string = input()
    print()
    simulasi_pda(input_string)


if __name__ == "__main__":
    main()
