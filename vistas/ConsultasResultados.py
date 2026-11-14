import tkinter as tk
from tkinter import messagebox, ttk

class ConsultasResultados:
    def __init__(self, root):
        self.root = root
        self.root.title("Módulo 2 - Consulta de Resultados Clínicos")
        self.root.geometry("680x440")
        self.root.resizable(False, False)

        self.resultados_db = {
            "70112233": [
                ("2026-11-10", "Hemograma Completo", "Normal (Hb: 14.2 g/dL)", "Dr. Carlos Mendoza"),
                ("2026-11-12", "Glucosa en Ayunas", "92 mg/dL - Rango Óptimo", "Dr. Carlos Mendoza")
            ],
            "70445566": [
                ("2026-11-08", "Perfil Lipídico", "Colesterol Total: 218 mg/dL (Alto)", "Lic. Ana Torres"),
                ("2026-11-11", "Radiografía de Tórax", "Sin alteraciones pleuropulmonares", "Dr. Carlos Mendoza")
            ]
        }

        frame_busq = tk.LabelFrame(root, text="Búsqueda de Exámenes y Resultados", padx=10, pady=10, font=("Arial", 10, "bold"))
        frame_busq.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_busq, text="DNI del Paciente:").pack(side="left", padx=5)
        self.ent_dni = tk.Entry(frame_busq, width=22)
        self.ent_dni.pack(side="left", padx=5)

        tk.Button(frame_busq, text="Buscar Resultados", bg="#1565c0", fg="white", width=16, command=self.buscar).pack(side="left", padx=5)
        tk.Button(frame_busq, text="Mostrar Todos", width=14, command=self.mostrar_todos).pack(side="left", padx=5)

        self.tabla = ttk.Treeview(root, columns=("DNI", "Fecha", "Examen", "Resultado", "Médico"), show="headings", height=13)
        for col, w in [("DNI", 85), ("Fecha", 95), ("Examen", 150), ("Resultado", 190), ("Médico", 125)]:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=w)
        self.tabla.pack(fill="both", expand=True, padx=15, pady=10)

        self.mostrar_todos()

    def mostrar_todos(self):
        self.ent_dni.delete(0, tk.END)
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for dni, lista in self.resultados_db.items():
            for reg in lista:
                self.tabla.insert("", "end", values=(dni, *reg))

    def buscar(self):
        dni = self.ent_dni.get().strip()
        if not dni:
            messagebox.showerror("Error de Validación", "Debe ingresar el DNI del paciente para buscar.")
            return
        if not dni.isdigit() or len(dni) != 8:
            messagebox.showerror("Error de Formato", "El DNI ingresado no es válido (debe tener 8 dígitos).")
            return

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        if dni in self.resultados_db:
            for reg in self.resultados_db[dni]:
                self.tabla.insert("", "end", values=(dni, *reg))
        else:
            messagebox.showinfo("Sin Resultados", f"No existen resultados clínicos registrados para el DNI {dni}.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConsultasResultados(root)
    root.mainloop()
