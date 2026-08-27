# Politica de Privacidad — VANER ASSET
# Cumplimiento GDPR/LGPD

## 1. Informacion del Responsable

- **Nombre:** VANER ASSET
- **Dominio:** vanerasset.com
- **Contacto:** soporte@vanerasset.com

## 2. Datos Recopilados

### 2.1 Datos de Identificacion
- Nombre completo
- Correo electronico
- Numero de telefono (opcional)
- Empresa/Organizacion

### 2.2 Datos de Autenticacion
- Contrasena hasheada (Argon2id)
- Tokens de sesion
- Historial de contrasenas (ultimas 5)
- Secretos MFA (TOTP)

### 2.3 Datos de Uso
- Registros de auditoria
- Logs de sistema
- Intentos de login
- IPs de origen

### 2.4 Datos de Negocio (Tenant-scoped)
- Equipos e inventario
- Mantenimientos y ordenes de trabajo
- Evidencias fotograficas
- Repuestos y movimientos
- Reportes generados

## 3. Base Legal para el Tratamiento

| Finalidad | Base Legal |
|-----------|------------|
| Autenticacion y acceso | Ejecucion de contrato |
| Gestion de inventario | Ejecucion de contrato |
| Auditoria y logs | Interes legitimo (seguridad) |
| Notificaciones | Consentimiento |
| Reportes y estadisticas | Ejecucion de contrato |

## 4. Derechos del Titular

### 4.1 Derecho de Acceso (Art. 15 GDPR)
El usuario puede solicitar una copia de todos sus datos personales.

**Implementacion:**
```http
GET /api/auth/mis-datos
```

### 4.2 Derecho de Rectificacion (Art. 16 GDPR)
El usuario puede corregir datos inexactos.

**Implementacion:**
```http
PUT /api/usuarios/{id}
```

### 4.3 Derecho de Supresion (Art. 17 GDPR)
El usuario puede solicitar la eliminacion de sus datos.

**Implementacion:**
```http
DELETE /api/auth/eliminar-cuenta
```

### 4.4 Derecho a la Portabilidad (Art. 20 GDPR)
El usuario puede exportar sus datos en formato estructurado.

**Implementacion:**
```http
GET /api/auth/exportar-datos
```

### 4.5 Derecho de Oposicion (Art. 21 GDPR)
El usuario puede oponerse al tratamiento de sus datos.

## 5. Retencion de Datos

| Tipo de Dato | Periodo de Retencion |
|--------------|---------------------|
| Datos de usuario | Mientras la cuenta este activa |
| Sesiones expiradas | 30 dias |
| Tokens de reset | 15 minutos |
| Registros de auditoria | 12 meses |
| Logs de sistema | 6 meses |
| Backups | 30 dias |
| Evidencias | Duracion del tenant |

## 6. Seguridad de los Datos

### 6.1 Cifrado
- Contraseñas: Argon2id (memory-hard)
- Datos sensibles: AES-256
- Transporte: TLS 1.3

### 6.2 Control de Acceso
- RBAC con 6 roles
- Row-Level Security (RLS) en 34 tablas
- MFA para roles criticos

### 6.3 Copias de Seguridad
- Backups automaticos diarios
- Retencion de 30 dias
- Cifrado de backups (opcional)

## 7. Transferencias Internacionales

No se realizan transferencias de datos fuera de la region del usuario sin su consentimiento explicito.

## 8. Cookies y Tecnologias de Rastreo

### 8.1 Cookies Esenciales
- `vaner_asset_refresh_token`: Autenticacion (necesaria)

### 8.2 Cookies de Analitica
No se utilizan cookies de analitica de terceros.

## 9. Menores de Edad

El servicio no esta dirigido a menores de 16 anos. No se recopilan datos de menores conscientemente.

## 10. Cambios en esta Politica

Los cambios seran notificados por correo electronico con 30 dias de antelacion.

## 11. Contacto para Asuntos de Privacidad

- **Email:** privacidad@vanerasset.com
- **Plazo de respuesta:** 30 dias

---

*Ultima actualizacion: 27 de agosto de 2026*
*Version: 1.0*
