import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  Administrador,
  AuditoriaAcceso,
  Consulta,
  DetalleReceta,
  Especialidad,
  EstudioImagen,
  Medicamento,
  Medico,
  Menu,
  Paciente,
  RecetaElectronica,
  RespuestaSincronizacion,
  ResultadoLaboratorio,
  Sede,
} from '../modelo';

type Filtros = Record<string, string | number | boolean | null | undefined>;

export function DetalleError(fallo: HttpErrorResponse, accion = 'guardar'): string {
  if (fallo.status === 0) {
    return `No se pudo conectar con el backend en ${environment.apiUrl}.`;
  }
  const cuerpo = fallo.error;
  if (typeof cuerpo === 'string') {
    return cuerpo;
  }
  if (cuerpo?.detail) {
    return String(cuerpo.detail);
  }
  const partes = Object.entries(cuerpo ?? {}).map(
    ([campo, errores]) => `${campo}: ${Array.isArray(errores) ? errores.join(' ') : errores}`,
  );
  return partes.join(' | ') || `No se pudo ${accion}.`;
}

export function UrlArchivo(valor: string | null | undefined): string {
  if (!valor) {
    return '';
  }
  if (/^https?:\/\//i.test(valor) || valor.startsWith('/')) {
    return valor.startsWith('/media/') ? `${environment.apiUrl}${valor}` : valor;
  }
  return `${environment.apiUrl}/media/${valor.replace(/^\/+/, '')}`;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/api/`;
  readonly menus = signal<Menu[]>([]);

  private Get<T>(recurso: string, filtros?: Filtros): Observable<T> {
    let parametros = new HttpParams();
    if (filtros) {
      Object.entries(filtros).forEach(([clave, valor]) => {
        if (valor !== null && valor !== undefined && valor !== '') {
          parametros = parametros.set(clave, String(valor));
        }
      });
    }
    return this.http.get<T>(`${this.baseUrl}${recurso}`, { params: parametros });
  }

  private Post<T, C>(recurso: string, contenido: C): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${recurso}`, contenido);
  }

  private Put<T, C>(recurso: string, contenido: C): Observable<T> {
    return this.http.put<T>(`${this.baseUrl}${recurso}`, contenido);
  }

  private Delete<T>(recurso: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}${recurso}`);
  }

  GetPacientes(): Observable<Paciente[]> {
    return this.Get<Paciente[]>('pacientes/');
  }

  GetPaciente(codigo: string): Observable<Paciente> {
    return this.Get<Paciente>(`pacientes/${codigo}/`);
  }

  PostPaciente(datos: FormData | Partial<Paciente>): Observable<Paciente> {
    return this.Post<Paciente, FormData | Partial<Paciente>>('pacientes/', datos);
  }

  PutPaciente(codigo: string, datos: FormData | Partial<Paciente>): Observable<Paciente> {
    return this.Put<Paciente, FormData | Partial<Paciente>>(`pacientes/${codigo}/`, datos);
  }

  DeletePaciente(codigo: string): Observable<void> {
    return this.Delete<void>(`pacientes/${codigo}/`);
  }

  GetConsultas(): Observable<Consulta[]> {
    return this.Get<Consulta[]>('consultas/');
  }

  GetConsulta(id: number): Observable<Consulta> {
    return this.Get<Consulta>(`consultas/${id}/`);
  }

  PostConsulta(datos: Partial<Consulta>): Observable<Consulta> {
    return this.Post<Consulta, Partial<Consulta>>('consultas/', datos);
  }

  PutConsulta(id: number, datos: Partial<Consulta>): Observable<Consulta> {
    return this.Put<Consulta, Partial<Consulta>>(`consultas/${id}/`, datos);
  }

  DeleteConsulta(id: number): Observable<void> {
    return this.Delete<void>(`consultas/${id}/`);
  }

  PostFinalizarConsulta(id: number): Observable<{ mensaje: string }> {
    return this.Post<{ mensaje: string }, Record<string, never>>(`consultas/${id}/finalizar/`, {});
  }

  GetRecetas(): Observable<RecetaElectronica[]> {
    return this.Get<RecetaElectronica[]>('recetas/');
  }

  GetReceta(id: number): Observable<RecetaElectronica> {
    return this.Get<RecetaElectronica>(`recetas/${id}/`);
  }

  PostReceta(datos: Partial<RecetaElectronica>): Observable<RecetaElectronica> {
    return this.Post<RecetaElectronica, Partial<RecetaElectronica>>('recetas/', datos);
  }

  PutReceta(id: number, datos: Partial<RecetaElectronica>): Observable<RecetaElectronica> {
    return this.Put<RecetaElectronica, Partial<RecetaElectronica>>(`recetas/${id}/`, datos);
  }

  PostAnularReceta(id: number): Observable<{ mensaje: string }> {
    return this.Post<{ mensaje: string }, Record<string, never>>(`recetas/${id}/anular/`, {});
  }

  DeleteReceta(id: number): Observable<void> {
    return this.Delete<void>(`recetas/${id}/`);
  }

  GetDetallesReceta(): Observable<DetalleReceta[]> {
    return this.Get<DetalleReceta[]>('detalles-receta/');
  }

  PostDetalleReceta(datos: Partial<DetalleReceta>): Observable<DetalleReceta> {
    return this.Post<DetalleReceta, Partial<DetalleReceta>>('detalles-receta/', datos);
  }

  DeleteDetalleReceta(id: number): Observable<void> {
    return this.Delete<void>(`detalles-receta/${id}/`);
  }

  GetMedicamentos(): Observable<Medicamento[]> {
    return this.Get<Medicamento[]>('medicamentos/');
  }

  PostMedicamento(datos: Partial<Medicamento>): Observable<Medicamento> {
    return this.Post<Medicamento, Partial<Medicamento>>('medicamentos/', datos);
  }

  PutMedicamento(id: number, datos: Partial<Medicamento>): Observable<Medicamento> {
    return this.Put<Medicamento, Partial<Medicamento>>(`medicamentos/${id}/`, datos);
  }

  DeleteMedicamento(id: number): Observable<void> {
    return this.Delete<void>(`medicamentos/${id}/`);
  }

  GetResultadosLaboratorio(filtros?: Filtros): Observable<ResultadoLaboratorio[]> {
    return this.Get<ResultadoLaboratorio[]>('resultados-laboratorio/', filtros);
  }

  PostResultadoLaboratorio(datos: FormData | Partial<ResultadoLaboratorio>): Observable<ResultadoLaboratorio> {
    return this.Post<ResultadoLaboratorio, FormData | Partial<ResultadoLaboratorio>>(
      'resultados-laboratorio/',
      datos,
    );
  }

  PutResultadoLaboratorio(
    id: number,
    datos: FormData | Partial<ResultadoLaboratorio>,
  ): Observable<ResultadoLaboratorio> {
    return this.Put<ResultadoLaboratorio, FormData | Partial<ResultadoLaboratorio>>(
      `resultados-laboratorio/${id}/`,
      datos,
    );
  }

  DeleteResultadoLaboratorio(id: number): Observable<void> {
    return this.Delete<void>(`resultados-laboratorio/${id}/`);
  }

  PostSincronizarLaboratorio(): Observable<RespuestaSincronizacion> {
    return this.Post<RespuestaSincronizacion, Record<string, never>>('resultados-laboratorio/sincronizar/', {});
  }

  GetEstudiosImagen(filtros?: Filtros): Observable<EstudioImagen[]> {
    return this.Get<EstudioImagen[]>('estudios-imagen/', filtros);
  }

  PostEstudioImagen(datos: FormData | Partial<EstudioImagen>): Observable<EstudioImagen> {
    return this.Post<EstudioImagen, FormData | Partial<EstudioImagen>>('estudios-imagen/', datos);
  }

  PutEstudioImagen(id: number, datos: FormData | Partial<EstudioImagen>): Observable<EstudioImagen> {
    return this.Put<EstudioImagen, FormData | Partial<EstudioImagen>>(`estudios-imagen/${id}/`, datos);
  }

  DeleteEstudioImagen(id: number): Observable<void> {
    return this.Delete<void>(`estudios-imagen/${id}/`);
  }

  PostSincronizarImagenes(): Observable<RespuestaSincronizacion> {
    return this.Post<RespuestaSincronizacion, Record<string, never>>('estudios-imagen/sincronizar/', {});
  }

  GetAuditorias(filtros?: Filtros): Observable<AuditoriaAcceso[]> {
    return this.Get<AuditoriaAcceso[]>('auditorias/', filtros);
  }

  GetUsuariosAuditoria(): Observable<string[]> {
    return this.Get<string[]>('auditorias/usuarios/');
  }

  GetExportarAuditoria(filtros?: Filtros): Observable<Blob> {
    let parametros = new HttpParams();
    if (filtros) {
      Object.entries(filtros).forEach(([clave, valor]) => {
        if (valor !== null && valor !== undefined && valor !== '') {
          parametros = parametros.set(clave, String(valor));
        }
      });
    }
    return this.http.get(`${this.baseUrl}auditorias/exportar/`, {
      params: parametros,
      responseType: 'blob',
    });
  }

  GetMedicos(): Observable<Medico[]> {
    return this.Get<Medico[]>('medicos/');
  }

  PostMedico(datos: FormData | Partial<Medico>): Observable<Medico> {
    return this.Post<Medico, FormData | Partial<Medico>>('medicos/', datos);
  }

  PutMedico(id: number, datos: FormData | Partial<Medico>): Observable<Medico> {
    return this.Put<Medico, FormData | Partial<Medico>>(`medicos/${id}/`, datos);
  }

  DeleteMedico(id: number): Observable<void> {
    return this.Delete<void>(`medicos/${id}/`);
  }

  GetEspecialidades(): Observable<Especialidad[]> {
    return this.Get<Especialidad[]>('especialidades/');
  }

  PostEspecialidad(datos: Partial<Especialidad>): Observable<Especialidad> {
    return this.Post<Especialidad, Partial<Especialidad>>('especialidades/', datos);
  }

  PutEspecialidad(id: number, datos: Partial<Especialidad>): Observable<Especialidad> {
    return this.Put<Especialidad, Partial<Especialidad>>(`especialidades/${id}/`, datos);
  }

  DeleteEspecialidad(id: number): Observable<void> {
    return this.Delete<void>(`especialidades/${id}/`);
  }

  GetSedes(): Observable<Sede[]> {
    return this.Get<Sede[]>('sedes/');
  }

  GetAdministradores(): Observable<Administrador[]> {
    return this.Get<Administrador[]>('administradores/');
  }

  PostAdministrador(datos: FormData | Partial<Administrador>): Observable<Administrador> {
    return this.Post<Administrador, FormData | Partial<Administrador>>('administradores/', datos);
  }

  PutAdministrador(id: number, datos: FormData | Partial<Administrador>): Observable<Administrador> {
    return this.Put<Administrador, FormData | Partial<Administrador>>(`administradores/${id}/`, datos);
  }

  DeleteAdministrador(id: number): Observable<void> {
    return this.Delete<void>(`administradores/${id}/`);
  }

  GetMenus(): Observable<Menu[]> {
    return this.Get<Menu[]>('menu/').pipe(tap((lista) => this.menus.set(lista)));
  }

  PostMenu(datos: Partial<Menu>): Observable<Menu> {
    return this.Post<Menu, Partial<Menu>>('menu/', datos);
  }

  PutMenu(id: number, datos: Partial<Menu>): Observable<Menu> {
    return this.Put<Menu, Partial<Menu>>(`menu/${id}/`, datos);
  }

  DeleteMenu(id: number): Observable<void> {
    return this.Delete<void>(`menu/${id}/`);
  }
}
