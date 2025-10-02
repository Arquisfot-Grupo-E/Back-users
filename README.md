# Back-users 👤

Microservicio de gestión de usuarios para la plataforma BookReview. Este backend está desarrollado con Django y Django REST Framework, proporcionando autenticación y gestión de perfiles de usuario.

## 🚀 Características

- **Autenticación JWT**: Sistema seguro de autenticación con tokens
- **Gestión de usuarios**: Registro, login y gestión de perfiles
- **API RESTful**: Endpoints bien documentados y estructurados
- **Reseteo de contraseñas**: Sistema de recuperación de contraseñas por email
- **Permisos y roles**: Sistema de autorización granular
- **Base de datos SQLite**: Fácil configuración para desarrollo

## 📋 Prerrequisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- **Python 3.8+**
- **pip** (gestor de paquetes de Python)
- **Virtual environment** (recomendado)

## 🛠️ Instalación

### 1. Clona el repositorio
```bash
git clone <url-del-repositorio>
cd Back-users
```

### 2. Crea un entorno virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configura la base de datos
```bash
python manage.py migrate
```

### 5. (Opcional) Crea un superusuario
```bash
python manage.py createsuperuser
```

## 🏃‍♂️ Ejecución

Para ejecutar el servidor de desarrollo:

```bash
python manage.py runserver 8001
```

El servidor estará disponible en: `http://localhost:8001`

## 📚 API Endpoints

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/accounts/register/` | Registro de nuevos usuarios |
| POST | `/accounts/login/` | Inicio de sesión (obtener token JWT) |
| POST | `/token/refresh/` | Renovar token JWT |

### Gestión de usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/accounts/profile/` | Obtener perfil del usuario actual |
| PUT | `/accounts/profile/update/` | Actualizar perfil del usuario |
| GET | `/accounts/users/` | Listar usuarios (solo admin) |

### Recuperación de contraseñas
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/accounts/password-reset/` | Solicitar reseteo de contraseña |
| POST | `/accounts/password-reset-confirm/` | Confirmar reseteo de contraseña |

## 🔧 Configuración

### Variables de entorno

El proyecto utiliza las siguientes configuraciones que puedes ajustar:

- **DEBUG**: Modo de desarrollo (True por defecto)
- **SECRET_KEY**: Clave secreta de Django
- **ALLOWED_HOSTS**: Hosts permitidos
- **DATABASE**: Configuración de base de datos (SQLite por defecto)

### Base de datos

Por defecto, el proyecto utiliza SQLite para facilitar el desarrollo. La base de datos se crea automáticamente como `db.sqlite3` en el directorio raíz.

## 📁 Estructura del proyecto

```
Back-users/
├── accounts/              # Aplicación principal de usuarios
│   ├── models.py         # Modelos de datos
│   ├── serializers.py    # Serializadores para API
│   ├── views.py          # Vistas/Controladores
│   ├── urls.py           # Rutas de la aplicación
│   └── migrations/       # Migraciones de base de datos
├── back_users/           # Configuración del proyecto
│   ├── settings.py       # Configuraciones
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # Configuración WSGI
├── manage.py             # Script de gestión de Django
├── requirements.txt      # Dependencias del proyecto
└── README.md            # Este archivo
```

## 🔐 Autenticación JWT

El sistema utiliza JWT (JSON Web Tokens) para la autenticación:

1. **Login**: Envía credenciales a `/accounts/login/`
2. **Token**: Recibes `access_token` y `refresh_token`
3. **Autorización**: Incluye el token en el header: `Authorization: Bearer <access_token>`
4. **Renovación**: Usa `/token/refresh/` para renovar tokens expirados

### Ejemplo de uso:

```bash
# Login
curl -X POST http://localhost:8001/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario", "password": "contraseña"}'

# Usar token
curl -X GET http://localhost:8001/accounts/profile/ \
  -H "Authorization: Bearer <tu-access-token>"
```

## 🛡️ Seguridad

- Tokens JWT con expiración automática
- Validación de contraseñas robustas
- Protección CSRF habilitada
- Sanitización de datos de entrada
- Permisos basados en roles

## 🐛 Solución de problemas

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de tener el entorno virtual activado
pip install -r requirements.txt
```

### Error: "Database is locked"
```bash
# Detén el servidor y ejecuta las migraciones
python manage.py migrate
```

### Puerto 8001 ocupado
```bash
# Usa un puerto diferente
python manage.py runserver 8002
```

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la documentación de Django: https://docs.djangoproject.com/
2. Consulta la documentación de Django REST Framework: https://www.django-rest-framework.org/
3. Abre un issue en el repositorio

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

**Desarrollado con ❤️ para BookReview Platform**
