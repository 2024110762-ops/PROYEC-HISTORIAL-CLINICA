import { HttpInterceptorFn } from '@angular/common/http';

import { environment } from '../../environments/environment';

export const authInterceptor: HttpInterceptorFn = (solicitud, siguiente) => {
  const token = sessionStorage.getItem('hce_token');
  if (token && solicitud.url.startsWith(environment.apiUrl)) {
    return siguiente(
      solicitud.clone({
        setHeaders: { Authorization: `Token ${token}` },
      }),
    );
  }
  return siguiente(solicitud);
};
