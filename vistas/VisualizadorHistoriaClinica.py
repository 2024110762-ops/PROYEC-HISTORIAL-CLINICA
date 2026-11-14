import tkinter as tk
from tkinter import messagebox, ttk

class RegistroAuditoriaVista:
    def __init__(self, root):
        self.root = root
        self.root.title("Módulo 2 - Registro de Auditoría y Seguridad")
        self.root.geometry("700x440")
        self.root.resizable(False, False)

        self.logs = [
            ("2026-11-14 08:15:10", "cmendoza", "CONSULTA", "Visualizó historia clínica del paciente DNI 70112233"),
            ("2026-11-14 09:02:44", "atorres", "ACTUALIZACIÓN", "Registró resultados de laboratorio DNI 70445566"),
            ("2026-11-14 10:30:19", "ainga", "SEGURIDAD", "Creó nuevo usuario médico en Gestión de Usuarios"),
            ("2026-11-14 11:12:05", "cmendoza", "CONSULTA", "Consultó hemograma completo DNI 70112233"),
            ("2026-11-14 11:45:30", "ainga", "AUDITORÍA", "Exportó reporte de actividad del sistema")
        ]

        frame_filtro = tk.LabelFrame(root, text="Control y Seguimiento de Auditoría", padx=10, pady=10, font=("Arial", 10, "bold"))
        frame_filtro.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_filtro, text="Filtrar por Usuario:").pack(side="left", padx=5)
        self.ent_usuario = tk.Entry(frame_filtro, width=22)
        self.ent_usuario.pack(side="left", padx=5)

        tk.Button(frame_filtro, text="Filtrar Registros", bg="#4527a0", fg="white", width=16, command=self.filtrar).pack(side="left", padx=5)
        tk.Button(frame_filtro, text="Mostrar Todos", width=14, command=self.mostrar_todo).pack(side="left", padx=5)

        self.tabla = ttk.Treeview(root, columns=("Fecha/Hora", "Usuario", "Módulo/Acción", "Descripción del Evento"), show="headings", height=13)
        for col, w in [("Fecha/Hora", 140), ("Usuario", 95), ("Módulo/Acción", 115), ("Descripción del Evento", 315)]:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=w)
        self.tabla.pack(fill="both", expand=True, padx=15, pady=10)

        self.mostrar_todo()

    def mostrar_todo(self):
        self.ent_usuario.delete(0, tk.END)
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for log in self.logs:
            self.tabla.insert("", "end", values=log)

    def filtrar(self):
        usuario = self.ent_usuario.get().strip().lower()
        if not usuario:
            messagebox.showerror("Error de Validación", "Ingrese un nombre de usuario para filtrar la auditoría.")
            return

        filtrados = [l for l in self.logs if usuario in l[1].lower()]
        if not filtrados:
            messagebox.showinfo("Sin Coincidencias", f"No se encontraron registros para el usuario '{usuario}'.")
            return

        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for log in filtrados:
            self.tabla.insert("", "end", values=log)

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroAuditoriaVista(root)
    root.mainloop()
