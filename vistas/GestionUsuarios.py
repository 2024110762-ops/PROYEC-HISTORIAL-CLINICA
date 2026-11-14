import tkinter as tk
from tkinter import messagebox, ttk

class GestionUsuarios:
    def __init__(self, root):
        self.root = root
        self.root.title("Módulo 2 - Gestión de Usuarios")
        self.root.geometry("640x460")
        self.root.resizable(False, False)

        self.usuarios = [
            ("71234567", "Dr. Carlos Mendoza", "Médico", "cmendoza"),
            ("72345678", "Lic. Ana Torres", "Enfermera", "atorres"),
            ("73456789", "Ing. Alanis Inga", "Administrador", "ainga")
        ]

        frame_form = tk.LabelFrame(root, text="Registro y Administración de Usuarios", padx=12, pady=12, font=("Arial", 10, "bold"))
        frame_form.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_form, text="DNI (8 dígitos):").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_dni = tk.Entry(frame_form, width=25)
        self.ent_dni.grid(row=0, column=1, padx=8)

        tk.Label(frame_form, text="Nombre Completo:").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_nombre = tk.Entry(frame_form, width=25)
        self.ent_nombre.grid(row=1, column=1, padx=8)

        tk.Label(frame_form, text="Rol en Sistema:").grid(row=0, column=2, sticky="w", pady=4)
        self.cb_rol = ttk.Combobox(frame_form, values=["Médico", "Enfermera", "Recepcionista", "Administrador"], state="readonly", width=19)
        self.cb_rol.grid(row=0, column=3, padx=8)

        tk.Label(frame_form, text="Usuario:").grid(row=1, column=2, sticky="w", pady=4)
        self.ent_user = tk.Entry(frame_form, width=22)
        self.ent_user.grid(row=1, column=3, padx=8)

        btn_frame = tk.Frame(frame_form)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        tk.Button(btn_frame, text="Registrar Usuario", bg="#2e7d32", fg="white", width=16, command=self.guardar_usuario).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar Seleccionado", bg="#c62828", fg="white", width=18, command=self.eliminar_usuario).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Limpiar Campos", width=14, command=self.limpiar_campos).pack(side="left", padx=5)

        self.tabla = ttk.Treeview(root, columns=("DNI", "Nombre", "Rol", "Usuario"), show="headings", height=10)
        for col, ancho in [("DNI", 100), ("Nombre", 210), ("Rol", 140), ("Usuario", 130)]:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True, padx=15, pady=10)

        self.cargar_tabla()

    def cargar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for u in self.usuarios:
            self.tabla.insert("", "end", values=u)

    def limpiar_campos(self):
        self.ent_dni.delete(0, tk.END)
        self.ent_nombre.delete(0, tk.END)
        self.cb_rol.set("")
        self.ent_user.delete(0, tk.END)

    def guardar_usuario(self):
        dni = self.ent_dni.get().strip()
        nombre = self.ent_nombre.get().strip()
        rol = self.cb_rol.get().strip()
        user = self.ent_user.get().strip()

        if not dni or not nombre or not rol or not user:
            messagebox.showerror("Error de Validación", "Todos los campos son obligatorios. Complete la información.")
            return
        if not dni.isdigit() or len(dni) != 8:
            messagebox.showerror("Error de Formato", "El DNI debe contener exactamente 8 dígitos numéricos.")
            return
        if len(nombre) < 5:
            messagebox.showerror("Error de Validación", "Ingrese el nombre y apellido completo del usuario.")
            return
        if any(u[0] == dni for u in self.usuarios):
            messagebox.showwarning("Usuario Duplicado", f"Ya existe un usuario registrado con el DNI {dni}.")
            return

        self.usuarios.append((dni, nombre, rol, user))
        self.cargar_tabla()
        self.limpiar_campos()
        messagebox.showinfo("Registro Exitoso", "El usuario ha sido registrado correctamente en el sistema.")

    def eliminar_usuario(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selección Requerida", "Seleccione un usuario de la tabla para eliminar.")
            return
        valores = self.tabla.item(seleccion[0], "values")
        self.usuarios = [u for u in self.usuarios if u[0] != valores[0]]
        self.cargar_tabla()
        messagebox.showinfo("Eliminado", f"Usuario {valores[1]} eliminado correctamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GestionUsuarios(root)
    root.mainloop()
