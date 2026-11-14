import tkinter as tk
from tkinter import messagebox

class VisualizadorHistoriaClinica:
    def __init__(self, root):
        self.root = root
        self.root.title("Módulo 2 - Visualizador de Historia Clínica")
        self.root.geometry("640x480")
        self.root.resizable(False, False)

        self.historias = {
            "70112233": {
                "nombre": "Juan Carlos Pérez Quispe",
                "edad": "34 años",
                "sexo": "Masculino",
                "grupo": "O+",
                "alergias": "Penicilina",
                "antecedentes": "Sin enfermedades crónicas previas.",
                "diagnostico": "Faringitis aguda bacteriana leve. Signos vitales estables.",
                "tratamiento": "Amoxicilina 500mg c/8h por 5 días + Ibuprofeno 400mg condicional."
            },
            "70445566": {
                "nombre": "María Elena Gómez Rojas",
                "edad": "47 años",
                "sexo": "Femenino",
                "grupo": "A+",
                "alergias": "Ninguna conocida",
                "antecedentes": "Hipertensión arterial controlada.",
                "diagnostico": "Dislipidemia leve detectada en control de rutina.",
                "tratamiento": "Dieta hipograsa, actividad física diaria y reevaluación en 30 días."
            }
        }

        frame_top = tk.LabelFrame(root, text="Consultar Expediente Clínico", padx=10, pady=10, font=("Arial", 10, "bold"))
        frame_top.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_top, text="DNI del Paciente:").pack(side="left", padx=5)
        self.ent_dni = tk.Entry(frame_top, width=22)
        self.ent_dni.pack(side="left", padx=5)

        tk.Button(frame_top, text="Visualizar Historia", bg="#00695c", fg="white", width=18, command=self.cargar_historia).pack(side="left", padx=5)
        tk.Button(frame_top, text="Limpiar", width=10, command=self.limpiar).pack(side="left", padx=5)

        self.txt_area = tk.Text(root, width=74, height=20, font=("Consolas", 10), state="disabled", bg="#f9f9f9", padx=10, pady=10)
        self.txt_area.pack(padx=15, pady=10)

    def limpiar(self):
        self.ent_dni.delete(0, tk.END)
        self.txt_area.config(state="normal")
        self.txt_area.delete("1.0", tk.END)
        self.txt_area.config(state="disabled")

    def cargar_historia(self):
        dni = self.ent_dni.get().strip()
        if not dni:
            messagebox.showerror("Error de Validación", "Ingrese el DNI del paciente para visualizar su historia.")
            return
        if not dni.isdigit() or len(dni) != 8:
            messagebox.showerror("Error de Formato", "El DNI debe contener exactamente 8 números.")
            return
        if dni not in self.historias:
            messagebox.showwarning("No Encontrado", f"No se encontró ninguna historia clínica con el DNI {dni}.")
            return

        h = self.historias[dni]
        reporte = (
            f"============================================================\n"
            f"               HISTORIA CLÍNICA ELECTRÓNICA                 \n"
            f"============================================================\n"
            f" DNI PACIENTE   : {dni}\n"
            f" NOMBRE         : {h['nombre']}\n"
            f" EDAD / SEXO    : {h['edad']} / {h['sexo']}\n"
            f" GRUPO SANG.    : {h['grupo']}\n"
            f" ALERGIAS       : {h['alergias']}\n"
            f"------------------------------------------------------------\n"
            f" ANTECEDENTES:\n {h['antecedentes']}\n\n"
            f" DIAGNÓSTICO ACTUAL:\n {h['diagnostico']}\n\n"
            f" TRATAMIENTO INDICADO:\n {h['tratamiento']}\n"
            f"============================================================\n"
        )

        self.txt_area.config(state="normal")
        self.txt_area.delete("1.0", tk.END)
        self.txt_area.insert(tk.END, reporte)
        self.txt_area.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualizadorHistoriaClinica(root)
    root.mainloop()
