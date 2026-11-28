export interface Menu {
  id: number;
  texto: string;
  icono: string;
  ruta: string;
  orden: number;
}

export interface Perfil {
  id: number | null;
  rol: string;
  username: string;
  nombre: string;
  nombres: string;
  apellidos: string;
  correo: string;
  imagen: string;
  especialidad: string;
  sede: string;
  codigo: string;
  telefono: string;
  direccion: string;
  fecha_nacimiento: string | null;
  sexo: string;
  cmp: string;
  estado: boolean;
  permisos: string[];
}

export interface RespuestaLogin extends Perfil {
  token: string;
}

export interface Especialidad {
  id: number;
  nombre: string;
  descripcion: string;
  activo: boolean;
}

export interface Sede {
  id: number;
  nombre: string;
  direccion: string;
  telefono: string;
  activo: boolean;
}

export interface Paciente {
  id: number;
  codigo_historia: string;
  nombres: string;
  apellidos: string;
  dni: string;
  dni_hash?: string;
  fecha_nacimiento: string | null;
  sexo: string;
  telefono: string;
  direccion: string;
  correo: string;
  foto: string | null;
  cuenta: number | null;
}

export interface Medico {
  id: number;
  codigo_medico: string;
  nombres: string;
  apellidos: string;
  especialidad: number;
  especialidad_nombre?: string;
  cmp: string;
  imagen: string | null;
  cuenta: number | null;
}

export interface PersonalClinica {
  id: number;
  codigo_empleado: string;
  nombres: string;
  apellidos: string;
  rol: string;
  sede: number;
  cuenta: number | null;
}

export interface Consulta {
  id: number;
  paciente: number;
  medico: number;
  especialidad: number;
  fecha_hora: string;
  motivo: string;
  diagnostico: string;
  estado: string;
  sede: number;
}

export interface Medicamento {
  id: number;
  nombre: string;
  descripcion: string;
}

export interface DetalleReceta {
  id?: number;
  medicamento: number;
  dosis: string;
  frecuencia: string;
  duracion: string;
  cantidad: number;
}

export interface RecetaElectronica {
  id: number;
  consulta: number;
  paciente: number;
  medico: number;
  fecha_emision: string;
  diagnostico: string;
  indicaciones: string;
  estado: string;
  firma_digital: string;
  qr: string | null;
  detalles: DetalleReceta[];
}

export interface ResultadoLaboratorio {
  id: number;
  paciente: number;
  consulta: number | null;
  codigo_externo: string | null;
  laboratorio: string;
  tipo_prueba: string;
  fecha_toma: string | null;
  fecha_resultado: string | null;
  estado: string;
  valores: string;
  unidad: string;
  interpretacion: string;
  archivo: string | null;
  fuente: string;
}

export interface EstudioImagen {
  id: number;
  paciente: number;
  consulta: number | null;
  codigo_externo: string | null;
  modalidad: string;
  tipo_estudio: string;
  fecha_estudio: string | null;
  informe: string;
  imagen: string | null;
  archivo: string | null;
  fuente: string;
  proveedor: string;
}

export interface AuditoriaAcceso {
  id: number;
  usuario: number | null;
  paciente: number | null;
  accion: string;
  modulo: string;
  fecha_hora: string;
  ip: string;
  user_agent: string;
  resultado: string;
  detalles: string;
}

export interface Administrador {
  id: number;
  dni: string;
  nombre: string;
  apellidos: string;
  usuario: number;
  contraseña?: string;
  estado: boolean;
  imagen: string | null;
}

export interface RespuestaSincronizacion {
  mensaje: string;
  creados: number;
  actualizados: number;
  total: number;
}
