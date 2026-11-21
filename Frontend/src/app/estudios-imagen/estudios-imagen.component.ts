import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { TagModule } from 'primeng/tag';
import { ToastModule } from 'primeng/toast';

import { environment } from '../../environments/environment';
import { EstudioImagen } from '../modelo';
import { ApiService, DetalleError as DetalleErrorComun } from '../service/api.service';
import { AuthService } from '../service/auth.service';

@Component({
  selector: 'app-estudios-imagen',
  standalone: true,
  imports: [CommonModule, ButtonModule, DialogModule, TagModule, ToastModule],
  providers: [MessageService],
  templateUrl: './estudios-imagen.component.html',
})
export class EstudiosImagenComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly autenticacion = inject(AuthService);
  private readonly mensajeria = inject(MessageService);

  readonly apiUrl = environment.apiUrl;
  readonly estudios = signal<EstudioImagen[]>([]);
  readonly estudioSeleccionado = signal<EstudioImagen | null>(null);
  readonly visorVisible = signal(false);
  readonly sincronizando = signal(false);

  readonly puedeSincronizar = this.autenticacion.tieneRol('ADMIN', 'IMAGEN');
  readonly urlImagen = computed(() => {
    const imagen = this.estudioSeleccionado()?.imagen;
    return imagen ? `${environment.apiUrl}/${imagen}` : '';
  });
  readonly urlArchivo = computed(() => {
    const archivo = this.estudioSeleccionado()?.archivo;
    return archivo ? `${environment.apiUrl}/${archivo}` : '';
  });

  ngOnInit(): void {
    this.GetEstudiosImagen();
  }

  GetEstudiosImagen(): void {
    this.api.GetEstudiosImagen().subscribe({
      next: (lista) => this.estudios.set(lista),
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo, 'cargar los estudios') }),
    });
  }

  Ver(estudio: EstudioImagen): void {
    this.estudioSeleccionado.set(estudio);
    this.visorVisible.set(true);
  }

  Sincronizar(): void {
    this.sincronizando.set(true);
    this.api.PostSincronizarImagenes().subscribe({
      next: (respuesta) => {
        this.sincronizando.set(false);
        this.mensajeria.add({
          severity: 'success',
          summary: 'Operación Exitosa',
          detail: `${respuesta.total} estudios sincronizados.`,
        });
        this.GetEstudiosImagen();
      },
      error: (fallo: HttpErrorResponse) => {
        this.sincronizando.set(false);
        this.mensajeria.add({
          severity: 'error',
          summary: 'Error',
          detail: DetalleErrorComun(fallo, 'sincronizar los estudios'),
        });
      },
    });
  }
}
