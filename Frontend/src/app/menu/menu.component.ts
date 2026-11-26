import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { TableModule } from 'primeng/table';
import { ToastModule } from 'primeng/toast';

import { Menu } from '../modelo';
import { ApiService, DetalleError as DetalleErrorComun } from '../service/api.service';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    MessageModule,
    TableModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './menu.component.html',
})
export class MenuComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly mensajeria = inject(MessageService);
  private readonly constructorFormulario = inject(FormBuilder);

  readonly menus = signal<Menu[]>([]);
  readonly dialogoVisible = signal(false);
  readonly menuEditando = signal<Menu | null>(null);
  readonly errorValidacion = signal('');

  readonly formulario = this.constructorFormulario.nonNullable.group({
    texto: ['', Validators.required],
    icono: ['pi pi-circle'],
    ruta: ['/sistema/', Validators.required],
    orden: [0, [Validators.required, Validators.min(0)]],
  });

  ngOnInit(): void {
    this.GetMenus();
  }

  GetMenus(): void {
    this.api.GetMenus().subscribe({ next: (lista) => this.menus.set(lista) });
  }

  AbrirNuevo(): void {
    this.menuEditando.set(null);
    this.errorValidacion.set('');
    this.formulario.reset({ texto: '', icono: 'pi pi-circle', ruta: '/sistema/', orden: 0 });
    this.dialogoVisible.set(true);
  }

  AbrirEditar(menu: Menu): void {
    this.menuEditando.set(menu);
    this.errorValidacion.set('');
    this.formulario.patchValue(menu);
    this.dialogoVisible.set(true);
  }

  GuardarMenu(): void {
    const datos = this.formulario.getRawValue();
    if (!datos.ruta.startsWith('/sistema/') || datos.orden < 0) {
      this.errorValidacion.set('La ruta debe iniciar con /sistema/ y el orden debe ser mayor o igual a 0.');
      return;
    }
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }
    this.errorValidacion.set('');
    const menu = this.menuEditando();
    const operacion = menu ? this.api.PutMenu(menu.id, datos) : this.api.PostMenu(datos);
    operacion.subscribe({
      next: () => {
        this.dialogoVisible.set(false);
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: 'Menú guardado.' });
        this.GetMenus();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo) }),
    });
  }

  EliminarMenu(menu: Menu): void {
    if (!confirm(`¿Eliminar la opción "${menu.texto}"?`)) {
      this.mensajeria.add({ severity: 'info', summary: 'No se realizaron cambios', detail: 'Eliminación cancelada.' });
      return;
    }
    this.api.DeleteMenu(menu.id).subscribe({
      next: () => {
        this.mensajeria.add({ severity: 'success', summary: 'Operación Exitosa', detail: 'Menú eliminado.' });
        this.GetMenus();
      },
      error: (fallo: HttpErrorResponse) =>
        this.mensajeria.add({ severity: 'error', summary: 'Error', detail: DetalleErrorComun(fallo, 'eliminar') }),
    });
  }
}
