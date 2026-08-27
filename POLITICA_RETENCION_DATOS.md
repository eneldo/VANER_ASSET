# Politica de Retencion de Datos — VANER ASSET

## Objetivo

Establecer los periodos de retencion y eliminacion de datos para cumplir con GDPR/LGPD y garantizar la seguridad del sistema.

## 1. Datos de Usuario

| Campo | Retencion | Accion |
|-------|-----------|--------|
| Nombre, email, telefono | Cuenta activa | Mantener |
| Contrasena hasheada | Cuenta activa | Mantener |
| Historial de contrasenas | 5 ultimas | Eliminar automaticamente |
| Secretos MFA | Cuenta activa | Mantener |
| Tokens de sesion | 30 dias | Eliminar automaticamente |
| Intentos de login fallidos | 24 horas | Eliminar automaticamente |

## 2. Tokens de Seguridad

| Tipo | Retencion | Accion |
|------|-----------|--------|
| Access token | 30 minutos | Expiracion automatica |
| Refresh token | 7 dias | Expiracion automatica |
| Password reset token | 15 minutos | Eliminar al usar o expirar |
| MFA backup codes | Cuenta activa | Mantener |

## 3. Auditoria y Logs

| Tipo | Retencion | Accion |
|------|-----------|--------|
| Registros de auditoria | 12 meses | Eliminar automaticamente |
| Logs de sistema | 6 meses | Eliminar automaticamente |
| Logs de SMTP | 30 dias | Eliminar automaticamente |
| Logs de DevOps | 30 dias | Eliminar automaticamente |
| Logs de scheduler | 30 dias | Eliminar automaticamente |

## 4. Backups

| Tipo | Retencion | Accion |
|------|-----------|--------|
| Backups completos | 30 dias | Eliminar automaticamente |
| Backups incrementales | 7 dias | Eliminar automaticamente |

## 5. Datos de Negocio (Tenant-scoped)

| Tipo | Retencion | Accion |
|------|-----------|--------|
| Empresas | Cuenta activa | Mantener |
| Sedes | Cuenta activa | Mantener |
| Equipos | Cuenta activa | Mantener |
| Mantenimientos | Cuenta activa | Mantener |
| Ordenes de trabajo | Cuenta activa | Mantener |
| Evidencias | Cuenta activa | Mantener |
| Repuestos | Cuenta activa | Mantener |
| Reportes | Cuenta activa | Mantener |

## 6. Eliminacion de Cuenta

Cuando un usuario solicita eliminar su cuenta:

1. **Verificacion:** Confirmar identidad via email
2. **Anonimizacion:** Los datos de negocio se anonimizan
3. **Eliminacion:** Datos personales se eliminan en 30 dias
4. **Backup:** Los backups se eliminan en el siguiente ciclo de retencion

## 7. Implementacion Tecnica

### 7.1 Eliminacion Automatica
```python
# Ejemplo: Eliminar sesiones expiradas
DELETE FROM refresh_tokens WHERE expira_en < NOW() - INTERVAL '30 days'
```

### 7.2 Anonimizacion
```python
# Ejemplo: Anonimizar usuario eliminado
UPDATE usuarios SET
    email = CONCAT('deleted_', id, '@deleted.com'),
    nombre_completo = 'Usuario Eliminado',
    telefono = NULL,
    password_hash = NULL,
    mfa_secret = NULL
WHERE id = :user_id
```

### 7.3 Limpieza de Backups
```bash
# Ejemplo: Eliminar backups antiguos
find backups/ -name "*.sql.gz" -mtime +30 -delete
```

## 8. Responsabilidades

- **Administrador:** Supervisar cumplimiento de la politica
- **Desarrolladores:** Implementar mecanismos de retencion
- **Auditoria:** Revisar ejecucion trimestralmente

---

*Ultima actualizacion: 27 de agosto de 2026*
*Version: 1.0*
