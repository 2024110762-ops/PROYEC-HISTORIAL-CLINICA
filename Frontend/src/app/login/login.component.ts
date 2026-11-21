import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';

import { AuthService } from '../service/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ButtonModule, InputTextModule, MessageModule],
  templateUrl: './login.component.html',
  styles: [
    `
      .hce-ingreso {
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, #0f766e 0%, #134e4a 100%);
      }
      .hce-tarjeta-ingreso {
        width: min(420px, 92vw);
        background: #fff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
      }
      .hce-ingreso h1 {
        color: #0f766e;
        letter-spacing: 0.12em;
      }
    `,
  ],
})
export class LoginComponent implements OnInit {
  private readonly constructorFormulario = inject(FormBuilder);
  private readonly autenticacion = inject(AuthService);
  private readonly enrutador = inject(Router);
  private readonly ruta = inject(ActivatedRoute);

  readonly cargando = signal(false);
  readonly mensajeError = signal('');

  readonly formulario = this.constructorFormulario.nonNullable.group({
    usuario: ['', Validators.required],
    contraseña: ['', Validators.required],
  });

  ngOnInit(): void {
    if (this.autenticacion.EstaAutenticado()) {
      this.enrutador.navigate(['/sistema']);
    }
  }

  Ingresar(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }
    this.cargando.set(true);
    this.mensajeError.set('');
    const { usuario, contraseña } = this.formulario.getRawValue();
    this.autenticacion.IniciarSesion(usuario, contraseña).subscribe({
      next: () => {
        this.cargando.set(false);
        const destino = this.ruta.snapshot.queryParamMap.get('returnUrl') || '/sistema';
        this.enrutador.navigateByUrl(destino);
      },
      error: () => {
        this.cargando.set(false);
        this.mensajeError.set('Credenciales inválidas. Intente nuevamente.');
      },
    });
  }
}
