import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ToastModule } from 'primeng/toast';

import { Consulta, Especialidad, Medico, Paciente, Sede } from '../modelo';
import { ApiService, DetalleError as DetalleErrorComun } from '../service/api.service';
import { AuthService } from '../service/auth.service';

@Component({
  selector: 'app-consultas',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ButtonModule,
    DatePickerModule,
    DialogModule,
    InputTextModule,
    SelectModule,
    TableModule,
    TagModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './consultas.component.html',
})
export class ConsultasComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly autenticacion = inject(AuthService);
  private readonly mensajeria = inject(MessageService);
  private readonly constructorFormulario = inject(FormBuilder);

  readonly consultas = signal<Consulta[]>([]);
  readonly pacientes = signal<Paciente[]>([]);
  readonly medicos = signal<Medico[]>([]);
  readonly especialidades = signal<Especialidad[]>([]);
  readonly sedes = signal<Sede[]>([]);
  readonly dialogoVisible = signal(false);
  readonly consultaEditando = signal<Consulta | null>(null);

  readonly formulario = this.constructorFormulario.nonNullable.group({
    paciente: [0, Validators.required],
    medico: [0, Validators.required],
    especialidad: [0, Validators.required],
    sede: [0, Validators.required],
    fecha_hora: [new Date(), Validators.required],
    motivo: [''],
    diagnostico: [''],
  });

  ngOnInit(): void {
    this.GetConsultas();
    this.api.GetPacientes().subscribe({ next: (lista) => this.pacientes.set(lista) });
    this.api.GetMedicos().subscribe({ next: (lista) => this.medicos.set(lista) });
    this.api.GetEspecialidades().subscribe({ next: (lista) => this.especialidades.set(lista) });
    this.api.GetSedes().subscribe({ next: (lista) => this.sedes.set(lista) });
  }

  GetConsultas(): void {
    this.api.GetConsultas().subscribe({ next: (lista) => this.consultas.set(lista) });
  }

  NombrePaciente(id: number): string {
    const paciente = this.pacientes().find((elemento) => elemento.id === id);
    return paciente ? `${paciente.nombres} ${paciente.apellidos}` : `Paciente ${id}`;
  }

  NombreMedico(id: number): string {
    const medico = this.medicos().find((elemento) => elemento.id === id);
    return medico ? `${medico.nombres} ${medico.apellidos}` : `Médico ${id}`;
  }

  NombreEspecialidad(id: number): string {
    return this.especialidades().find((elemento) => elemento.id === id)?.nombre ?? `Especialidad ${id}`;
  }

  PuedeFinalizar(consulta: Consulta): boolean {
    const habilitado =
      this.autenticacion.tieneRol('ADMIN') ||
      this.autenticacion.esDeEspecialidad(this.NombreEspecialidad(consulta.especialidad));
    return habilitado && consulta.estado !== 'FINALIZADA' && consulta.estado !== 'CANCELADA';
  }

  AbrirNueva(): void {
    this.consultaEditando.set(null);
    this.formulario.reset({
      paciente: this.pacientes()[0]?.id ?? 0,
      medico: this.medicos()[0]?.id ?? 0,
      especialidad: this.especialidades()[0]?.id ?? 0,
      sede: this.sedes()[0]?.id ?? 0,
      fecha_hora: new Date(),
      motivo: '',
      diagnostico: '',
    });
    this.dialogoVisible.set(true);
  }

  AbrirEditar(consulta: Consulta): void {
    this.consultaEditando.set(consulta);
    this.formulario.patchValue({
      paciente: consulta.paciente,
      medico: consulta.medico,
      especialidad: consulta.especialidad,
      sede: consulta.sede,
      fecha_hora: new Date(consulta.fecha_hora),
      motivo: consulta.motivo,
      diagnostico: consulta.diagnostico,
    });
    this.dialogoVisible.set(true);
  }

  GuardarConsulta(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }
    const valores = this.formulario.getRawValue();
    const datos: Partial<Consulta> = {
      ...valores,
      fecha_hora: new Date(valores.fecha_hora).toISOString(),
    };
    const consulta = this.consultaEditando();
    const operacion = consulta
      ? this.api.PutConsulta(consulta.id, datos)
      : this.api.PostConsulta(datos);
    operacion.subscribe({
      next: () => {
        this.dialogoVisible.set(false);
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: 'Consulta guardada.' });
        this.GetConsultas();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo) }),
    });
  }

  Finalizar(consulta: Consulta): void {
    this.api.PostFinalizarConsulta(consulta.id).subscribe({
      next: (respuesta) =>
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: respuesta.mensaje }),
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo, 'finalizar la consulta') }),
    });
  }

  EliminarConsulta(consulta: Consulta): void {
    if (!confirm('¿Eliminar la consulta programada?')) {
      this.mensajeria.add({ severity: 'info', summary: 'No se realizaron cambios', detail: 'Eliminación cancelada.' });
      return;
    }
    this.api.DeleteConsulta(consulta.id).subscribe({
      next: () => {
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: 'Consulta eliminada.' });
        this.GetConsultas();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo, 'eliminar') }),
    });
  }
}
