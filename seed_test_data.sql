-- ============================================================
-- SCRIPT DE DATOS DE PRUEBA - NOTIFICACION DE VISITA
-- Ejecutar en PostgreSQL en la BD neplatic, esquema neplatic
-- ============================================================

-- 1. ROLES DE USUARIO
INSERT INTO neplatic.rol_usuario (id_rol, codigo, nombre, descripcion, activo) VALUES
(1, 'ADMIN', 'Administrador', 'Acceso total', true),
(2, 'SUPERVISOR', 'Supervisor', 'Supervision de campo', true),
(3, 'NORMAL', 'Notificador', 'Notificador de campo', true)
ON CONFLICT (id_rol) DO NOTHING;

-- 2. ESTADOS DE NOTIFICACION
INSERT INTO neplatic.estado_notificacion (id_estado_notif, codigo, nombre, color_hex, descripcion) VALUES
(1, 'NOTIFICADO', 'Notificado', '#16a34a', 'Contribuyente notificado exitosamente'),
(2, 'AUSENTE', 'Ausente', '#f59e0b', 'No se encontro a nadie en el domicilio'),
(3, 'DIR_ERRADA', 'Direccion errada', '#dc2626', 'La direccion no corresponde'),
(4, 'RECHAZADO', 'Rechazado', '#7c3aed', 'El contribuyente rechazo la notificacion'),
(5, 'FALLECIDO', 'Contribuyente fallecido', '#6b7280', 'El contribuyente ha fallecido')
ON CONFLICT (id_estado_notif) DO NOTHING;

-- 3. TIPO DE TRIBUTO
INSERT INTO neplatic.tipo_tributo (id_tipo_tributo, codigo, nombre, descripcion, activo) VALUES
(1, 'PREDIAL', 'Impuesto Predial', 'Impuesto anual sobre predios', true),
(2, 'ARBITRIOS', 'Arbitrios Municipales', 'Limpieza, serenazgo, parques', true)
ON CONFLICT (id_tipo_tributo) DO NOTHING;

-- 4. ESTADO DE COBRANZA
INSERT INTO neplatic.estado_cobranza (id_estado, codigo, nombre, color_hex, prioridad, descripcion, activo) VALUES
(1, 'SIN_PROCESO', 'Sin proceso', '#3b82f6', 1, 'Deuda no gestionada', true),
(2, 'ORDINARIA', 'Ordinaria', '#7c2d12', 2, 'Cobranza ordinaria', true),
(3, 'COACTIVA', 'Coactiva', '#dc2626', 3, 'Cobranza coactiva', true)
ON CONFLICT (id_estado) DO NOTHING;

-- 5. TIPO DE DOCUMENTO
INSERT INTO neplatic.tipo_documento (id_tipo_doc, codigo, nombre, activo) VALUES
(1, 'D', 'DNI', true),
(2, 'R', 'RUC', true)
ON CONFLICT (id_tipo_doc) DO NOTHING;

-- 6. SECTOR
INSERT INTO neplatic.sector (id_sector, codigo, nombre, activo) VALUES
(1, 'S01', 'Sector Centro', true)
ON CONFLICT (id_sector) DO NOTHING;

-- 7. MANZANA
INSERT INTO neplatic.manzana (id_manzana, id_sector, codigo, activo) VALUES
(1, 1, 'MZ-001', true)
ON CONFLICT (id_manzana) DO NOTHING;

-- 8. VIA
INSERT INTO neplatic.via (id_via, codigo, nombre, tipo) VALUES
(1, 'V-001', 'Av. Principal', 'AVENIDA')
ON CONFLICT (id_via) DO NOTHING;

-- 9. LOTE
INSERT INTO neplatic.lote (id_lote, id_manzana, id_via, codigo, numero_municipal, direccion, activo) VALUES
(1, 1, 1, 'L-001', '100', 'Av. Principal 100', true),
(2, 1, 1, 'L-002', '200', 'Av. Principal 200', true),
(3, 1, 1, 'L-003', '300', 'Calle Secundaria 50', true)
ON CONFLICT (id_lote) DO NOTHING;

-- 10. CONTRIBUYENTES
INSERT INTO neplatic.contribuyente (id_contribuyente, id_tipo_doc, numero_documento, nombres, apellido_paterno, apellido_materno, direccion_fiscal, activo) VALUES
(1, 1, '12345678', 'Juan', 'Perez', 'Garcia', 'Av. Principal 100', true),
(2, 1, '87654321', 'Maria', 'Lopez', 'Quispe', 'Av. Principal 200', true),
(3, 1, '11223344', 'Carlos', 'Mamani', 'Choque', 'Calle Secundaria 50', true)
ON CONFLICT (id_contribuyente) DO NOTHING;

-- 11. USUARIOS DE PRUEBA
-- admin1 / Admin2026  (Administrador)
INSERT INTO neplatic.usuario (id_usuario, username, password_hash, nombres, apellidos, id_rol, email, activo, bloqueado) VALUES
(1, 'admin1', '$2b$12$LJ3m4ys3GZfnYMz8kVsKaOLSfFbhpmEKWmO4VHxGvFrbBZz5Xt1Oq', 'Admin', 'Sistema', 1, 'admin@municipalidad.gob.pe', true, false)
ON CONFLICT (id_usuario) DO NOTHING;

