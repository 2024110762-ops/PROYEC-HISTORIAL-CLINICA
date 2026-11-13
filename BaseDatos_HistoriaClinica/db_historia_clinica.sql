
USE db_historia_clinica;


-- 1. TABLA: USUARIOS

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    rol VARCHAR(30) NOT NULL,
    estado VARCHAR(20) DEFAULT 'ACTIVO'
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS pacientes (
    id_paciente INT AUTO_INCREMENT PRIMARY KEY,
    dni CHAR(8) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    sexo VARCHAR(20),
    telefono VARCHAR(20),
    direccion VARCHAR(200),
    correo VARCHAR(100)
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS especialidades (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS medicos (
    id_medico INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    id_especialidad INT NOT NULL,
    cmp VARCHAR(20) NOT NULL UNIQUE,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_especialidad)
        REFERENCES especialidades(id_especialidad)
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS consultas (
    id_consulta INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT NOT NULL,
    id_medico INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    motivo TEXT,
    diagnostico TEXT,
    estado VARCHAR(30) DEFAULT 'PROGRAMADA',

    FOREIGN KEY (id_paciente)
        REFERENCES pacientes(id_paciente),

    FOREIGN KEY (id_medico)
        REFERENCES medicos(id_medico)
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS medicamentos (
    id_medicamento INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS recetas (
    id_receta INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta INT NOT NULL,
    fecha_emision DATETIME DEFAULT CURRENT_TIMESTAMP,
    indicaciones TEXT,

    FOREIGN KEY (id_consulta)
        REFERENCES consultas(id_consulta)
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS detalle_receta (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_receta INT NOT NULL,
    id_medicamento INT NOT NULL,
    dosis VARCHAR(100),
    frecuencia VARCHAR(100),
    duracion VARCHAR(100),
    cantidad INT NOT NULL,

    FOREIGN KEY (id_receta)
        REFERENCES recetas(id_receta)
        ON DELETE CASCADE,

    FOREIGN KEY (id_medicamento)
        REFERENCES medicamentos(id_medicamento)
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS examenes_laboratorio (
    id_examen INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS ordenes_laboratorio (
    id_orden INT AUTO_INCREMENT PRIMARY KEY,
    id_consulta INT NOT NULL,
    fecha_orden DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(30) DEFAULT 'PENDIENTE',

    FOREIGN KEY (id_consulta)
        REFERENCES consultas(id_consulta)
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS resultados_laboratorio (
    id_resultado INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL,
    id_examen INT NOT NULL,
    resultado TEXT,
    unidad VARCHAR(50),
    fecha_resultado DATETIME,

    FOREIGN KEY (id_orden)
        REFERENCES ordenes_laboratorio(id_orden),

    FOREIGN KEY (id_examen)
        REFERENCES examenes_laboratorio(id_examen),

    UNIQUE (id_orden, id_examen)
) ENGINE=InnoDB;



SHOW TABLES;