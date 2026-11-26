import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ToastModule } from 'primeng/toast';

import { Paciente, ResultadoLaboratorio } from '../modelo';
import {
  ApiService,
  DetalleError as DetalleErrorComun,
  UrlArchivo as UrlArchivoComun,
} from '../service/api.service';
import { AuthService } from '../service/auth.service';

@Component({
  selector: 'app-resultados-laboratorio',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    SelectModule,
    TableModule,
    TagModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './resultados-laboratorio.component.html',
})
export class ResultadosLaboratorioComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly autenticacion = inject(AuthService);
  private readonly mensajeria = inject(MessageService);
  private readonly constructorFormulario = inject(FormBuilder);

  readonly resultados = signal<ResultadoLaboratorio[]>([]);
  readonly pacientes = signal<Paciente[]>([]);
  readonly filtroTexto = signal('');
  readonly filtroEstado = signal('');
  readonly visorVisible = signal(false);
  readonly resultadoSeleccionado = signal<ResultadoLaboratorio | null>(null);
  readonly sincronizando = signal(false);
  readonly formularioVisible = signal(false);

  readonly puedeSincronizar = this.autenticacion.tieneRol('ADMIN', 'LABORATORIO');
  readonly puedeCrear = this.autenticacion.tieneRol('ADMIN', 'LABORATORIO');

  readonly formulario = this.constructorFormulario.nonNullable.group({
    paciente: ['', Validators.required],
    tipo_prueba: ['', Validators.required],
    laboratorio: [''],
    fecha_toma: [''],
    fecha_resultado: [''],
    estado: ['DISPONIBLE'],
    valores: [''],
    unidad: [''],
    interpretacion: [''],
    codigo_externo: [''],
  });
  readonly urlArchivo = computed(() => {
    const archivo = this.resultadoSeleccionado()?.archivo;
    return UrlArchivoComun(archivo);
  });

  readonly resultadosFiltrados = computed(() => {
    const texto = this.filtroTexto().trim().toLowerCase();
    const estado = this.filtroEstado();
    return this.resultados().filter((resultado) => {
      const coincideTexto = !texto || `${resultado.tipo_prueba} ${resultado.laboratorio}`.toLowerCase().includes(texto);
      const coincideEstado = !estado || resultado.estado === estado;
      return coincideTexto && coincideEstado;
    });
  });

  ngOnInit(): void {
    this.GetResultadosLaboratorio();
    if (this.puedeCrear) {
      this.api.GetPacientes().subscribe({
        next: (lista) => this.pacientes.set(lista),
        error: (fallo: HttpErrorResponse) =>
          this.mensajeria.add({
            severity: 'error',
            summary: 'Error',
            detail: DetalleErrorComun(fallo, 'cargar los pacientes'),
          }),
      });
    }
  }

  GetResultadosLaboratorio(): void {
    this.api.GetResultadosLaboratorio().subscribe({
      next: (lista) => this.resultados.set(lista),
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({
          severity: 'error',
          summary: 'Error',
          detail: DetalleErrorComun(fallo, 'cargar los resultados'),
        }),
    });
  }

  AbrirNuevo(): void {
    this.formulario.reset({ estado: 'DISPONIBLE' });
    this.formularioVisible.set(true);
  }

  GuardarResultado(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }
    const datos = new FormData();
    Object.entries(this.formulario.getRawValue()).forEach(([clave, valor]) => {
      if (valor) {
        datos.append(clave, String(valor));
      }
    });
    this.api.PostResultadoLaboratorio(datos).subscribe({
      next: () => {
        this.formularioVisible.set(false);
        this.mensajeria.add({
          severity: 'success',
          summary: 'Operación Exitosa',
          detail: 'Resultado registrado.',
        });
        this.GetResultadosLaboratorio();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({
          severity: 'error',
          summary: 'No se pudo registrar el resultado',
          detail: DetalleErrorComun(fallo, 'registrar el resultado'),
        }),
    });
  }

  Ver(resultado: ResultadoLaboratorio): void {
    this.resultadoSeleccionado.set(resultado);
    this.visorVisible.set(true);
  }

  Sincronizar(): void {
    this.sincronizando.set(true);
    this.api.PostSincronizarLaboratorio().subscribe({
      next: (respuesta) => {
        this.sincronizando.set(false);
        this.mensajeria.add({
          severity: 'success',
          summary: 'Operación Exitosa',
          detail: `${respuesta.total} resultados sincronizados.`,
        });
        this.GetResultadosLaboratorio();
      },
      error: (fallo: HttpErrorResponse) => {
        this.sincronizando.set(false);
        this.mensajeria.add({
          severity: 'error',
          summary: 'Error',
          detail: DetalleErrorComun(fallo, 'sincronizar los resultados'),
        });
      },
    });
  }
}
