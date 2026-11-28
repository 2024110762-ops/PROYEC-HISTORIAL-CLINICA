import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ToastModule } from 'primeng/toast';
import QRCode from 'qrcode';

import { Consulta, DetalleReceta, Medicamento, Medico, Paciente, RecetaElectronica } from '../modelo';
import { ApiService, DetalleError as DetalleErrorComun } from '../service/api.service';
import { AuthService } from '../service/auth.service';

interface DetalleBorrador {
  medicamento: number;
  dosis: string;
  frecuencia: string;
  duracion: string;
  cantidad: number;
}

@Component({
  selector: 'app-recetas',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    SelectModule,
    TableModule,
    TagModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './recetas.component.html',
})
export class RecetasComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly autenticacion = inject(AuthService);
  private readonly mensajeria = inject(MessageService);

  readonly recetas = signal<RecetaElectronica[]>([]);
  readonly medicamentos = signal<Medicamento[]>([]);
  readonly consultas = signal<Consulta[]>([]);
  readonly pacientes = signal<Paciente[]>([]);
  readonly medicos = signal<Medico[]>([]);
  readonly dialogoVisible = signal(false);
  readonly recetaSeleccionada = signal<RecetaElectronica | null>(null);
  readonly codigoQR = signal('');
  readonly detalles = signal<DetalleBorrador[]>([]);

  readonly cabecera = signal({
    consulta: 0,
    paciente: 0,
    medico: 0,
    diagnostico: '',
    indicaciones: '',
  });

  readonly esMedico = this.autenticacion.tieneRol('MEDICO');
  readonly puedeEmitir = this.autenticacion.tieneRol('MEDICO', 'ADMIN');
  readonly soloLectura = !this.puedeEmitir;

  ngOnInit(): void {
    this.GetRecetas();
    this.api.GetMedicamentos().subscribe({ next: (lista) => this.medicamentos.set(lista) });
    this.api.GetConsultas().subscribe({ next: (lista) => this.consultas.set(lista) });
    this.api.GetPacientes().subscribe({ next: (lista) => this.pacientes.set(lista) });
    this.api.GetMedicos().subscribe({
      next: (lista) => {
        this.medicos.set(lista);
        if (!this.esMedico && !this.cabecera().medico && lista.length) {
          this.cabecera.update((valor) => ({ ...valor, medico: lista[0].id }));
        }
      },
    });
  }

  GetRecetas(): void {
    this.api.GetRecetas().subscribe({ next: (lista) => this.recetas.set(lista) });
  }

  NombrePaciente(id: number): string {
    const paciente = this.pacientes().find((elemento) => elemento.id === id);
    return paciente ? `${paciente.nombres} ${paciente.apellidos}` : `Paciente ${id}`;
  }

  AbrirNueva(): void {
    this.recetaSeleccionada.set(null);
    this.cabecera.set({
      consulta: this.consultas()[0]?.id ?? 0,
      paciente: this.pacientes()[0]?.id ?? 0,
      medico: this.medicos()[0]?.id ?? 0,
      diagnostico: '',
      indicaciones: '',
    });
    this.detalles.set([]);
    this.codigoQR.set('');
    this.dialogoVisible.set(true);
  }

  VerReceta(receta: RecetaElectronica): void {
    this.recetaSeleccionada.set(receta);
    this.cabecera.set({
      consulta: receta.consulta,
      paciente: receta.paciente,
      medico: receta.medico,
      diagnostico: receta.diagnostico,
      indicaciones: receta.indicaciones,
    });
    this.detalles.set(receta.detalles ?? []);
    this.GenerarQR(receta.firma_digital);
    this.dialogoVisible.set(true);
  }

  GenerarQR(firma: string): void {
    if (!firma) {
      this.codigoQR.set('');
      return;
    }
    QRCode.toDataURL(firma, { width: 220, margin: 1 }).then((url) => this.codigoQR.set(url));
  }

  AgregarDetalle(): void {
    this.detalles.update((lista) => [
      ...lista,
      {
        medicamento: this.medicamentos()[0]?.id ?? 0,
        dosis: '',
        frecuencia: '',
        duracion: '',
        cantidad: 1,
      },
    ]);
  }

  QuitarDetalle(indice: number): void {
    this.detalles.update((lista) => lista.filter((_, posicion) => posicion !== indice));
  }

  GuardarReceta(): void {
    if (!this.puedeEmitir || this.recetaSeleccionada()) {
      return;
    }
    const cabecera = this.cabecera();
    if (!cabecera.consulta || !cabecera.paciente || (!this.esMedico && !cabecera.medico)) {
      this.mensajeria.add({
        severity: 'warn',
        summary: 'No se realizaron cambios',
        detail: 'Complete la cabecera.',
      });
      return;
    }
    const datos: Partial<RecetaElectronica> = {
      consulta: cabecera.consulta,
      paciente: cabecera.paciente,
      ...(this.esMedico ? {} : { medico: cabecera.medico }),
      diagnostico: cabecera.diagnostico,
      indicaciones: cabecera.indicaciones,
      detalles: this.detalles() as DetalleReceta[],
    };
    this.api.PostReceta(datos).subscribe({
      next: (receta) => {
        this.mensajeria.add({
          severity: 'success',
          summary: 'Operación Exitosa',
          detail: 'Receta emitida y firmada digitalmente.',
        });
        this.GetRecetas();
        this.VerReceta(receta);
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({
          severity: 'error',
          summary: 'No se pudo emitir la receta',
          detail: DetalleErrorComun(fallo, 'emitir la receta'),
        }),
    });
  }

  EliminarReceta(receta: RecetaElectronica): void {
    if (this.soloLectura || !confirm('¿Anular la receta seleccionada?')) {
      this.mensajeria.add({
        severity: 'info',
        summary: 'No se realizaron cambios',
        detail: 'Operación cancelada.',
      });
      return;
    }
    this.api.PostAnularReceta(receta.id).subscribe({
      next: () => {
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: 'Receta anulada.' });
        this.GetRecetas();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({
          severity: 'error',
          summary: 'Error',
          detail: DetalleErrorComun(fallo, 'anular la receta'),
        }),
    });
  }
}
