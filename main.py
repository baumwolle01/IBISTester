import serial
import os
import sys
import glob
from datetime import datetime
import tkinter as tk

# --- KONFIGURATION ---
SERIAL_PORT = '/dev/ttyUSB0' #Hier an den entsprechenden Port anpassen
BAUD_RATE = 1200

# IBIS Umwandlungstabelle
class IBISComm:
    IBIS_MAP = {    
        'ä': '{', 'ö': '|', 'ü': '}', 'ß': '~',
        'Ä': '[', 'Ö': '\\', 'Ü': ']', 'µ': '`'
    }
    
    def __init__(self, port_config):
        self.ser = None
        # Rechte für den USB-Port erzwingen
        try: os.system(f"sudo chmod 666 {port_config}")
        except: pass
            
        try:
            # WICHTIG: stopbits=2 für den echten IBIS-Standard!
            self.ser = serial.Serial(port_config, BAUD_RATE, bytesize=7, parity='E', stopbits=2, timeout=1)
            print(f"Verbunden mit {port_config}")
        except:
            ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
            for p in ports:
                try:
                    self.ser = serial.Serial(p, BAUD_RATE, bytesize=7, parity='E', stopbits=2, timeout=1)
                    print(f"Alternativ verbunden mit {p}")
                    break
                except: continue
                
    def translate(self, text):
        # Übersetzt deutsche Umlaute in IBIS-Sonderzeichen.
        res = ""
        for char in str(text):
            res += self.IBIS_MAP.get(char, char)
        return res

    def send(self, command, data):
        # Bereitet Daten vor und sendet sie an den Bus.
        # 1. Übersetzung und Formatierung
        clean_data = self.translate(data)
        actual_cmd = command[0] if command.startswith("aA") else command
       
        # Hier werden die Datensätze "aufgefüllt" 
        if command == "l":      clean_data = str(clean_data).zfill(3)
        elif command == "lE":   clean_data = str(clean_data).zfill(2)
        elif command == "z":    clean_data = str(clean_data).zfill(3)
        elif command == "v" or command == "zI6": 
            clean_data = f"{str(clean_data)[:24]:<24}" # TODO: Fix für die 24 Zeichen begrenzung bauen
        elif command.startswith("aA"): 
            # Standard Zielanzeige (z.B. A11)
            prefix = "A11" if "A11" in command else "A21"
            clean_data = f"{prefix}{str(clean_data)[:16]:<16}"

        # 2. Checksumme berechnen (Startwert 0x7F)
        checksum_payload = f"{actual_cmd}{clean_data}\r"
        checksum = 0x7F
        for char in checksum_payload:
            checksum ^= ord(char)
        checksum &= 0x7F
        
        # 3. Finales Paket bauen
        full_msg = checksum_payload.encode('ascii', errors='ignore') + bytes([checksum])
        
        # Debug-Ausgabe
        display_output = checksum_payload.replace('\r', '<CR>')
        hex_checksum = hex(checksum).upper()[2:].zfill(2)
        
        if self.ser:
            self.ser.write(full_msg)
            print(f"out-> {display_output}<{hex_checksum}>")
        else:
            print(f"SIMULATION out-> {display_output}<{hex_checksum}>")

    def close(self):
        if self.ser: self.ser.close()

class IBISTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IBIS Tester")
        self.root.attributes("-fullscreen", True) # Setzt das Programm in den Vollbild-Modus
        self.root.bind("<Escape>", lambda e: self.root.destroy()) # ESC beendet das Programm
        self.ibis = IBISComm(SERIAL_PORT)
        
        # INIT Oriented Farben (Original-Look)
        self.bg_blue = "#66CCCC"
        self.btn_tan = "#CCC990"
        self.btn_orange = "#FFA500"
        self.header_yellow = "#CCC990"
        self.btn_ok = "#00FF00"
        self.btn_abort = "#B22222"

        self.main_container = tk.Frame(root, bg=self.bg_blue)
        self.main_container.pack(expand=True, fill='both')
        self.show_main_menu()

    def clear_frame(self):
        for widget in self.main_container.winfo_children(): widget.destroy()

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S  %d.%m.%Y")
        if hasattr(self, 'lbl_clock'): self.lbl_clock.config(text=now)
        self.root.after(1000, self.update_clock)

    def show_main_menu(self):
        self.clear_frame()
        top_bar = tk.Frame(self.main_container, bg=self.header_yellow, height=200)
        top_bar.pack(fill='x')
        self.lbl_clock = tk.Label(top_bar, bg=self.header_yellow, font=("Courier", 30, "bold"))
        self.lbl_clock.pack(side='left', padx=20)
        self.update_clock()

        grid_frame = tk.Frame(self.main_container, bg=self.bg_blue)
        grid_frame.pack(expand=True)

        # Hier werden die Menüeinträge mit den Datensätzen angepasst/erweitert
        menu_items = [
            ("Linie (DS001)", "l", "num"), 
            ("Sonderz. (DS001a)", "lE", "num"), 
            ("Zielnr. (DS003)", "z", "num"),
            ("Ziel (DS021 ANZ1) (A11)", "aA11", "list_z"), 
            ("Ziel (DS021 ANZ2) (A21)", "aA21", "list_z"),
            ("Ziel (DS003a)", "zA", "list_ziel"),            
            ("Innen (DS009 (v))", "v", "list_i"),
            ("Innen (DS003c (zI))", "zI6", "list_i"), #zI6 ist die 24 Zeichenbegrenzung
            ("", "", ""), 
            ("", "", "")
        ]

        r, c = 0, 0
        for label, cmd, mode in menu_items:
            if label:
                btn = tk.Button(grid_frame, text=label, bg=self.btn_tan, font=("Arial", 16, "bold"),
                                width=20, height=4, command=lambda m=mode, d=cmd: self.handle_action(m, d))
                btn.grid(row=r, column=c, padx=10, pady=10)
            c += 1
            if c > 2: c = 0; r += 1

        # Neustart-Button unten rechts, Startet das Gerät neu
        tk.Button(self.main_container, text="Sofort-\nNeustart", bg=self.btn_orange, font=("Arial", 16, "bold"),
                  width=12, height=3, command=self.restart_device).place(relx=0.9, rely=0.85, anchor="center")
        
        tk.Label(self.main_container, text="IBIS-Tester\nAlpha v.0.0.1", font=("Arial", 16, "bold"),
                  width=12, height=3) .place(relx=0.9, rely=0.95, anchor="center")

    def restart_device(self):
        self.ibis.close()
        os.system('sudo reboot')

    def handle_action(self, mode, cmd):
        if mode == "num": self.open_numpad(cmd)
        else: self.show_list_view("Ziel/Ziele.txt" if mode == "list_z" else "Innen/Innen.txt", cmd)

    def open_numpad(self, cmd):
        self.clear_frame()
        val = tk.StringVar()
        tk.Label(self.main_container, text=f"Eingabe: {cmd}", bg=self.bg_blue, font=("Arial", 16)).pack(pady=10)
        tk.Entry(self.main_container, textvariable=val, font=("Arial", 30), justify='center', width=10).pack(pady=10)
        pad = tk.Frame(self.main_container, bg=self.bg_blue)
        pad.pack()
        keys = ['1','2','3','4','5','6','7','8','9','<','0','OK']
        r, c = 0, 0
        for k in keys:
            color = self.btn_ok if k == 'OK' else "white"
            tk.Button(pad, text=k, font=("Arial", 18, "bold"), bg=color, width=5, height=2,
                      command=lambda x=k: self.press_num(x, val, cmd)).grid(row=r, column=c, padx=5, pady=5)
            c += 1
            if c > 2: c = 0; r += 1

    def press_num(self, key, var, cmd):
        if key == 'OK': 
            self.ibis.send(cmd, var.get())
            self.show_main_menu()
        elif key == '<': var.set(var.get()[:-1])
        else: var.set(var.get() + key)

    def show_list_view(self, path, cmd):
        self.clear_frame()
        title = "Ziele" if "Ziel" in path else "Innenanzeige"
        tk.Label(self.main_container, text=title, bg="#ADD8E6", font=("Arial", 20, "bold"), anchor="w", padx=20).pack(fill='x')
        lf = tk.Frame(self.main_container, bg="white")
        lf.pack(side='left', expand=True, fill='both', padx=10, pady=10)
        
        lb = tk.Listbox(lf, font=("Arial", 18), bg="#D3D3D3", selectbackground="black")
        lb.pack(side='left', expand=True, fill='both')
        
        # Scrollbar hinzufügen
        sb = tk.Scrollbar(lf)
        sb.pack(side='right', fill='y')
        lb.config(yscrollcommand=sb.set)
        sb.config(command=lb.yview)

        lb.insert(tk.END, "Datum/Uhrzeit")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f: 
                    if line.strip(): lb.insert(tk.END, line.strip())
        
        ft = tk.Frame(self.main_container, bg=self.bg_blue)
        ft.pack(side='bottom', fill='x', pady=20)
        tk.Button(ft, text="Abbruch", bg=self.btn_abort, fg="white", font=("Arial", 12, "bold"), 
                  width=15, height=2, command=self.show_main_menu).pack(side='left', padx=60)
        tk.Button(ft, text="OK", bg=self.btn_ok, font=("Arial", 12, "bold"), 
                  width=15, height=2, command=lambda: self.confirm_list(lb, cmd)).pack(side='right', padx=60)

    def confirm_list(self, lb, cmd):
        try:
            sel = lb.curselection()[0]
            text = lb.get(sel)
            if sel == 0: # Datum/Uhrzeit Fall
                text = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.ibis.send(cmd, text)
            self.show_main_menu()
        except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = IBISTesterApp(root)
    root.mainloop()
