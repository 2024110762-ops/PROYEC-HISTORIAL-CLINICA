import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = (_ruta, estado) => {
  const autenticacion = inject(AuthService);
  const enrutador = inject(Router);
  const redirigir = () =>
    enrutador.createUrlTree(['/login'], { queryParams: { returnUrl: estado.url } });

  if (!autenticacion.EstaAutenticado()) {
    return redirigir();
  }
  if (autenticacion.getPerfil()()) {
    return true;
  }
  return autenticacion.CargarPerfil().pipe(
    map(() => true),
    catchError(() => {
      autenticacion.CerrarSesion();
      return of(redirigir());
    }),
  );
};
