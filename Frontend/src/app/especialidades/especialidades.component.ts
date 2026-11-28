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

import { Especialidad } from '../modelo';
import { ApiService, DetalleError as DetalleErrorComun } from '../service/api.service';
import { AuthService } from '../service/auth.service';

@Component({
  selector: 'app-especialidades',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    TableModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './especialidades.component.html',
})
export class EspecialidadesComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly autenticacion = inject(AuthService);
  private readonly mensajeria = inject(MessageService);
  private readonly constructorFormulario = inject(FormBuilder);

  readonly puedeGestionar = this.autenticacion.tieneRol('ADMIN');
  readonly especialidades = signal<Especialidad[]>([]);
  readonly dialogoVisible = signal(false);
  readonly especialidadEditando = signal<Especialidad | null>(null);

  readonly formulario = this.constructorFormulario.nonNullable.group({
    nombre: ['', Validators.required],
    descripcion: [''],
    activo: [true],
  });

  ngOnInit(): void {
    this.GetEspecialidades();
  }

  GetEspecialidades(): void {
    this.api.GetEspecialidades().subscribe({ next: (lista) => this.especialidades.set(lista) });
  }

  AbrirNueva(): void {
    this.especialidadEditando.set(null);
    this.formulario.reset({ nombre: '', descripcion: '', activo: true });
    this.dialogoVisible.set(true);
  }

  AbrirEditar(especialidad: Especialidad): void {
    this.especialidadEditando.set(especialidad);
    this.formulario.patchValue(especialidad);
    this.dialogoVisible.set(true);
  }

  GuardarEspecialidad(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }
    const datos = this.formulario.getRawValue();
    const especialidad = this.especialidadEditando();
    const operacion = especialidad
      ? this.api.PutEspecialidad(especialidad.id, datos)
      : this.api.PostEspecialidad(datos);
    operacion.subscribe({
      next: () => {
        this.dialogoVisible.set(false);
        this.mensajeria.add({
          severity: 'success',
          summary: 'Operación Exitosa',
          detail: 'Especialidad guardada.',
        });
        this.GetEspecialidades();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo) }),
    });
  }

  EliminarEspecialidad(especialidad: Especialidad): void {
    if (!confirm(`¿Eliminar ${especialidad.nombre}?`)) {
      this.mensajeria.add({
        severity: 'info',
        summary: 'No se realizaron cambios',
        detail: 'Eliminación cancelada.',
      });
      return;
    }
    this.api.DeleteEspecialidad(especialidad.id).subscribe({
      next: () => {
        this.mensajeria.add({
          severity: 'success',
          summary: 'Operación Exitosa',
          detail: 'Especialidad eliminada.',
        });
        this.GetEspecialidades();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({
          severity: 'error',
          summary: 'Error',
          detail: DetalleErrorComun(fallo, 'eliminar'),
        }),
    });
  }
}
