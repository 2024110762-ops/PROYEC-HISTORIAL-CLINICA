import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ToastModule } from 'primeng/toast';

import { AuditoriaAcceso } from '../modelo';
import { ApiService, DetalleError as DetalleErrorComun } from '../service/api.service';

@Component({
  selector: 'app-auditoria',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonModule, InputTextModule, TableModule, TagModule, ToastModule],
  providers: [MessageService],
  templateUrl: './auditoria.component.html',
})
export class AuditoriaComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly mensajeria = inject(MessageService);

  readonly registros = signal<AuditoriaAcceso[]>([]);
  readonly filtros = signal({ paciente: '', usuario: '', accion: '', desde: '', hasta: '' });

  ngOnInit(): void {
    this.GetAuditorias();
  }

  GetAuditorias(): void {
    this.api.GetAuditorias(this.filtros()).subscribe({
      next: (lista) => this.registros.set(lista),
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo, 'cargar la auditoría') }),
    });
  }

  ExportarCSV(): void {
    this.api.GetExportarAuditoria(this.filtros()).subscribe({
      next: (archivo) => {
        const enlace = document.createElement('a');
        enlace.href = URL.createObjectURL(archivo);
        enlace.download = 'auditoria-hce.csv';
        enlace.click();
        URL.revokeObjectURL(enlace.href);
        this.mensajeria.add({
          severity: 'success',
          summary: 'Operación Exitosa',
          detail: 'Exportación realizada y auditada.',
        });
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo, 'exportar la auditoría') }),
    });
  }
}
