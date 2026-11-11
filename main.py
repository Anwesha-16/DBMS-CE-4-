
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date
import math

# =====================================================
# 1. DATABASE CONFIGURATION
# =====================================================

DB_PATH = Path(__file__).resolve().parent / "Hospital_Ward.db"


def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def initialize_database():

    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            emergency_contact TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admissions (
            admission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            room_number TEXT NOT NULL,
            admission_date TEXT NOT NULL,
            FOREIGN KEY (patient_id)
                REFERENCES patients(patient_id)
                ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS treatments (
            treatment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_id INTEGER NOT NULL,
            procedure_name TEXT NOT NULL,
            cost REAL NOT NULL CHECK(cost >= 0),
            FOREIGN KEY (admission_id)
                REFERENCES admissions(admission_id)
                ON DELETE CASCADE
        )
    """)

    # Seed records only when all three tables are empty
    cur.execute("""
        SELECT
            (SELECT COUNT(*) FROM patients),
            (SELECT COUNT(*) FROM admissions),
            (SELECT COUNT(*) FROM treatments)
    """)

    counts = cur.fetchone()

    if counts == (0, 0, 0):

        patients = [
            ("Rahul Sharma", "9876543210"),
            ("Priya Verma", "9876543211"),
            ("Amit Kumar", "9876543212"),
            ("Sneha Gupta", "9876543213"),
            ("Arjun Singh", "9876543214")
        ]

        cur.executemany("""
            INSERT INTO patients (name, emergency_contact)
            VALUES (?, ?)
        """, patients)

        admissions = [
            (1, "101", "2026-11-01"),
            (2, "102", "2026-11-02"),
            (3, "103", "2026-11-03"),
            (1, "104", "2026-11-04"),
            (4, "105", "2026-11-04"),
            (5, "106", "2026-11-04")
        ]

        cur.executemany("""
            INSERT INTO admissions
            (patient_id, room_number, admission_date)
            VALUES (?, ?, ?)
        """, admissions)

        treatments = [
            (1, "Blood Test", 500),
            (1, "X-Ray", 1200),
            (2, "ECG", 800),
            (3, "General Checkup", 1000),
            (4, "MRI Scan", 3500),
            (4, "Blood Test", 500),
            (5, "Ultrasound", 1800),
            (6, "CT Scan", 4000)
        ]

        cur.executemany("""
            INSERT INTO treatments
            (admission_id, procedure_name, cost)
            VALUES (?, ?, ?)
        """, treatments)

    con.commit()
    con.close()


# =====================================================
# 2. MAIN APPLICATION
# =====================================================

class HospitalWardApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Hospital Ward Operations Management System")
        self.root.geometry("1450x900")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#F2F7F4")

        self.setup_style()
        self.create_header()
        self.create_insert_panel()
        self.create_delete_panel()
        self.create_tabs()

        self.refresh_all()

    # =================================================
    # 3. EMERALD GREEN THEME
    # =================================================

    def setup_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.colors = {
            "green": "#176B55",
            "dark_green": "#104B3B",
            "mint": "#E4F1E9",
            "background": "#F2F7F4",
            "white": "#FFFFFF",
            "text": "#243B35",
            "border": "#C8DDD1",
            "alternate": "#F0F7F2"
        }

        style.configure(
            "TFrame",
            background=self.colors["background"]
        )

        style.configure(
            "TLabel",
            background=self.colors["white"],
            foreground=self.colors["text"],
            font=("Arial", 10)
        )

        style.configure(
            "TLabelframe",
            background=self.colors["white"],
            bordercolor=self.colors["border"],
            relief="solid",
            padding=8
        )

        style.configure(
            "TLabelframe.Label",
            background=self.colors["background"],
            foreground=self.colors["green"],
            font=("Arial", 11, "bold")
        )

        style.configure(
            "TEntry",
            fieldbackground=self.colors["white"],
            foreground=self.colors["text"],
            padding=7
        )

        style.configure(
            "TCombobox",
            fieldbackground=self.colors["white"],
            background=self.colors["mint"],
            foreground=self.colors["text"],
            padding=7
        )

        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", self.colors["white"])
            ]
        )

        style.configure(
            "TButton",
            background=self.colors["green"],
            foreground=self.colors["white"],
            font=("Arial", 10, "bold"),
            padding=(12, 9),
            borderwidth=0
        )

        style.map(
            "TButton",
            background=[
                ("active", self.colors["dark_green"]),
                ("pressed", self.colors["dark_green"])
            ],
            foreground=[
                ("active", self.colors["white"])
            ]
        )

        style.configure(
            "TNotebook",
            background=self.colors["background"],
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background=self.colors["mint"],
            foreground=self.colors["dark_green"],
            font=("Arial", 10, "bold"),
            padding=[15, 10]
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", self.colors["green"]),
                ("active", "#C8E2D1")
            ],
            foreground=[
                ("selected", self.colors["white"])
            ]
        )

        style.configure(
            "Treeview",
            background=self.colors["white"],
            fieldbackground=self.colors["white"],
            foreground=self.colors["text"],
            rowheight=32,
            font=("Arial", 10),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["green"],
            foreground=self.colors["white"],
            font=("Arial", 10, "bold"),
            padding=10
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#B9DDC9")
            ],
            foreground=[
                ("selected", self.colors["dark_green"])
            ]
        )

    # =================================================
    # 4. HEADER
    # =================================================

    def create_header(self):

        header = tk.Frame(
            self.root,
            bg="#176B55",
            height=110
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="HOSPITAL WARD MANAGEMENT",
            font=("Arial", 25, "bold"),
            bg="#176B55",
            fg="white"
        ).pack(pady=(20, 5))

        tk.Label(
            header,
            text="Patient Admissions  |  Medical Treatments  |  Ward Operations",
            font=("Arial", 11),
            bg="#176B55",
            fg="#E1F3EA"
        ).pack()

    # =================================================
    # 5. INSERT PANEL
    # =================================================

    def create_insert_panel(self):

        panel = ttk.LabelFrame(
            self.root,
            text="  PATIENT REGISTRATION AND ADMISSION  ",
            padding=15
        )

        panel.pack(
            fill="x",
            padx=15,
            pady=10
        )

        self.name_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.room_var = tk.StringVar()
        self.procedure_var = tk.StringVar()
        self.cost_var = tk.StringVar()

        fields = [
            ("Patient Name:", self.name_var),
            ("Emergency Contact:", self.contact_var),
            ("Room Number:", self.room_var),
            ("Procedure Name:", self.procedure_var),
            ("Treatment Cost (₹):", self.cost_var)
        ]

        positions = [
            (0, 0),
            (0, 2),
            (0, 4),
            (1, 0),
            (1, 2)
        ]

        for (label, variable), (row, col) in zip(fields, positions):

            ttk.Label(
                panel,
                text=label
            ).grid(
                row=row,
                column=col,
                padx=8,
                pady=10,
                sticky="w"
            )

            ttk.Entry(
                panel,
                textvariable=variable,
                width=24
            ).grid(
                row=row,
                column=col + 1,
                padx=8,
                pady=10
            )

        ttk.Button(
            panel,
            text="ADD PATIENT / ADMISSION / TREATMENT",
            command=self.insert_record
        ).grid(
            row=1,
            column=4,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="ew"
        )

    # =================================================
    # 6. INSERT RECORD LOGIC
    # =================================================

    def insert_record(self):

        name = self.name_var.get().strip()
        contact = self.contact_var.get().strip()
        room = self.room_var.get().strip()
        procedure = self.procedure_var.get().strip()
        cost_text = self.cost_var.get().strip()

        if not all([name, contact, room, procedure, cost_text]):

            messagebox.showwarning(
                "Missing Information",
                "Please fill in all fields."
            )
            return

        if not contact.isdigit() or len(contact) < 7:

            messagebox.showwarning(
                "Invalid Contact",
                "Enter a valid emergency contact number."
            )
            return

        try:

            cost = float(cost_text)

            if not math.isfinite(cost) or cost < 0:
                raise ValueError

        except ValueError:

            messagebox.showwarning(
                "Invalid Treatment Cost",
                "Treatment cost must be a valid non-negative number."
            )
            return

        con = connect_db()

        try:

            cur = con.cursor()

            # Check whether patient already exists

            cur.execute("""
                SELECT patient_id
                FROM patients
                WHERE name = ?
            """, (name,))

            result = cur.fetchone()

            if result:

                patient_id = result[0]

            else:

                cur.execute("""
                    INSERT INTO patients
                    (name, emergency_contact)
                    VALUES (?, ?)
                """, (name, contact))

                patient_id = cur.lastrowid

            # Create admission

            admission_date = date.today().isoformat()

            cur.execute("""
                INSERT INTO admissions
                (patient_id, room_number, admission_date)
                VALUES (?, ?, ?)
            """, (patient_id, room, admission_date))

            admission_id = cur.lastrowid

            # Create treatment

            cur.execute("""
                INSERT INTO treatments
                (admission_id, procedure_name, cost)
                VALUES (?, ?, ?)
            """, (admission_id, procedure, cost))

            treatment_id = cur.lastrowid

            con.commit()

            # Clear input fields

            self.name_var.set("")
            self.contact_var.set("")
            self.room_var.set("")
            self.procedure_var.set("")
            self.cost_var.set("")

            self.refresh_all()

            messagebox.showinfo(
                "Record Added",
                f"Patient record added successfully!\n\n"
                f"Patient ID: {patient_id}\n"
                f"Admission ID: {admission_id}\n"
                f"Treatment ID: {treatment_id}"
            )

        except sqlite3.Error as error:

            con.rollback()

            messagebox.showerror(
                "Database Error",
                str(error)
            )

        finally:

            con.close()

    # =================================================
    # 7. DELETE PANEL
    # =================================================

    def create_delete_panel(self):

        panel = ttk.LabelFrame(
            self.root,
            text="  MANAGE HOSPITAL RECORDS  ",
            padding=15
        )

        panel.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.patient_delete_var = tk.StringVar()
        self.admission_delete_var = tk.StringVar()

        # Patient dropdown

        ttk.Label(
            panel,
            text="Delete Patient Profile:"
        ).grid(
            row=0,
            column=0,
            padx=8,
            pady=9,
            sticky="w"
        )

        self.patient_dropdown = ttk.Combobox(
            panel,
            textvariable=self.patient_delete_var,
            width=42,
            state="readonly"
        )

        self.patient_dropdown.grid(
            row=0,
            column=1,
            padx=8,
            pady=9
        )

        ttk.Button(
            panel,
            text="DELETE PATIENT",
            command=self.delete_patient
        ).grid(
            row=0,
            column=2,
            padx=12,
            pady=9
        )

        # Admission dropdown

        ttk.Label(
            panel,
            text="Delete Admission / Discharge:"
        ).grid(
            row=1,
            column=0,
            padx=8,
            pady=9,
            sticky="w"
        )

        self.admission_dropdown = ttk.Combobox(
            panel,
            textvariable=self.admission_delete_var,
            width=42,
            state="readonly"
        )

        self.admission_dropdown.grid(
            row=1,
            column=1,
            padx=8,
            pady=9
        )

        ttk.Button(
            panel,
            text="DELETE ADMISSION",
            command=self.delete_admission
        ).grid(
            row=1,
            column=2,
            padx=12,
            pady=9
        )

    # =================================================
    # 8. DELETE PATIENT
    # =================================================

    def delete_patient(self):

        selected = self.patient_delete_var.get()

        if not selected:

            messagebox.showwarning(
                "Selection Required",
                "Please select a patient."
            )
            return

        patient_id = int(selected.split(" | ")[0])

        confirm = messagebox.askyesno(
            "Confirm Patient Deletion",
            "Deleting this patient will also delete "
            "all associated admissions and treatments.\n\n"
            "Do you want to continue?"
        )

        if not confirm:
            return

        con = connect_db()

        try:

            con.execute("""
                DELETE FROM patients
                WHERE patient_id = ?
            """, (patient_id,))

            con.commit()

            self.refresh_all()

            messagebox.showinfo(
                "Success",
                "Patient and associated records deleted successfully."
            )

        except sqlite3.Error as error:

            con.rollback()

            messagebox.showerror(
                "Database Error",
                str(error)
            )

        finally:

            con.close()

    # =================================================
    # 9. DELETE ADMISSION
    # =================================================

    def delete_admission(self):

        selected = self.admission_delete_var.get()

        if not selected:

            messagebox.showwarning(
                "Selection Required",
                "Please select an admission."
            )
            return

        admission_id = int(selected.split(" | ")[0])

        confirm = messagebox.askyesno(
            "Confirm Admission Deletion",
            "Deleting this admission will also delete "
            "its associated treatments.\n\n"
            "The patient profile will remain.\n\n"
            "Continue?"
        )

        if not confirm:
            return

        con = connect_db()

        try:

            con.execute("""
                DELETE FROM admissions
                WHERE admission_id = ?
            """, (admission_id,))

            con.commit()

            self.refresh_all()

            messagebox.showinfo(
                "Success",
                "Admission and associated treatments deleted."
            )

        except sqlite3.Error as error:

            con.rollback()

            messagebox.showerror(
                "Database Error",
                str(error)
            )

        finally:

            con.close()

    # =================================================
    # 10. CREATE FOUR DISPLAY TABS
    # =================================================

    def create_tabs(self):

        frame = ttk.Frame(self.root)

        frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=12
        )

        self.notebook = ttk.Notebook(frame)

        self.notebook.pack(
            fill="both",
            expand=True
        )

        self.tree_manifest = self.create_table_tab(
            "Master Ward Manifest"
        )

        self.tree_patients = self.create_table_tab(
            "Patients"
        )

        self.tree_admissions = self.create_table_tab(
            "Admissions"
        )

        self.tree_treatments = self.create_table_tab(
            "Treatments"
        )

    # =================================================
    # 11. CREATE TABLE VIEW
    # =================================================

    def create_table_tab(self, title):

        frame = ttk.Frame(self.notebook)

        self.notebook.add(
            frame,
            text=title
        )

        container = ttk.Frame(frame)

        container.pack(
            fill="both",
            expand=True
        )

        tree = ttk.Treeview(
            container,
            show="headings"
        )

        vertical = ttk.Scrollbar(
            container,
            orient="vertical",
            command=tree.yview
        )

        horizontal = ttk.Scrollbar(
            container,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        container.rowconfigure(
            0,
            weight=1
        )

        container.columnconfigure(
            0,
            weight=1
        )

        return tree

    # =================================================
    # 12. POPULATE TABLES
    # =================================================

    def populate_tree(self, tree, columns, rows):

        tree.delete(*tree.get_children())

        tree["columns"] = columns

        for column in columns:

            tree.heading(
                column,
                text=column.replace("_", " ").title()
            )

            tree.column(
                column,
                width=155,
                minwidth=100,
                anchor="center"
            )

        tree.tag_configure(
            "even",
            background="#FFFFFF"
        )

        tree.tag_configure(
            "odd",
            background="#F0F7F2"
        )

        for index, row in enumerate(rows):

            tag = "even" if index % 2 == 0 else "odd"

            tree.insert(
                "",
                "end",
                values=row,
                tags=(tag,)
            )

    # =================================================
    # 13. REFRESH ALL TABLES AND DROPDOWNS
    # =================================================

    def refresh_all(self):

        con = connect_db()
        cur = con.cursor()

        try:

            # Master Ward Manifest

            cur.execute("""
                SELECT
                    p.patient_id,
                    p.name AS patient_name,
                    p.emergency_contact,
                    a.admission_id,
                    a.room_number,
                    a.admission_date,
                    t.treatment_id,
                    t.procedure_name,
                    t.cost
                FROM patients p
                INNER JOIN admissions a
                    ON p.patient_id = a.patient_id
                INNER JOIN treatments t
                    ON a.admission_id = t.admission_id
                ORDER BY a.admission_id, t.treatment_id
            """)

            self.populate_tree(
                self.tree_manifest,
                [
                    "patient_id",
                    "patient_name",
                    "emergency_contact",
                    "admission_id",
                    "room_number",
                    "admission_date",
                    "treatment_id",
                    "procedure_name",
                    "cost"
                ],
                cur.fetchall()
            )

            # Patients table

            cur.execute("""
                SELECT *
                FROM patients
                ORDER BY patient_id
            """)

            patients = cur.fetchall()

            self.populate_tree(
                self.tree_patients,
                [
                    "patient_id",
                    "name",
                    "emergency_contact"
                ],
                patients
            )

            # Admissions table

            cur.execute("""
                SELECT *
                FROM admissions
                ORDER BY admission_id
            """)

            admissions = cur.fetchall()

            self.populate_tree(
                self.tree_admissions,
                [
                    "admission_id",
                    "patient_id",
                    "room_number",
                    "admission_date"
                ],
                admissions
            )

            # Treatments table

            cur.execute("""
                SELECT *
                FROM treatments
                ORDER BY treatment_id
            """)

            treatments = cur.fetchall()

            self.populate_tree(
                self.tree_treatments,
                [
                    "treatment_id",
                    "admission_id",
                    "procedure_name",
                    "cost"
                ],
                treatments
            )

            # Patient dropdown

            self.patient_dropdown["values"] = [
                f"{row[0]} | {row[1]}"
                for row in patients
            ]

            # Admission dropdown

            cur.execute("""
                SELECT
                    a.admission_id,
                    p.name,
                    a.room_number,
                    a.admission_date
                FROM admissions a
                INNER JOIN patients p
                    ON a.patient_id = p.patient_id
                ORDER BY a.admission_id
            """)

            admission_options = cur.fetchall()

            self.admission_dropdown["values"] = [
                f"{row[0]} | {row[1]} | Room {row[2]} | {row[3]}"
                for row in admission_options
            ]

            # Clear old dropdown selections

            self.patient_delete_var.set("")
            self.admission_delete_var.set("")

        finally:

            con.close()


# =====================================================
# 14. APPLICATION STARTUP
# =====================================================

def main():

    try:

        initialize_database()

        root = tk.Tk()

        app = HospitalWardApp(root)

        root.mainloop()

    except tk.TclError as error:

        print("GUI could not start:", error)

    except sqlite3.Error as error:

        print("Database Error:", error)

    except Exception as error:

        print("Application Error:", error)


if __name__ == "__main__":
    main()
