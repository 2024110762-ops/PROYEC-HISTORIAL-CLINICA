import { HttpErrorResponse } from '@angular/common/http';
import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { MessageService } from 'primeng/api';
import { EMPTY, Observable, of } from 'rxjs';
import { describe, expect, it, vi } from 'vitest';

import { appRoutes } from './app.routes';
import { Especialidad, Medico, Paciente, Perfil } from './modelo';
import { EspecialidadesComponent } from './especialidades/especialidades.component';
import { MedicosComponent } from './medicos/medicos.component';
import { PerfilComponent } from './perfil/perfil.component';
import { PacientesComponent } from './pacientes/pacientes.component';
import { ResultadosLaboratorioComponent } from './resultados-laboratorio/resultados-laboratorio.component';
import { ApiService, DetalleError, UrlArchivo } from './service/api.service';
import { AuthService } from './service/auth.service';
import { MENU_BASE } from './service/menu';
import { SharedService } from './service/shared.service';

describe('Configuración de la aplicación', () => {
  it('define la ruta de ingreso y el área del sistema', () => {
    const rutas = appRoutes.map((ruta) => ruta.path);
    expect(rutas).toContain('login');
    expect(rutas).toContain('sistema');

    const sistema = appRoutes.find((ruta) => ruta.path === 'sistema');
    const raiz = sistema?.children?.find((ruta) => ruta.path === '');
    expect(raiz?.redirectTo).toBe('pacientes');

    const menu = sistema?.children?.find((ruta) => ruta.path === 'menu');
    expect(menu?.data?.['roles']).toEqual(['ADMIN']);

    const perfil = sistema?.children?.find((ruta) => ruta.path === 'perfil');
    expect(perfil?.title).toBe('Mi perfil · HCE');
    expect(MENU_BASE[0].texto).toBe('Mi perfil');
    expect(MENU_BASE[1].texto).toBe('Pacientes');
  });

  it('protege el módulo de auditoría por rol', () => {
    const sistema = appRoutes.find((ruta) => ruta.path === 'sistema');
    const auditoria = sistema?.children?.find((ruta) => ruta.path === 'auditoria');
    expect(auditoria?.canActivate?.length).toBeGreaterThan(0);
    expect(auditoria?.data?.['roles']).toEqual(['ADMIN']);
  });
});

