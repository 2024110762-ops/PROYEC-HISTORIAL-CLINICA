import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { DetalleError } from '../service/api.service';
import { AuthService } from '../service/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent implements OnInit {
  private readonly constructorFormulario = inject(FormBuilder);
  private readonly autenticacion = inject(AuthService);
  private readonly enrutador = inject(Router);
  private readonly ruta = inject(ActivatedRoute);

  readonly cargando = signal(false);
  readonly mensajeError = signal('');
  readonly verClave = signal(false);

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
      error: (fallo: HttpErrorResponse) => {
        this.cargando.set(false);
        this.mensajeError.set(
          fallo.status === 401
            ? 'Credenciales inválidas. Intente nuevamente.'
            : DetalleError(fallo, 'ingresar'),
        );
      },
    });
  }

  alternarClave(): void {
    this.verClave.update((visible) => !visible);
  }
}
