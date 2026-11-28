import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { ToastModule } from 'primeng/toast';

import { Especialidad, Medico } from '../modelo';
import { ApiService, DetalleError as DetalleErrorComun } from '../service/api.service';
import { AuthService } from '../service/auth.service';

@Component({
  selector: 'app-medicos',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    SelectModule,
    TableModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './medicos.component.html',
})
export class MedicosComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly autenticacion = inject(AuthService);
  private readonly mensajeria = inject(MessageService);
  private readonly constructorFormulario = inject(FormBuilder);

  readonly puedeGestionar = this.autenticacion.tieneRol('ADMIN');
  readonly medicos = signal<Medico[]>([]);
  readonly especialidades = signal<Especialidad[]>([]);
  readonly dialogoVisible = signal(false);
  readonly medicoEditando = signal<Medico | null>(null);

  readonly formulario = this.constructorFormulario.nonNullable.group({
    codigo_medico: ['', Validators.required],
    nombres: ['', Validators.required],
    apellidos: ['', Validators.required],
    especialidad: [0, [Validators.required, Validators.min(1)]],
    cmp: ['', Validators.required],
    cuenta: [''],
    username: [''],
    password: [''],
  });

  ngOnInit(): void {
    this.GetMedicos();
    this.api.GetEspecialidades().subscribe({ next: (lista) => this.especialidades.set(lista) });
  }

  GetMedicos(): void {
    this.api.GetMedicos().subscribe({ next: (lista) => this.medicos.set(lista) });
  }

  NombreEspecialidad(id: number): string {
    return this.especialidades().find((elemento) => elemento.id === id)?.nombre ?? '—';
  }

  AbrirNuevo(): void {
    this.medicoEditando.set(null);
    this.formulario.reset({
      codigo_medico: '',
      nombres: '',
      apellidos: '',
      especialidad: this.especialidades()[0]?.id ?? 0,
      cmp: '',
      cuenta: '',
      username: '',
      password: '',
    });
    this.dialogoVisible.set(true);
  }

  AbrirEditar(medico: Medico): void {
    this.medicoEditando.set(medico);
    this.formulario.patchValue({
      codigo_medico: medico.codigo_medico,
      nombres: medico.nombres,
      apellidos: medico.apellidos,
      especialidad: medico.especialidad,
      cmp: medico.cmp,
      cuenta: medico.cuenta != null ? String(medico.cuenta) : '',
      username: '',
      password: '',
    });
    this.dialogoVisible.set(true);
  }

  GuardarMedico(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }
    const datos = new FormData();
    Object.entries(this.formulario.getRawValue()).forEach(([clave, valor]) => {
      if (clave === 'cuenta' || (valor !== '' && valor !== null && valor !== undefined)) {
        datos.append(clave, valor === '' ? '' : String(valor));
      }
    });
    const medico = this.medicoEditando();
    const operacion = medico ? this.api.PutMedico(medico.id, datos) : this.api.PostMedico(datos);
    operacion.subscribe({
      next: () => {
        this.dialogoVisible.set(false);
        this.mensajeria.add({
          severity: 'success',
          summary: 'Operación Exitosa',
          detail: 'Médico guardado.',
        });
        this.GetMedicos();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo) }),
    });
  }

  EliminarMedico(medico: Medico): void {
    if (!confirm(`¿Eliminar al médico ${medico.nombres}?`)) {
      this.mensajeria.add({
        severity: 'info',
        summary: 'No se realizaron cambios',
        detail: 'Eliminación cancelada.',
      });
      return;
    }
    this.api.DeleteMedico(medico.id).subscribe({
      next: () => {
        this.mensajeria.add({
          severity: 'success',
          summary: 'Operación Exitosa',
          detail: 'Médico eliminado.',
        });
        this.GetMedicos();
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
