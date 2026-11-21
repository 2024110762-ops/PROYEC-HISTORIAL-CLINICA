import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';

import { ApiService } from '../service/api.service';
import { AuthService } from '../service/auth.service';
import { MENU_BASE } from '../service/menu';
import { SharedService } from '../service/shared.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ButtonModule, InputTextModule, MessageModule],
  templateUrl: './layout.component.html',
  styles: [
    `
      .hce-layout {
        display: grid;
        grid-template-columns: 260px 1fr;
        min-height: 100vh;
      }
      .hce-sidebar {
        background: #0f172a;
        color: #e2e8f0;
        padding: 1.25rem 0.75rem;
      }
      .hce-sidebar h2 {
        font-size: 1rem;
        padding: 0 0.75rem 1rem;
        margin: 0;
        color: #5eead4;
      }
      .hce-sidebar nav a {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.65rem 0.75rem;
        margin-bottom: 0.2rem;
        border-radius: 8px;
        color: #cbd5e1;
        text-decoration: none;
      }
      .hce-sidebar nav a:hover,
      .hce-sidebar nav a.router-link-active {
        background: #134e4a;
        color: #fff;
      }
      .hce-principal {
        display: flex;
        flex-direction: column;
        min-width: 0;
      }
      .hce-topbar {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.85rem 1.5rem;
        background: #fff;
        border-bottom: 1px solid #e2e8f0;
      }
      .hce-topbar input {
        max-width: 380px;
      }
      .hce-topbar .hce-espaciador {
        flex: 1;
      }
      .hce-contenido {
        padding: 1.5rem;
        overflow: auto;
      }
      @media (max-width: 800px) {
        .hce-layout {
          grid-template-columns: 1fr;
        }
        .hce-sidebar nav {
          display: flex;
          flex-wrap: wrap;
        }
      }
    `,
  ],
})
export class LayoutComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly autenticacion = inject(AuthService);
  private readonly compartido = inject(SharedService);
  private readonly enrutador = inject(Router);
  private readonly ruta = inject(ActivatedRoute);

  readonly menus = this.api.menus;
  readonly perfil = this.autenticacion.getPerfil();
  readonly mensaje = signal(this.ruta.snapshot.queryParamMap.get('error') ?? '');
  readonly busquedaGlobal = signal(this.compartido.ObtenerBusqueda());

  ngOnInit(): void {
    this.compartido.busqueda.subscribe((texto) => this.busquedaGlobal.set(texto));
    if (!this.perfil()) {
      this.autenticacion.CargarPerfil().subscribe({ next: () => undefined, error: () => undefined });
    }
    this.api.GetMenus().subscribe({
      next: (lista) => {
        if (!lista.length) {
          this.api.menus.set(MENU_BASE);
        }
      },
      error: () => this.api.menus.set(MENU_BASE),
    });
  }

  Buscar(evento: Event): void {
    const texto = (evento.target as HTMLInputElement).value;
    this.busquedaGlobal.set(texto);
    this.compartido.CambiarBusqueda(texto);
  }

  CerrarSesion(): void {
    this.autenticacion.CerrarSesion();
    this.enrutador.navigate(['/login']);
  }
}