describe('Pantalla de pacientes', () => {
  const paciente: Paciente = {
    id: 1,
    codigo_historia: 'HC-001',
    nombres: 'María',
    apellidos: 'Quispe',
    dni: '70100001',
    fecha_nacimiento: '1985-04-12',
    sexo: 'F',
    telefono: '987111001',
    direccion: 'Av. Demo 1',
    correo: 'maria@demo.test',
    foto: null,
    cuenta: null,
  };

  function configurar(
    getPacientes: () => Observable<Paciente[]>,
    postPaciente: () => Observable<Paciente> = () => of(paciente),
  ) {
    TestBed.configureTestingModule({
      imports: [PacientesComponent],
      providers: [
        { provide: ApiService, useValue: { GetPacientes: getPacientes, PostPaciente: postPaciente } },
        { provide: MessageService, useValue: { add: vi.fn() } },
      ],
    });
    return TestBed.createComponent(PacientesComponent);
  }

  it('renderiza las filas de los pacientes en la tabla', () => {
    const fixture = configurar(() => of([paciente]));
    fixture.componentInstance.ngOnInit();
    fixture.detectChanges();

    const filas = fixture.nativeElement.querySelectorAll('tbody tr');
    expect(filas.length).toBeGreaterThan(0);
    expect(filas[0].textContent).toContain(paciente.codigo_historia);
  });

  it('filtra sin acentos y por teléfono o correo', () => {
    const fixture = configurar(() => of([paciente]));
    const componente = fixture.componentInstance;
    componente.ngOnInit();

    componente.busqueda.set('maria');
    expect(componente.pacientesFiltrados()).toEqual([paciente]);

    componente.busqueda.set('987111');
    expect(componente.pacientesFiltrados()).toEqual([paciente]);

    componente.busqueda.set('DEMO.TEST');
    expect(componente.pacientesFiltrados()).toEqual([paciente]);
  });

  it('recarga la lista y limpia el buscador al guardar', () => {
    const nuevo: Paciente = { ...paciente, id: 2, codigo_historia: 'HC-002', nombres: 'Nuevo' };
    const listar = vi
      .fn()
      .mockReturnValueOnce(of([paciente]))
      .mockReturnValueOnce(of([paciente, nuevo]));
    const crear = vi.fn(() => of(nuevo));
    const fixture = configurar(listar, crear);
    const componente = fixture.componentInstance;
    const compartido = TestBed.inject(SharedService);
    compartido.CambiarBusqueda('maria');
    componente.ngOnInit();

    componente.formulario.patchValue({
      codigo_historia: 'HC-002',
      nombres: 'Nuevo',
      apellidos: 'Paciente',
      dni: '70100002',
    });
    componente.GuardarPaciente();

    expect(crear).toHaveBeenCalledOnce();
    expect(listar).toHaveBeenCalledTimes(2);
    expect(componente.pacientes().map((item) => item.codigo_historia)).toEqual(['HC-002', 'HC-001']);
    expect(componente.busqueda()).toBe('');
    expect(compartido.ObtenerBusqueda()).toBe('');
  });

  it('confirma visualmente al presionar Actualizar', () => {
    const listar = vi.fn(() => of([paciente]));
    const add = vi.fn();
    TestBed.overrideComponent(PacientesComponent, {
      set: { providers: [{ provide: MessageService, useValue: { add } }] },
    });
    const fixture = configurar(listar);
    const componente = fixture.componentInstance;
    componente.ngOnInit();

    componente.Actualizar();

    expect(listar).toHaveBeenCalledTimes(2);
    expect(add).toHaveBeenCalledWith(expect.objectContaining({ summary: 'Lista actualizada' }));
    expect(componente.ultimaActualizacion()).toBeInstanceOf(Date);
  });

  it('paginates the patients five at a time', () => {
    const ocho = Array.from({ length: 8 }, (_, indice) => ({
      ...paciente,
      id: indice + 1,
      codigo_historia: `HC-00${indice + 1}`,
    }));
    const fixture = configurar(() => of(ocho));
    fixture.componentInstance.ngOnInit();
    fixture.detectChanges();

    const filas = fixture.nativeElement.querySelectorAll('tbody tr');
    const paginas = fixture.nativeElement.querySelectorAll('.p-paginator-page');
    expect(filas.length).toBe(5);
    expect([...paginas].map((pagina) => pagina.textContent?.trim())).toContain('2');
  });

  it('recarga la lista al volver a la pestaña', () => {
    const listar = vi.fn(() => of([paciente]));
    const fixture = configurar(listar);
    const componente = fixture.componentInstance;
    componente.ngOnInit();

    componente.AlEnfocar();

    expect(listar).toHaveBeenCalledTimes(2);
  });

  it('muestra el paciente recién agregado aunque falle la recarga', () => {
    const nuevo: Paciente = { ...paciente, id: 2, codigo_historia: 'HC-002', nombres: 'Nuevo' };
    const listar = vi
      .fn()
      .mockReturnValueOnce(of([paciente]))
      .mockReturnValueOnce(EMPTY);
    const fixture = configurar(listar, () => of(nuevo));
    const componente = fixture.componentInstance;
    componente.ngOnInit();

    componente.formulario.patchValue({
      codigo_historia: 'HC-002',
      nombres: 'Nuevo',
      apellidos: 'Paciente',
      dni: '70100002',
    });
    componente.GuardarPaciente();

    expect(componente.pacientesFiltrados().map((item) => item.codigo_historia)).toEqual(['HC-002', 'HC-001']);
  });
});

describe('Detalle de errores', () => {
  it('muestra el detail devuelto por el backend', () => {
    const fallo = new HttpErrorResponse({
      status: 400,
      error: { detail: 'La receta no tiene medicamentos.' },
    });
    expect(DetalleError(fallo)).toBe('La receta no tiene medicamentos.');
  });

  it('muestra los errores por campo y el texto de conexión', () => {
    const porCampo = new HttpErrorResponse({
      status: 400,
      error: { paciente: ['Este campo es obligatorio.'] },
    });
    expect(DetalleError(porCampo)).toContain('paciente: Este campo es obligatorio.');

    const sinConexion = new HttpErrorResponse({ status: 0 });
    expect(DetalleError(sinConexion)).toContain('No se pudo conectar');
  });
});

describe('URL de archivos', () => {
  it('agrega /media/ a una ruta relativa', () => {
    expect(UrlArchivo('laboratorio/analisis.pdf')).toBe(
      'http://127.0.0.1:8000/media/laboratorio/analisis.pdf',
    );
  });

  it('respeta la URL absoluta devuelta por el backend', () => {
    expect(UrlArchivo('http://127.0.0.1:8000/media/laboratorio/analisis.pdf')).toBe(
      'http://127.0.0.1:8000/media/laboratorio/analisis.pdf',
    );
  });
});

