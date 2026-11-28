import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import QRCode from 'qrcode';

import { Perfil } from '../modelo';
import { UrlArchivo } from '../service/api.service';
import { AuthService } from '../service/auth.service';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [ButtonModule],
  templateUrl: './perfil.component.html',
  styles: [
    `
      .hce-contenedor {
        max-width: 1150px;
        margin: 0 auto;
      }
      .hce-tarjeta {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
      }
      .hce-carnet-layout {
        display: grid;
        grid-template-columns: minmax(0, 1.7fr) minmax(0, 0.85fr);
        align-items: start;
        gap: 34px;
      }
      .hce-carnet-columna {
        display: flex;
        width: 100%;
        flex-direction: column;
        gap: 16px;
        min-width: 0;
      }
      .hce-carnet-marco,
      .hce-qr-marco {
        position: relative;
        width: 100%;
        min-width: 0;
      }
      .hce-carnet-marco::after,
      .hce-qr-marco::after {
        content: '';
        position: absolute;
        inset: 10px -12px -12px 10px;
        z-index: 0;
        background: linear-gradient(135deg, rgba(8, 125, 182, 0.2), rgba(15, 23, 42, 0.14));
        border-radius: 14px;
      }
      .hce-carnet {
        position: relative;
        z-index: 1;
        min-height: 367px;
        background: #fff;
        border: 1px solid #d8e3ec;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 14px 16px 32px rgba(15, 23, 42, 0.24);
      }
      .hce-qr {
        position: relative;
        z-index: 1;
        display: flex;
        width: 100%;
        max-width: none;
        height: 367px;
        flex-direction: column;
        padding: 0;
        background: #fff;
        border: 1px solid #d8e3ec;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 14px 16px 32px rgba(15, 23, 42, 0.24);
      }
      .hce-qr-encabezado {
        display: flex;
        align-items: center;
        gap: 12px;
        height: 56px;
        padding: 0 16px;
        background: linear-gradient(120deg, #087db6, #45b4e4);
        color: #fff;
      }
      .hce-qr-logo {
        display: grid;
        place-items: center;
        width: 36px;
        height: 36px;
        border: 2px solid rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 800;
        letter-spacing: 0.06em;
      }
      .hce-qr-encabezado h2 {
        margin: 0;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
      }
      .hce-qr-encabezado span {
        font-size: 0.7rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        opacity: 0.85;
      }
      .hce-qr-cuerpo {
        display: flex;
        flex: 1;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 8px 16px;
      }
      .hce-qr-cuerpo img {
        width: 175px;
        height: 205px;
        object-fit: contain;
      }
      .hce-qr-cuerpo p {
        margin: 0;
        color: #1684b5;
        font-size: 0.75rem;
        font-weight: 700;
        text-align: center;
      }
      .hce-qr-cargando {
        display: grid;
        place-items: center;
        width: 175px;
        height: 205px;
        color: #64748b;
        font-size: 0.75rem;
      }
      .hce-acciones {
        align-self: flex-end;
        padding-right: 12px;
      }
      .hce-carnet-encabezado {
        display: flex;
        align-items: center;
        gap: 24px;
        height: 104px;
        padding: 0 32px;
        background: linear-gradient(120deg, #087db6, #45b4e4);
        color: #fff;
      }
      .hce-carnet-logo {
        display: grid;
        place-items: center;
        width: 56px;
        height: 56px;
        border: 2px solid rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 800;
        letter-spacing: 0.06em;
      }
      .hce-carnet-encabezado h2 {
        margin: 0;
        font-size: 1.9rem;
        letter-spacing: 0.05em;
      }
      .hce-carnet-encabezado span {
        font-size: 0.82rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        opacity: 0.85;
      }
      .hce-carnet-cuerpo {
        display: flex;
        align-items: center;
        gap: 34px;
        padding: 28px 40px;
      }
      .hce-avatar {
        width: 175px;
        height: 205px;
        border-radius: 8px;
        overflow: hidden;
        background: #1688bd;
        color: #fff;
        display: grid;
        place-items: center;
        font-size: 3.5rem;
        font-weight: 700;
        flex-shrink: 0;
        border: 3px solid #fff;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.22);
      }
      .hce-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center top;
      }
      .hce-identidad {
        flex: 1;
        min-width: 0;
      }
      .hce-identidad h1 {
        margin: 0;
        color: #111827;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.01em;
      }
      .hce-identidad p {
        margin: 0.35rem 0 1.25rem;
        color: #1684b5;
        font-size: 1.1rem;
        font-weight: 700;
      }
      .hce-carnet-datos {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.75rem 1.25rem;
      }
      .hce-carnet-datos div {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
        min-width: 0;
      }
      .hce-carnet-datos strong {
        color: #1684b5;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .hce-carnet-datos span {
        color: #334155;
        font-size: 0.95rem;
        font-weight: 600;
        overflow-wrap: anywhere;
      }
      .hce-foto-input {
        display: none;
      }
      @media (max-width: 1100px) {
        .hce-carnet-layout {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 640px) {
        .hce-carnet-encabezado {
          padding: 0 18px;
        }
        .hce-carnet-encabezado h2 {
          font-size: 1.35rem;
        }
        .hce-carnet-cuerpo {
          flex-direction: column;
        }
        .hce-avatar {
          width: 100%;
          height: 205px;
        }
      }
    `,
  ],
})
export class PerfilComponent implements OnInit {
  private readonly autenticacion = inject(AuthService);

