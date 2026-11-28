import { Menu } from '../modelo';

export const MENU_PERFIL: Menu = {
  id: 0,
  texto: 'Mi perfil',
  icono: 'pi pi-user-edit',
  ruta: '/sistema/perfil',
  orden: 0,
};

export const MENU_BASE: Menu[] = [
  MENU_PERFIL,
  { id: 1, texto: 'Pacientes', icono: 'pi pi-users', ruta: '/sistema/pacientes', orden: 1 },
  { id: 2, texto: 'Consultas', icono: 'pi pi-calendar', ruta: '/sistema/consultas', orden: 2 },
  { id: 3, texto: 'Recetas', icono: 'pi pi-file', ruta: '/sistema/recetas', orden: 3 },
  {
    id: 4,
    texto: 'Laboratorio',
    icono: 'pi pi-clipboard',
    ruta: '/sistema/resultados-laboratorio',
    orden: 4,
  },
  { id: 5, texto: 'Imágenes', icono: 'pi pi-image', ruta: '/sistema/estudios-imagen', orden: 5 },
  { id: 6, texto: 'Auditoría', icono: 'pi pi-shield', ruta: '/sistema/auditoria', orden: 6 },
  { id: 7, texto: 'Médicos', icono: 'pi pi-user', ruta: '/sistema/medicos', orden: 7 },
  { id: 8, texto: 'Especialidades', icono: 'pi pi-heart', ruta: '/sistema/especialidades', orden: 8 },
  { id: 9, texto: 'Administradores', icono: 'pi pi-cog', ruta: '/sistema/administradores', orden: 9 },
  { id: 10, texto: 'Menús', icono: 'pi pi-list', ruta: '/sistema/menu', orden: 10 },
];

export const ROLES_POR_RUTA: Record<string, string[]> = {
  '/sistema/perfil': [],
  '/sistema/pacientes': [],
  '/sistema/consultas': [],
  '/sistema/recetas': ['ADMIN', 'MEDICO', 'PACIENTE', 'ADMINISTRATIVO'],
  '/sistema/resultados-laboratorio': [
    'ADMIN',
    'MEDICO',
    'LABORATORIO',
    'IMAGEN',
    'PACIENTE',
    'ADMINISTRATIVO',
  ],
  '/sistema/estudios-imagen': ['ADMIN', 'MEDICO', 'LABORATORIO', 'IMAGEN', 'PACIENTE', 'ADMINISTRATIVO'],
  '/sistema/auditoria': ['ADMIN'],
  '/sistema/medicos': [],
  '/sistema/especialidades': [],
  '/sistema/administradores': ['ADMIN'],
  '/sistema/menu': ['ADMIN'],
};