describe('Resultados de laboratorio', () => {
  const paciente: Paciente = {
    id: 1,
    codigo_historia: 'HC-001',
    nombres: 'María',
    apellidos: 'Quispe',
    dni: '70100001',
    fecha_nacimiento: null,
    sexo: '',
    telefono: '',
    direccion: '',
    correo: '',
    foto: null,
    cuenta: null,
  };

  it('registra un resultado desde el formulario y recarga la tabla', () => {
    const crear = vi.fn(() => of({ id: 1 }));
    const listar = vi.fn(() => of([]));
    const add = vi.fn();
    TestBed.overrideComponent(ResultadosLaboratorioComponent, {
      set: { providers: [{ provide: MessageService, useValue: { add } }] },
    });
    TestBed.configureTestingModule({
      imports: [ResultadosLaboratorioComponent],
      providers: [
        {
          provide: ApiService,
          useValue: {
            GetResultadosLaboratorio: listar,
            GetPacientes: () => of([paciente]),
            PostResultadoLaboratorio: crear,
          },
        },
        { provide: AuthService, useValue: { tieneRol: () => true } },
      ],
    });
    const fixture = TestBed.createComponent(ResultadosLaboratorioComponent);
    const componente = fixture.componentInstance;
    componente.ngOnInit();

    componente.formulario.patchValue({ paciente: String(paciente.id), tipo_prueba: 'Hemograma' });
    componente.GuardarResultado();

    expect(crear).toHaveBeenCalledOnce();
    expect(componente.formularioVisible()).toBe(false);
    expect(listar).toHaveBeenCalledTimes(2);
  });
});

describe('Pantalla de médicos', () => {
  const medico: Medico = {
    id: 1,
    codigo_medico: 'MED-001',
    nombres: 'Ana',
    apellidos: 'Ruiz',
    especialidad: 1,
    cmp: 'CMP-001',
    imagen: null,
    cuenta: null,
  };

  it('oculta las acciones de gestión para el rol médico', () => {
    TestBed.configureTestingModule({
      imports: [MedicosComponent],
      providers: [
        {
          provide: ApiService,
          useValue: {
            GetMedicos: () => of([medico]),
            GetEspecialidades: () => of([]),
          },
        },
        { provide: AuthService, useValue: { tieneRol: () => false } },
      ],
    });
    const fixture = TestBed.createComponent(MedicosComponent);
    fixture.componentInstance.ngOnInit();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).not.toContain('Nuevo médico');
    expect(fixture.nativeElement.querySelector('[aria-label="Editar"]')).toBeNull();
    expect(fixture.nativeElement.querySelector('[aria-label="Eliminar"]')).toBeNull();
  });

  it('envía usuario y contraseña al crear un médico', () => {
    const crear = vi.fn((_datos: FormData) => of(medico));
    TestBed.configureTestingModule({
      imports: [MedicosComponent],
      providers: [
        {
          provide: ApiService,
          useValue: {
            GetMedicos: () => of([]),
            GetEspecialidades: () => of([{ id: 1, nombre: 'Cardiología', descripcion: '', activo: true }]),
            PostMedico: crear,
          },
        },
        { provide: AuthService, useValue: { tieneRol: () => true } },
      ],
    });
    const fixture = TestBed.createComponent(MedicosComponent);
    const componente = fixture.componentInstance;
    componente.ngOnInit();
    componente.AbrirNuevo();
    componente.formulario.patchValue({
      codigo_medico: 'MED-002',
      nombres: 'Luis',
      apellidos: 'Pérez',
      especialidad: 1,
      cmp: 'CMP-002',
      username: 'medico_nuevo',
      password: 'ClaveSegura123!',
    });

    componente.GuardarMedico();

    expect(crear).toHaveBeenCalledOnce();
    const datos = crear.mock.calls[0][0] as FormData;
    expect(datos.get('username')).toBe('medico_nuevo');
    expect(datos.get('password')).toBe('ClaveSegura123!');
  });
});

describe('Pantalla de especialidades', () => {
  const especialidad: Especialidad = {
    id: 1,
    nombre: 'Cardiología',
    descripcion: 'Especialidad cardiovascular',
    activo: true,
  };

  it('oculta las acciones de gestión para el rol médico', () => {
    TestBed.configureTestingModule({
      imports: [EspecialidadesComponent],
      providers: [
        { provide: ApiService, useValue: { GetEspecialidades: () => of([especialidad]) } },
        { provide: AuthService, useValue: { tieneRol: () => false } },
      ],
    });
    const fixture = TestBed.createComponent(EspecialidadesComponent);
    fixture.componentInstance.ngOnInit();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).not.toContain('Nueva especialidad');
    expect(fixture.nativeElement.querySelector('[aria-label="Editar"]')).toBeNull();
    expect(fixture.nativeElement.querySelector('[aria-label="Eliminar"]')).toBeNull();
  });
});

