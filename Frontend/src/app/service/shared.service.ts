import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SharedService {
  private readonly busquedaInterna = new BehaviorSubject<string>('');
  readonly busqueda: Observable<string> = this.busquedaInterna.asObservable();

  CambiarBusqueda(texto: string): void {
    this.busquedaInterna.next(texto);
  }

  ObtenerBusqueda(): string {
    return this.busquedaInterna.value;
  }
}
