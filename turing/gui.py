import tkinter as tk
from tkinter import scrolledtext
 
import cv2

from camera_detector import CameraDetector
from turing_machine import TuringMachine


class AutomaticDoorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulasi Pintu Otomatis - Mesin Turing")
        self.root.geometry("1280x760")
        self.root.minsize(1120, 680)

        self.detector = CameraDetector()
        self.machine = TuringMachine()
        self.running = False
        self.door_phase = "q0"
        self.person_present = False
        self.detection_lock = False
        self.no_person_unlock_since = None
        self.no_person_since = None
        self.keep_open_log_since = None
        self.input_symbols = []
        self.tm_running = False
        self.detection_frames = 0
        self.current_photo = None

        self.camera_label = None
        self.tape_value = None
        self.state_cards = {}
        self.head_value = None
        self.door_value = None
        self.log_area = None
        self.start_button = None
        self.reset_button = None
        self.exit_button = None

        self.build_interface()
        self.reset_system()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def build_interface(self):
        self.root.configure(bg="#e5e7eb")

        title = tk.Label(
            self.root,
            text="SIMULASI PINTU OTOMATIS",
            font=("Arial", 26, "bold"),
            bg="#111827",
            fg="#ffffff",
            pady=14,
        )
        title.pack(fill=tk.X)

        main_frame = tk.Frame(self.root, bg="#e5e7eb")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)
        main_frame.columnconfigure(0, weight=45)
        main_frame.columnconfigure(1, weight=55)
        main_frame.rowconfigure(0, weight=1)

        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#cbd5e1")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)

        camera_title = tk.Label(
            left_frame,
            text="KAMERA LANGSUNG",
            font=("Arial", 18, "bold"),
            bg="#ffffff",
            fg="#111827",
            pady=10,
        )
        camera_title.grid(row=0, column=0, sticky="ew")

        self.camera_label = tk.Label(
            left_frame,
            text="Kamera belum aktif",
            font=("Arial", 22, "bold"),
            bg="#111827",
            fg="#ffffff",
        )
        self.camera_label.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        button_frame = tk.Frame(left_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        self.start_button = tk.Button(
            button_frame,
            text="MULAI KAMERA",
            command=self.start_system,
            font=("Arial", 13, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            height=2,
        )
        self.start_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.reset_button = tk.Button(
            button_frame,
            text="RESET SIMULASI",
            command=self.reset_system,
            font=("Arial", 13, "bold"),
            bg="#f59e0b",
            fg="#111827",
            height=2,
        )
        self.reset_button.grid(row=0, column=1, sticky="ew", padx=4)

        self.exit_button = tk.Button(
            button_frame,
            text="KELUAR",
            command=self.exit_app,
            font=("Arial", 13, "bold"),
            bg="#dc2626",
            fg="#ffffff",
            height=2,
        )
        self.exit_button.grid(row=0, column=2, sticky="ew", padx=(4, 0))

        right_frame = tk.Frame(main_frame, bg="#e5e7eb")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(4, weight=1)

        status_frame = tk.Frame(right_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#cbd5e1")
        status_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        status_title = tk.Label(
            status_frame,
            text="STATUS PINTU",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#475569",
        )
        status_title.pack(fill=tk.X, pady=(10, 0))

        self.door_value = tk.Label(
            status_frame,
            text="MENUNGGU",
            font=("Arial", 34, "bold"),
            bg="#dbeafe",
            fg="#1e3a8a",
            padx=12,
            pady=12,
        )
        self.door_value.pack(fill=tk.X, padx=12, pady=10)

        state_frame = tk.Frame(right_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#cbd5e1")
        state_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        state_title = tk.Label(
            state_frame,
            text="STATE MESIN TURING",
            font=("Arial", 15, "bold"),
            bg="#ffffff",
            fg="#475569",
        )
        state_title.pack(fill=tk.X, pady=(10, 0))

        state_grid = tk.Frame(state_frame, bg="#ffffff")
        state_grid.pack(fill=tk.X, padx=12, pady=10)
        state_grid.columnconfigure(0, weight=1)
        state_grid.columnconfigure(1, weight=1)

        self.add_state_card(state_grid, "q0", "State Awal\nMenunggu pengguna", 0, 0)
        self.add_state_card(state_grid, "q1", "Membaca simbol d\nPintu mulai membuka", 0, 1)
        self.add_state_card(state_grid, "q2", "Membaca simbol o\nPintu terbuka", 1, 0)
        self.add_state_card(state_grid, "q3", "Membaca simbol p\nPengguna telah lewat", 1, 1)
        self.add_state_card(state_grid, "q4", "Membaca simbol c\nPintu menutup", 2, 0)
        self.add_state_card(state_grid, "qf", "State Akhir\nString diterima", 2, 1)

        tape_frame = tk.Frame(right_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#cbd5e1")
        tape_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        tape_title = tk.Label(
            tape_frame,
            text="TAPE",
            font=("Arial", 15, "bold"),
            bg="#ffffff",
            fg="#475569",
        )
        tape_title.pack(fill=tk.X, pady=(10, 0))

        self.tape_value = tk.Label(
            tape_frame,
            text="B",
            font=("Consolas", 26, "bold"),
            bg="#ecfdf5",
            fg="#065f46",
            padx=12,
            pady=10,
            anchor="center",
        )
        self.tape_value.pack(fill=tk.X, padx=12, pady=10)

        self.head_value = tk.Label(
            tape_frame,
            text="Posisi Head : 0",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#64748b",
        )
        self.head_value.pack(fill=tk.X, padx=12, pady=(0, 10))

        tape_note = tk.Label(
            tape_frame,
            text="Keterangan:\nX = Simbol yang sudah diproses\nB = Blank (akhir tape)",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            fg="#475569",
            justify=tk.LEFT,
            anchor="w",
        )
        tape_note.pack(fill=tk.X, padx=12, pady=(0, 10))

        symbol_frame = tk.Frame(right_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#cbd5e1")
        symbol_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        symbol_title = tk.Label(
            symbol_frame,
            text="KETERANGAN SIMBOL",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#111827",
        )
        symbol_title.pack(fill=tk.X, pady=(10, 4))

        symbol_content = tk.Frame(symbol_frame, bg="#ffffff")
        symbol_content.pack(fill=tk.X, padx=12, pady=(0, 10))

        self.add_symbol_row(symbol_content, "d", "Sensor mendeteksi pengguna")
        self.add_symbol_row(symbol_content, "o", "Pintu terbuka")
        self.add_symbol_row(symbol_content, "p", "Pengguna melewati pintu")
        self.add_symbol_row(symbol_content, "c", "Pintu menutup")
        self.add_symbol_row(symbol_content, "X", "Simbol yang sudah diproses oleh Mesin Turing")
        self.add_symbol_row(symbol_content, "B", "Blank (akhir tape)")

        log_frame = tk.Frame(right_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#cbd5e1")
        log_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        log_frame.rowconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)

        log_title = tk.Label(
            log_frame,
            text="LOG SISTEM",
            font=("Arial", 18, "bold"),
            bg="#ffffff",
            fg="#111827",
            pady=8,
        )
        log_title.grid(row=0, column=0, sticky="ew", padx=12)

        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            height=14,
            font=("Arial", 15, "bold"),
            bg="#111827",
            fg="#f8fafc",
            insertbackground="#f8fafc",
            wrap=tk.WORD,
            relief=tk.FLAT,
            state=tk.DISABLED,
        )
        self.log_area.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.log_area.tag_configure("penting", foreground="#fde68a", font=("Arial", 15, "bold"))

    def add_state_card(self, parent, state_name, description, row, column):
        card = tk.Frame(parent, bg="#f8fafc", bd=0, highlightthickness=1, highlightbackground="#e2e8f0")
        card.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)

        name_label = tk.Label(
            card,
            text=state_name,
            font=("Consolas", 18, "bold"),
            bg="#f8fafc",
            fg="#64748b",
        )
        name_label.pack(fill=tk.X, pady=(6, 0))

        description_label = tk.Label(
            card,
            text=description,
            font=("Arial", 10, "bold"),
            bg="#f8fafc",
            fg="#64748b",
            justify=tk.CENTER,
            wraplength=260,
        )
        description_label.pack(fill=tk.X, padx=8, pady=(0, 6))

        self.state_cards[state_name] = {
            "frame": card,
            "name": name_label,
            "description": description_label,
        }

    def add_symbol_row(self, parent, symbol, description):
        row = tk.Frame(parent, bg="#ffffff")
        row.pack(fill=tk.X, pady=1)

        symbol_label = tk.Label(
            row,
            text=symbol,
            font=("Consolas", 15, "bold"),
            bg="#eef2ff",
            fg="#1e3a8a",
            width=3,
            padx=4,
            pady=2,
        )
        symbol_label.pack(side=tk.LEFT, padx=(0, 8))

        description_label = tk.Label(
            row,
            text="= " + description,
            font=("Arial", 13, "bold"),
            bg="#ffffff",
            fg="#111827",
            anchor="w",
        )
        description_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def start_system(self):
        if self.running:
            return

        if not self.detector.start():
            self.set_door_status("KESALAHAN KAMERA")
            self.add_log("Kamera tidak dapat dibuka.")
            return

        self.running = True
        self.prepare_waiting_state(clear_log=True)
        self.start_button.config(state=tk.DISABLED)
        self.update_camera()

    def update_camera(self):
        if not self.running:
            return

        success, frame = self.detector.read_frame()

        if not success:
            self.add_log("Gagal membaca frame kamera.")
            self.root.after(300, self.update_camera)
            return

        person_detected, frame = self.detector.detect_person(frame)
        self.show_frame(frame)
        self.handle_detection_state(person_detected)

        self.root.after(80, self.update_camera)

    def handle_detection_state(self, person_detected):
        current_time = self.current_time_ms()

        if self.detection_lock:
            if person_detected:
                self.no_person_unlock_since = None
                return
            if self.no_person_unlock_since is None:
                self.no_person_unlock_since = current_time
                self.add_log("Area sensor harus kosong selama 1 detik sebelum siklus baru.")
                return
            if current_time - self.no_person_unlock_since >= 1000:
                self.detection_lock = False
                self.no_person_unlock_since = None
                self.add_log("Area sensor kosong. Sistem siap menerima deteksi baru.", important=True)
            return

        if self.door_phase == "q0":
            if person_detected:
                self.detection_frames += 1
                if self.detection_frames >= 5:
                    self.detection_frames = 0
                    self.start_door_cycle()
            else:
                self.detection_frames = 0
            return

        if person_detected:
            self.no_person_since = None
            if self.door_phase == "q2":
                self.set_door_status("PINTU TERBUKA")
                if self.keep_open_log_since is None or current_time - self.keep_open_log_since >= 2000:
                    self.keep_open_log_since = current_time
                    self.add_log("Pengguna masih berada di area sensor.")
                    self.add_log("Pintu tetap terbuka.", important=True)
            return

        if self.door_phase != "q2":
            return

        if self.no_person_since is None:
            self.no_person_since = current_time
            self.keep_open_log_since = None
            self.add_log("Area sensor kosong. Menunggu 3 detik sebelum pintu menutup...")
            return

        if current_time - self.no_person_since >= 3000:
            self.no_person_since = None
            self.keep_open_log_since = None
            self.go_to_q3()

    def show_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        success, encoded_image = cv2.imencode(".ppm", rgb_frame)
        if not success:
            return
        self.current_photo = tk.PhotoImage(data=encoded_image.tobytes(), format="PPM")
        self.camera_label.config(image=self.current_photo, text="")

    def start_door_cycle(self):
        if self.door_phase != "q0":
            return
        self.door_phase = "q1"
        self.input_symbols = ["d"]
        self.update_machine_display()
        self.set_door_status("MEMBUKA PINTU")
        self.add_log("Pengguna terdeteksi oleh sensor.", important=True)
        self.add_log("Simbol yang dihasilkan : d")
        self.root.after(5000, self.go_to_q2)

    def go_to_q2(self):
        if self.door_phase != "q1":
            return
        self.door_phase = "q2"
        self.input_symbols.append("o")
        self.update_machine_display()
        self.set_door_status("PINTU TERBUKA")
        self.add_log("Pintu terbuka.", important=True)
        self.add_log("Simbol yang dihasilkan : o")

    def go_to_q3(self):
        if self.door_phase != "q2":
            return
        self.door_phase = "q3"
        self.input_symbols.append("p")
        self.update_machine_display()
        self.set_door_status("PINTU TERBUKA")
        self.add_log("Pengguna telah melewati pintu.", important=True)
        self.add_log("Simbol yang dihasilkan : p")
        self.root.after(3000, self.go_to_q4)

    def go_to_q4(self):
        if self.door_phase != "q3":
            return
        self.door_phase = "q4"
        self.input_symbols.append("c")
        self.update_machine_display()
        self.set_door_status("MENUTUP PINTU")
        self.add_log("Pintu menutup.", important=True)
        self.add_log("Simbol yang dihasilkan : c")
        self.root.after(3000, self.go_to_qf)

    def go_to_qf(self):
        if self.door_phase != "q4":
            return
        self.door_phase = "qf"
        self.update_machine_display()
        self.set_door_status("PINTU TERTUTUP")
        self.add_log("State akhir. String diterima.", important=True)
        self.add_log("Pintu tertutup.", important=True)
        self.run_turing_machine()

    def run_turing_machine(self):
        if self.tm_running:
            return
        input_string = "".join(self.input_symbols)
        self.tm_running = True
        self.machine.load_input(input_string)
        self.update_machine_display()
        self.add_log("Input lengkap : " + input_string)
        self.add_log("Menjalankan simulasi Mesin Turing...", important=True)
        self.root.after(500, self.run_next_tm_step)

    def run_next_tm_step(self):
        if not self.tm_running:
            return
        if self.machine.is_halted():
            self.finish_turing_machine()
            return
        result = self.machine.step_once()
        self.update_machine_display()
        self.add_log("Langkah " + str(result["step"]))
        self.add_log("State saat ini : " + result["state_before"])
        self.add_log("Membaca simbol : " + result["read"])
        self.add_log("Tape : " + self.format_tape(result["tape_after"]))
        self.add_log("State berubah menjadi : " + result["state_after"], important=True)
        self.root.after(600, self.run_next_tm_step)

    def finish_turing_machine(self):
        if not self.tm_running:
            return
        self.update_machine_display()
        if self.machine.get_state() == "qaccept":
            self.set_door_status("DITERIMA")
            self.add_log("Mesin Turing mencapai state qaccept.", important=True)
            self.add_log("Status akhir : DITERIMA", important=True)
        else:
            self.set_door_status("DITOLAK")
            self.add_log("Mesin Turing mencapai state qreject.", important=True)
            self.add_log("Status akhir : DITOLAK", important=True)
        self.tm_running = False
        self.root.after(500, self.reset_after_tm)

    def reset_after_tm(self):
        self.prepare_waiting_state(clear_log=False, lock_detection=True)
        self.add_log("Sistem kembali ke q0. Menunggu deteksi baru...")

    def update_machine_display(self):
        state_colors = {
            "q0": ("#fef3c7", "#92400e"),
            "q1": ("#dbeafe", "#1e3a8a"),
            "q2": ("#e0e7ff", "#3730a3"),
            "q3": ("#fce7f3", "#9d174d"),
            "q4": ("#dcfce7", "#166534"),
            "qf": ("#bbf7d0", "#14532d"),
        }

        if self.tm_running:
            tm_state = self.machine.get_state()
            active_state = "qf" if tm_state in ("qaccept", "qreject") else tm_state
        else:
            active_state = self.door_phase

        for state_name, card in self.state_cards.items():
            if state_name == active_state:
                bg_color, fg_color = state_colors.get(state_name, ("#fef3c7", "#92400e"))
                border_color = fg_color
            else:
                bg_color = "#f8fafc"
                fg_color = "#94a3b8"
                border_color = "#e2e8f0"

            card["frame"].config(bg=bg_color, highlightbackground=border_color)
            card["name"].config(bg=bg_color, fg=fg_color)
            card["description"].config(bg=bg_color, fg=fg_color)

        if self.tm_running:
            tape_text = self.machine.get_tape_text()
            head_pos = str(self.machine.get_head_position())
        else:
            tape_text = "".join(self.input_symbols) if self.input_symbols else "B"
            head_pos = "0"

        self.tape_value.config(text=self.format_tape(tape_text))
        self.head_value.config(text="Posisi Head : " + head_pos)

    def set_door_status(self, status):
        colors = {
            "MENUNGGU": ("#dbeafe", "#1e3a8a"),
            "MEMBUKA PINTU": ("#dcfce7", "#166534"),
            "PINTU TERBUKA": ("#bbf7d0", "#14532d"),
            "MENUTUP PINTU": ("#fee2e2", "#991b1b"),
            "PINTU TERTUTUP": ("#e2e8f0", "#334155"),
            "DITERIMA": ("#dcfce7", "#166534"),
            "DITOLAK": ("#fee2e2", "#991b1b"),
            "KESALAHAN KAMERA": ("#fee2e2", "#991b1b"),
        }
        bg_color, fg_color = colors.get(status, ("#dbeafe", "#1e3a8a"))
        self.door_value.config(text=status, bg=bg_color, fg=fg_color)

    def add_log(self, message, important=False):
        self.log_area.config(state=tk.NORMAL)
        tag = "penting" if important else None

        if tag is None:
            self.log_area.insert(tk.END, message + "\n")
        else:
            self.log_area.insert(tk.END, message + "\n", tag)

        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def format_tape(self, tape_text):
        return " ".join(tape_text)

    def current_time_ms(self):
        return int(self.root.tk.call("clock", "milliseconds"))

    def prepare_waiting_state(self, clear_log, lock_detection=False):
        self.door_phase = "q0"
        self.person_present = False
        self.detection_lock = lock_detection
        self.no_person_unlock_since = None
        self.no_person_since = None
        self.keep_open_log_since = None
        self.input_symbols = []
        self.tm_running = False
        self.detection_frames = 0
        self.machine.reset()
        self.update_machine_display()
        self.set_door_status("MENUNGGU")

        if clear_log and self.log_area is not None:
            self.log_area.config(state=tk.NORMAL)
            self.log_area.delete("1.0", tk.END)
            self.log_area.config(state=tk.DISABLED)

        self.add_log("Sistem siap.")

        if lock_detection:
            self.add_log("Menunggu area sensor kosong selama 1 detik...", important=True)
        else:
            self.add_log("Menunggu pengguna...", important=True)

    def reset_system(self):
        was_running = self.running
        self.running = False
        self.prepare_waiting_state(clear_log=True)

        if not was_running and self.camera_label is not None:
            self.camera_label.config(image="", text="Kamera belum aktif")
            self.current_photo = None

        if was_running:
            self.running = True
            self.add_log("Sistem direset.")
        else:
            self.detector.stop()

        if self.start_button is not None:
            if self.running:
                self.start_button.config(state=tk.DISABLED)
            else:
                self.start_button.config(state=tk.NORMAL)

    def exit_app(self):
        self.running = False
        self.detector.stop()
        self.root.destroy()