  readonly perfil = this.autenticacion.getPerfil();
  readonly codigoQR = signal('');
  readonly subiendoFoto = signal(false);

  readonly esMedico = computed(() => this.perfil()?.rol === 'MEDICO');
  readonly urlImagen = computed(() => UrlArchivo(this.perfil()?.imagen));
  readonly iniciales = computed(() => {
    const datos = this.perfil();
    if (!datos) {
      return '?';
    }
    return (
      `${datos.nombres?.[0] ?? datos.nombre?.[0] ?? ''}${datos.apellidos?.[0] ?? ''}`.toUpperCase() || '?'
    );
  });

  ngOnInit(): void {
    const datos = this.perfil();
    if (datos) {
      this.GenerarQR(datos);
      return;
    }
    this.autenticacion.CargarPerfil().subscribe(() => {
      const cargado = this.perfil();
      if (cargado) {
        this.GenerarQR(cargado);
      }
    });
  }

  EtiquetaRol(rol: string): string {
    const etiquetas: Record<string, string> = {
      ADMIN: 'Administrador',
      MEDICO: 'Médico',
      PACIENTE: 'Paciente',
      ADMINISTRATIVO: 'Administrativo',
      LABORATORIO: 'Laboratorio',
      IMAGEN: 'Imágenes',
      RECEPCION: 'Recepción',
      ENFERMERIA: 'Enfermería',
    };
    return etiquetas[rol] ?? rol;
  }

  CambiarFoto(evento: Event): void {
    const entrada = evento.target as HTMLInputElement;
    const archivo = entrada.files?.item(0);
    if (!archivo) {
      return;
    }
    const datos = new FormData();
    datos.append('imagen', archivo);
    this.subiendoFoto.set(true);
    this.autenticacion.ActualizarPerfil(datos).subscribe({
      next: () => this.subiendoFoto.set(false),
      error: () => this.subiendoFoto.set(false),
    });
    entrada.value = '';
  }

  GenerarQR(datos: Perfil): void {
    const valor = ['HCE', 'CARNET', datos.rol, datos.codigo || datos.username || '', datos.cmp || '']
      .filter(Boolean)
      .join('|');
    QRCode.toDataURL(valor, { width: 360, margin: 1 })
      .then((url) => this.codigoQR.set(url))
      .catch(() => this.codigoQR.set(''));
  }
}
