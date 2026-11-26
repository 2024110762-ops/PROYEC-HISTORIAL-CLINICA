import { Routes } from '@angular/router';

import { authGuard } from './service/auth.guard';
import { roleGuard } from './service/role.guard';

export const appRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: '/login' },
  {
    path: 'login',
    title: 'Ingreso · HCE',
    loadComponent: () => import('./login/login.component').then((modulo) => modulo.LoginComponent),
  },
  {
    path: 'sistema',
    loadComponent: () => import('./layout/layout.component').then((modulo) => modulo.LayoutComponent),
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'pacientes' },
      {
        path: 'pacientes',
        title: 'Pacientes · HCE',
        loadComponent: () =>
          import('./pacientes/pacientes.component').then((modulo) => modulo.PacientesComponent),
      },
      {
        path: 'consultas',
        title: 'Consultas · HCE',
        loadComponent: () =>
          import('./consultas/consultas.component').then((modulo) => modulo.ConsultasComponent),
      },
      {
        path: 'recetas',
        title: 'Recetas · HCE',
        canActivate: [roleGuard],
        data: { roles: ['ADMIN', 'MEDICO', 'PACIENTE', 'ADMINISTRATIVO'] },
        loadComponent: () => import('./recetas/recetas.component').then((modulo) => modulo.RecetasComponent),
      },
      {
        path: 'resultados-laboratorio',
        title: 'Resultados de laboratorio · HCE',
        canActivate: [roleGuard],
        data: { roles: ['ADMIN', 'MEDICO', 'LABORATORIO', 'IMAGEN', 'PACIENTE', 'ADMINISTRATIVO'] },
        loadComponent: () =>
          import('./resultados-laboratorio/resultados-laboratorio.component').then(
            (modulo) => modulo.ResultadosLaboratorioComponent,
          ),
      },
      {
        path: 'estudios-imagen',
        title: 'Estudios de imagen · HCE',
        canActivate: [roleGuard],
        data: { roles: ['ADMIN', 'MEDICO', 'LABORATORIO', 'IMAGEN', 'PACIENTE', 'ADMINISTRATIVO'] },
        loadComponent: () =>
          import('./estudios-imagen/estudios-imagen.component').then(
            (modulo) => modulo.EstudiosImagenComponent,
          ),
      },
      {
        path: 'auditoria',
        title: 'Auditoría · HCE',
        canActivate: [roleGuard],
        data: { roles: ['ADMIN'] },
        loadComponent: () => import('./auditoria/auditoria.component').then((modulo) => modulo.AuditoriaComponent),
      },
      {
        path: 'medicos',
        title: 'Médicos · HCE',
        loadComponent: () => import('./medicos/medicos.component').then((modulo) => modulo.MedicosComponent),
      },
      {
        path: 'especialidades',
        title: 'Especialidades · HCE',
        loadComponent: () =>
          import('./especialidades/especialidades.component').then(
            (modulo) => modulo.EspecialidadesComponent,
          ),
      },
      {
        path: 'administradores',
        title: 'Administradores · HCE',
        canActivate: [roleGuard],
        data: { roles: ['ADMIN'] },
        loadComponent: () =>
          import('./administradores/administradores.component').then(
            (modulo) => modulo.AdministradoresComponent,
          ),
      },
      {
        path: 'menu',
        title: 'Menús · HCE',
        canActivate: [roleGuard],
        data: { roles: ['ADMIN'] },
        loadComponent: () => import('./menu/menu.component').then((modulo) => modulo.MenuComponent),
      },
    ],
  },
  { path: '**', redirectTo: '/login' },
];
