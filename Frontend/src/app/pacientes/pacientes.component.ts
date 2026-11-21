import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, HostListener, OnInit, ViewChild, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { MessageService } from 'primeng/api';
import { Table, TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ToastModule } from 'primeng/toast';

import { Paciente } from '../modelo';
import { ApiService, DetalleError as DetalleErrorComun } from '../service/api.service';
import { SharedService } from '../service/shared.service';

@Component({
  selector: 'app-pacientes',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    TableModule,
    TagModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './pacientes.component.html',
})
export class PacientesComponent implements OnInit {
  @ViewChild('tabla') private tabla?: Table;

  private readonly api = inject(ApiService);
  private readonly mensajeria = inject(MessageService);
  private readonly compartido = inject(SharedService);
  private readonly constructorFormulario = inject(FormBuilder);

  readonly pacientes = signal<Paciente[]>([]);
  readonly busqueda = signal('');
  readonly ultimaActualizacion = signal<Date | null>(null);
  readonly dialogoVisible = signal(false);
  readonly pacienteEditando = signal<Paciente | null>(null);
  private foto: File | null = null;

  readonly pacientesFiltrados = computed(() => {
    const texto = this.Normalizar(this.busqueda());
    if (!texto) {
      return this.pacientes();
    }
    return this.pacientes().filter((paciente) =>
      this.Normalizar(
        [
          paciente.codigo_historia,
          paciente.nombres,
          paciente.apellidos,
          paciente.dni,
          paciente.telefono,
          paciente.direccion,
          paciente.correo,
          paciente.fecha_nacimiento,
        ]
          .filter(Boolean)
          .join(' '),
      ).includes(texto),
    );
  });

  readonly formulario = this.constructorFormulario.nonNullable.group({
    codigo_historia: ['', Validators.required],
    nombres: ['', Validators.required],
    apellidos: ['', Validators.required],
    dni: ['', Validators.required],
    fecha_nacimiento: [''],
    sexo: [''],
    telefono: [''],
    direccion: [''],
    correo: [''],
  });

  ngOnInit(): void {
    this.busqueda.set(this.compartido.ObtenerBusqueda());
    this.GetPacientes();
    this.compartido.busqueda.subscribe((texto) => this.busqueda.set(texto));
  }

  GetPacientes(notificar = false): void {
    this.api.GetPacientes().subscribe({
      next: (lista) => {
        this.pacientes.set([...lista].sort((a, b) => b.id - a.id));
        this.ultimaActualizacion.set(new Date());
        if (notificar) {
          this.mensajeria.add({
            severity: 'success',
            summary: 'Lista actualizada',
            detail: `${lista.length} paciente(s) registrado(s).`,
            life: 2000,
          });
        }
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({
          severity: 'error',
          summary: 'Error',
          detail: this.DetalleError(fallo, 'cargar los pacientes'),
        }),
    });
  }

  Actualizar(): void {
    this.GetPacientes(true);
  }

  @HostListener('window:focus')
  AlEnfocar(): void {
    this.GetPacientes();
  }

  AbrirNuevo(): void {
    this.pacienteEditando.set(null);
    this.formulario.reset();
    this.foto = null;
    this.dialogoVisible.set(true);
  }

  AbrirEditar(paciente: Paciente): void {
    this.pacienteEditando.set(paciente);
    this.formulario.patchValue({
      codigo_historia: paciente.codigo_historia,
      nombres: paciente.nombres,
      apellidos: paciente.apellidos,
      dni: paciente.dni,
      fecha_nacimiento: paciente.fecha_nacimiento ?? '',
      sexo: paciente.sexo,
      telefono: paciente.telefono,
      direccion: paciente.direccion,
      correo: paciente.correo,
    });
    this.foto = null;
    this.dialogoVisible.set(true);
  }

  SeleccionarFoto(evento: Event): void {
    const archivo = (evento.target as HTMLInputElement).files?.item(0);
    this.foto = archivo ?? null;
  }

  Normalizar(texto: string | null | undefined): string {
    return (texto ?? '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim()
      .toLowerCase();
  }

  DetalleError(fallo: HttpErrorResponse, accion = 'guardar el paciente'): string {
    return DetalleErrorComun(fallo, accion);
  }

  GuardarPaciente(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }
    const datos = new FormData();
    Object.entries(this.formulario.getRawValue()).forEach(([clave, valor]) => {
      if (clave === 'fecha_nacimiento' && !valor) {
        return;
      }
      datos.append(clave, valor ?? '');
    });
    if (this.foto) {
      datos.append('foto', this.foto);
    }
    const paciente = this.pacienteEditando();
    const operacion = paciente
      ? this.api.PutPaciente(paciente.codigo_historia, datos)
      : this.api.PostPaciente(datos);
    operacion.subscribe({
      next: (guardado: Paciente) => {
        this.dialogoVisible.set(false);
        this.compartido.CambiarBusqueda('');
        this.busqueda.set('');
        this.pacientes.update((lista) => [
          guardado,
          ...lista.filter((item) => item.codigo_historia !== guardado.codigo_historia),
        ]);
        this.tabla?.reset();
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: 'Paciente guardado.' });
        this.GetPacientes();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({
          severity: 'error',
          summary: 'Error',
          detail: this.DetalleError(fallo),
        }),
    });
  }

  EliminarPaciente(paciente: Paciente): void {
    if (!confirm(`¿Eliminar la historia de ${paciente.nombres} ${paciente.apellidos}?`)) {
      this.mensajeria.add({ severity: 'info', summary: 'No se realizaron cambios', detail: 'Eliminación cancelada.' });
      return;
    }
    this.api.DeletePaciente(paciente.codigo_historia).subscribe({
      next: () => {
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: 'Paciente eliminado.' });
        this.GetPacientes();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({
          severity: 'error',
          summary: 'Error',
          detail: this.DetalleError(fallo, 'eliminar el paciente'),
        }),
    });
  }
}