-- notif1 / Campo2026  (Notificador)
INSERT INTO neplatic.usuario (id_usuario, username, password_hash, nombres, apellidos, id_rol, email, activo, bloqueado) VALUES
(2, 'notif1', '$2b$12$testHASHnotificador1campo2026aaaaaaa', 'Pedro', 'Flores Condori', 3, 'pedro.flores@municipalidad.gob.pe', true, false)
ON CONFLICT (id_usuario) DO NOTHING;

-- 12. DEUDAS DE PRUEBA
INSERT INTO neplatic.deuda (id_deuda, id_contribuyente, id_lote, id_tipo_tributo, id_estado_cobranza, anio_tributo, periodo, monto_original, saldo_pendiente, fecha_emision, fecha_vencimiento, activo) VALUES
(101, 1, 1, 1, 2, 2026, '202601', 850.00, 850.00, '2026-01-15', '2026-03-31', true),
(102, 2, 2, 1, 3, 2025, '202503', 2100.00, 2100.00, '2025-03-01', '2025-06-30', true),
(103, 3, 3, 2, 2, 2026, '202602', 450.00, 450.00, '2026-02-01', '2026-04-30', true),
(104, 1, 1, 2, 1, 2026, '202603', 320.00, 320.00, '2026-03-01', '2026-05-31', true),
(105, 2, 2, 2, 2, 2026, '202601', 180.00, 180.00, '2026-01-10', '2026-03-15', true)
ON CONFLICT (id_deuda) DO NOTHING;

-- 13. CONTRIBUYENTE_LOTE (relacion)
INSERT INTO neplatic.contribuyente_lote (id_contribuyente, id_lote, tipo_relacion) VALUES
(1, 1, 'PROPIETARIO'),
(2, 2, 'PROPIETARIO'),
(3, 3, 'PROPIETARIO')
ON CONFLICT DO NOTHING;

-- 14. RUTA DE NOTIFICACION para notif1 (id_usuario=2)
INSERT INTO neplatic.ruta_notificacion (id_ruta, id_usuario, fecha_ruta, estado_ruta, total_deudas, distancia_estimada_km) VALUES
(1, 2, CURRENT_DATE, 'PLANIFICADA', 3, 4.5)
ON CONFLICT (id_ruta) DO NOTHING;

-- 15. RUTA DETALLE - orden de visita para las deudas
INSERT INTO neplatic.ruta_detalle (id_ruta_detalle, id_ruta, id_deuda, orden_visita, visitado) VALUES
(1, 1, 101, 1, false),
(2, 1, 102, 2, false),
(3, 1, 104, 3, false)
ON CONFLICT (id_ruta_detalle) DO NOTHING;

-- 16. PERMISOS
INSERT INTO neplatic.permiso (id_permiso, codigo, nombre, descripcion, modulo) VALUES
(1, 'usuarios:gestionar', 'Gestion de usuarios', 'Crear, editar, desactivar usuarios', 'usuarios'),
(2, 'rutas:visualizar_propias', 'Ver rutas propias', 'Visualizar rutas asignadas al usuario', 'rutas'),
(3, 'notificaciones:registrar', 'Registrar notificaciones', 'Registrar visitas de campo', 'notificaciones'),
(4, 'reportes:descargar', 'Descargar reportes', 'Exportar reportes en PDF y Excel', 'reportes'),
(5, 'etl:ejecutar', 'Ejecutar ETL', 'Ejecutar proceso ETL Oracle->PostgreSQL', 'etl')
ON CONFLICT (id_permiso) DO NOTHING;

-- 17. ROL_PERMISO
INSERT INTO neplatic.rol_permiso (id_rol, id_permiso) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5),  -- Admin: todos
(3, 2), (3, 3)                                -- Notificador: rutas propias + notificar
ON CONFLICT DO NOTHING;

-- ============================================================
-- VERIFICACION
-- ============================================================
SELECT '--- VERIFICACION ---' AS msg;

SELECT 'usuarios' AS tabla, count(*) AS registros FROM neplatic.usuario
UNION ALL SELECT 'roles', count(*) FROM neplatic.rol_usuario
UNION ALL SELECT 'deudas', count(*) FROM neplatic.deuda
UNION ALL SELECT 'contribuyentes', count(*) FROM neplatic.contribuyente
UNION ALL SELECT 'rutas', count(*) FROM neplatic.ruta_notificacion
UNION ALL SELECT 'detalle_ruta', count(*) FROM neplatic.ruta_detalle
UNION ALL SELECT 'estados_notif', count(*) FROM neplatic.estado_notificacion
UNION ALL SELECT 'permisos', count(*) FROM neplatic.rol_permiso;

-- Datos clave para el formulario "Notificar visita":
SELECT '--- DATOS PARA PROBAR ---' AS msg;
SELECT 
    rd.id_deuda AS "ID Deuda (usar en formulario)",
    d.saldo_pendiente AS "Monto S/",
    l.direccion AS "Direccion fiscal",
    c.nombres || ' ' || c.apellido_paterno AS "Contribuyente",
    ec.nombre AS "Etapa cobranza"
FROM neplatic.ruta_detalle rd
JOIN neplatic.deuda d ON rd.id_deuda = d.id_deuda
JOIN neplatic.lote l ON d.id_lote = l.id_lote
JOIN neplatic.contribuyente c ON d.id_contribuyente = c.id_contribuyente
JOIN neplatic.estado_cobranza ec ON d.id_estado_cobranza = ec.id_estado
WHERE rd.visitado = false
ORDER BY rd.orden_visita;
