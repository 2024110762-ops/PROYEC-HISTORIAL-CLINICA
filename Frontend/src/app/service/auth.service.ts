import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, switchMap, tap } from 'rxjs';

import { environment } from '../../environments/environment';
import { Perfil, RespuestaLogin } from '../modelo';

const CLAVE_TOKEN = 'hce_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly token = signal<string | null>(sessionStorage.getItem(CLAVE_TOKEN));
  private readonly perfil = signal<Perfil | null>(null);

  IniciarSesion(usuario: string, contraseña: string): Observable<Perfil> {
    return this.http
      .post<RespuestaLogin>(`${environment.apiUrl}/api/login/`, {
        username: usuario,
        password: contraseña,
      })
      .pipe(
        tap((respuesta) => {
          sessionStorage.setItem(CLAVE_TOKEN, respuesta.token);
          this.token.set(respuesta.token);
        }),
        switchMap(() => this.CargarPerfil()),
      );
  }

  CargarPerfil(): Observable<Perfil> {
    return this.http
      .get<Perfil>(`${environment.apiUrl}/api/perfil/`)
      .pipe(tap((perfil) => this.perfil.set(perfil)));
  }

  getPerfil() {
    return this.perfil.asReadonly();
  }

  getToken(): string | null {
    return this.token();
  }

  EstaAutenticado(): boolean {
    return !!this.token();
  }

  tieneRol(...roles: string[]): boolean {
    const rol = this.perfil()?.rol;
    return !!rol && roles.includes(rol);
  }

  esDeEspecialidad(especialidad: string): boolean {
    return (this.perfil()?.especialidad ?? '') === especialidad;
  }

  CerrarSesion(): void {
    this.http.post(`${environment.apiUrl}/api/logout/`, {}).subscribe({
      next: () => undefined,
      error: () => undefined,
    });
    sessionStorage.removeItem(CLAVE_TOKEN);
    this.token.set(null);
    this.perfil.set(null);
  }
}
