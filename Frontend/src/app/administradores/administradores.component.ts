import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { ToastModule } from 'primeng/toast';

import { Administrador } from '../modelo';
import { ApiService, DetalleError as DetalleErrorComun } from '../service/api.service';

@Component({
  selector: 'app-administradores',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonModule, DialogModule, InputTextModule, TableModule, ToastModule],
  providers: [MessageService],
  templateUrl: './administradores.component.html',
})
export class AdministradoresComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly mensajeria = inject(MessageService);
  private readonly constructorFormulario = inject(FormBuilder);

  readonly administradores = signal<Administrador[]>([]);
  readonly dialogoVisible = signal(false);
  readonly administradorEditando = signal<Administrador | null>(null);
  private imagen: File | null = null;

  readonly formulario = this.constructorFormulario.nonNullable.group({
    dni: ['', Validators.required],
    nombre: ['', Validators.required],
    apellidos: ['', Validators.required],
    usuario: [0, Validators.required],
    contraseña: [''],
    estado: [true],
  });

  ngOnInit(): void {
    this.GetAdministradores();
  }

  GetAdministradores(): void {
    this.api.GetAdministradores().subscribe({ next: (lista) => this.administradores.set(lista) });
  }

  AbrirNuevo(): void {
    this.administradorEditando.set(null);
    this.formulario.reset({ dni: '', nombre: '', apellidos: '', usuario: 0, contraseña: '', estado: true });
    this.imagen = null;
    this.dialogoVisible.set(true);
  }

  AbrirEditar(administrador: Administrador): void {
    this.administradorEditando.set(administrador);
    this.formulario.patchValue({ ...administrador, contraseña: '' });
    this.imagen = null;
    this.dialogoVisible.set(true);
  }

  SeleccionarImagen(evento: Event): void {
    this.imagen = (evento.target as HTMLInputElement).files?.item(0) ?? null;
  }

  GuardarAdministrador(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }
    const datos = new FormData();
    Object.entries(this.formulario.getRawValue()).forEach(([clave, valor]) => datos.append(clave, String(valor ?? '')));
    if (this.imagen) {
      datos.append('imagen', this.imagen);
    }
    const administrador = this.administradorEditando();
    const operacion = administrador
      ? this.api.PutAdministrador(administrador.id, datos)
      : this.api.PostAdministrador(datos);
    operacion.subscribe({
      next: () => {
        this.dialogoVisible.set(false);
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: 'Administrador guardado.' });
        this.GetAdministradores();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo) }),
    });
  }

  EliminarAdministrador(administrador: Administrador): void {
    if (!confirm(`¿Eliminar al administrador ${administrador.nombre}?`)) {
      this.mensajeria.add({ severity: 'info', summary: 'No se realizaron cambios', detail: 'Eliminación cancelada.' });
      return;
    }
    this.api.DeleteAdministrador(administrador.id).subscribe({
      next: () => {
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: 'Administrador eliminado.' });
        this.GetAdministradores();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo, 'eliminar') }),
    });
  }
}
