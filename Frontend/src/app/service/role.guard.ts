import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from './auth.service';

export const roleGuard: CanActivateFn = (ruta) => {
  const roles = (ruta.data['roles'] as string[] | undefined) ?? [];
  const autenticacion = inject(AuthService);
  const enrutador = inject(Router);
  if (!roles.length || autenticacion.tieneRol(...roles)) {
    return true;
  }
  return enrutador.createUrlTree(['/sistema'], {
    queryParams: { error: 'No tienes permiso para acceder' },
  });
};