describe('Pantalla de perfil', () => {
  const perfilMedico: Perfil = {
    id: 1,
    rol: 'MEDICO',
    username: 'medico_cardio',
    nombre: 'Ana Ruiz',
    nombres: 'Ana',
    apellidos: 'Ruiz',
    correo: 'ana@hce.test',
    imagen: '',
    especialidad: 'Cardiología',
    sede: '',
    codigo: 'MED-001',
    telefono: '',
    direccion: '',
    fecha_nacimiento: null,
    sexo: '',
    cmp: 'CMP-001',
    estado: true,
    permisos: ['Emitir recetas electrónicas', 'Editar mi perfil'],
  };

  const perfilAdmin: Perfil = {
    ...perfilMedico,
    rol: 'ADMIN',
    username: 'admin',
    nombre: 'Root Admin',
    nombres: 'Root',
    apellidos: 'Admin',
    especialidad: '',
    cmp: '',
    permisos: ['Consultar auditoría', 'Editar mi perfil'],
  };

  function configurar(datos: Perfil, actualizar: (valores: FormData) => Observable<Perfil>) {
    TestBed.configureTestingModule({
      imports: [PerfilComponent],
      providers: [
        {
          provide: AuthService,
          useValue: { getPerfil: () => signal(datos), ActualizarPerfil: actualizar },
        },
        MessageService,
      ],
    });
    return TestBed.createComponent(PerfilComponent);
  }

  it('muestra el carnet del médico y permite cambiar la foto', () => {
    const actualizar = vi.fn((_datos: FormData) => of(perfilMedico));
    const fixture = configurar(perfilMedico, actualizar);
    fixture.componentInstance.ngOnInit();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.hce-carnet')).not.toBeNull();
    expect(fixture.nativeElement.querySelector('.hce-identidad h1').textContent).toBe('Ana Ruiz');
    expect(fixture.nativeElement.querySelector('.hce-identidad p').textContent).toBe('Cardiología');
    expect(fixture.nativeElement.textContent).toContain('CMP-001');
    expect(fixture.nativeElement.textContent).toContain('Cambiar foto de perfil');
    expect(fixture.nativeElement.querySelector('.hce-carnet .hce-acciones')).toBeNull();
    expect(fixture.nativeElement.querySelector('.hce-carnet-columna > .hce-acciones')).not.toBeNull();
    expect(fixture.nativeElement.querySelector('.hce-qr')).not.toBeNull();
    expect(fixture.nativeElement.textContent).not.toContain('Datos personales');
    expect(fixture.nativeElement.textContent).not.toContain('Guardar cambios');
    expect(fixture.nativeElement.textContent).not.toContain('Permisos según mi rol');
    expect(fixture.nativeElement.querySelector('.hce-carnet-qr')).toBeNull();

    const archivo = new File(['x'], 'foto.png', { type: 'image/png' });
    fixture.componentInstance.CambiarFoto({
      target: { files: { item: () => archivo }, value: '' },
    } as unknown as Event);

    expect(actualizar).toHaveBeenCalledOnce();
    expect(actualizar.mock.calls[0][0].get('imagen')).toBe(archivo);
  });

  it('muestra los permisos de administrador', () => {
    const fixture = configurar(perfilAdmin, (_datos: FormData) => of(perfilAdmin));
    fixture.componentInstance.ngOnInit();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.hce-identidad h1').textContent).toBe('Root Admin');
    expect(fixture.nativeElement.querySelector('.hce-identidad p').textContent).toBe('Administrador');
    expect(fixture.nativeElement.textContent).toContain('Activo');
  });

  it('renderiza el perfil aunque el backend devuelva el formato anterior', () => {
    const anterior = {
      rol: 'MEDICO',
      nombre: 'Ana Ruiz',
      especialidad: 'Cardiología',
    } as Perfil;
    const fixture = configurar(anterior, (_datos: FormData) => of(anterior));
    fixture.componentInstance.ngOnInit();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.hce-identidad h1').textContent).toBe('Ana Ruiz');
    expect(fixture.nativeElement.querySelector('.hce-identidad p').textContent).toBe('Cardiología');
    expect(fixture.nativeElement.querySelector('.hce-carnet')).not.toBeNull();
  });
});
