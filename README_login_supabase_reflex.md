# Login, Registro y Página Protegida con Reflex y Supabase

Este proyecto contiene un sistema modular de autenticación con **Reflex** y **Supabase**. Permite crear cuentas, iniciar sesión, conservar la sesión al recargar la página, cerrar sesión y entrar a una página de prueba protegida.

## Funcionalidades

- Registro con correo y contraseña.
- Inicio y cierre de sesión.
- Validación de contraseña y mensajes de error.
- Redirección automática a `/prueba` cuando el inicio de sesión es correcto.
- Protección de la ruta `/prueba` para que nadie entre sin sesión válida.
- Persistencia de sesión mediante cookies.
- Tabla `profiles` vinculada a los usuarios de Supabase Auth.

> **Importante:** la contraseña no se guarda en una tabla creada por nosotros. Supabase la guarda cifrada dentro de `auth.users`.

## Estructura del proyecto

```text
login_supabase/
│
├── .env
├── .gitignore
├── requirements.txt
├── rxconfig.py
│
└── login_supabase/
    ├── __init__.py
    ├── login_supabase.py
    │
    ├── components/
    │   ├── __init__.py
    │   └── auth_layout.py
    │
    ├── pages/
    │   ├── __init__.py
    │   ├── login.py
    │   ├── registro.py
    │   └── prueba.py
    │
    ├── services/
    │   ├── __init__.py
    │   └── supabase_client.py
    │
    └── states/
        ├── __init__.py
        └── auth_state.py
```

## Instalación

En PowerShell, dentro de la carpeta principal del proyecto:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
reflex run
```

Después abre la dirección que aparezca en la terminal, normalmente `http://localhost:3000`.

## Archivos de configuración

### `requirements.txt`

```txt
reflex==0.9.9
supabase==2.31.0
python-dotenv>=1.0,<2.0
```

### `.env`

```env
SUPABASE_URL=https://TU-PROYECTO.supabase.co
SUPABASE_KEY=TU_CLAVE_ANON_O_PUBLISHABLE
COOKIE_SECURE=false
```

- `SUPABASE_URL`: URL de tu proyecto, obtenida en Supabase.
- `SUPABASE_KEY`: clave **anon** o **publishable** de Supabase.
- `COOKIE_SECURE=false`: se usa mientras pruebas en `localhost`. Para desplegar con HTTPS, cambia a `true`.

Nunca uses la clave `service_role` en este archivo ni en el frontend.

### `.gitignore`

```gitignore
venv/
.venv/
__pycache__/
*.pyc
.env
.web/
```

### `rxconfig.py`

```python
import reflex as rx


config = rx.Config(
    app_name="login_supabase",
    env_file=".env",
    plugins=[
        rx.plugins.RadixThemesPlugin(),
    ],
)
```

## Archivos `__init__.py`

### `login_supabase/__init__.py`

```python
```

### `login_supabase/services/__init__.py`

```python
```

### `login_supabase/states/__init__.py`

```python
from login_supabase.states.auth_state import AuthState

__all__ = ["AuthState"]
```

### `login_supabase/components/__init__.py`

```python
from login_supabase.components.auth_layout import auth_layout

__all__ = ["auth_layout"]
```

### `login_supabase/pages/__init__.py`

```python
from login_supabase.pages.login import login_page
from login_supabase.pages.prueba import prueba_page
from login_supabase.pages.registro import registro_page

__all__ = [
    "login_page",
    "registro_page",
    "prueba_page",
]
```

## Conexión con Supabase

### `login_supabase/services/supabase_client.py`

```python
import os

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url:
        raise ValueError("Falta SUPABASE_URL en el archivo .env")

    if not supabase_key:
        raise ValueError("Falta SUPABASE_KEY en el archivo .env")

    return create_client(supabase_url, supabase_key)
```

Este archivo crea la conexión con Supabase. Se crea un cliente nuevo por operación para evitar compartir sesiones entre personas diferentes.

## Estado de autenticación

### `login_supabase/states/auth_state.py`

```python
import os

import reflex as rx

from login_supabase.services.supabase_client import get_supabase_client


COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


class AuthState(rx.State):
    """Estado encargado del registro y autenticación."""

    email: str = ""
    password: str = ""
    confirm_password: str = ""

    error_message: str = ""
    success_message: str = ""
    is_loading: bool = False

    user_id: str = ""
    user_email: str = ""

    access_token: str = rx.Cookie(
        "",
        name="sb_access_token",
        path="/",
        max_age=604800,
        same_site="lax",
        secure=COOKIE_SECURE,
    )

    refresh_token: str = rx.Cookie(
        "",
        name="sb_refresh_token",
        path="/",
        max_age=604800,
        same_site="lax",
        secure=COOKIE_SECURE,
    )

    @rx.event
    def set_email(self, value: str):
        self.email = value

    @rx.event
    def set_password(self, value: str):
        self.password = value

    @rx.event
    def set_confirm_password(self, value: str):
        self.confirm_password = value

    def _clear_messages(self):
        self.error_message = ""
        self.success_message = ""

    def _save_session(self, session):
        self.access_token = session.access_token
        self.refresh_token = session.refresh_token

        if session.user:
            self.user_id = str(session.user.id)
            self.user_email = session.user.email or ""

    def _clear_session(self):
        self.access_token = ""
        self.refresh_token = ""
        self.user_id = ""
        self.user_email = ""
        self.password = ""
        self.confirm_password = ""

    def _friendly_error(self, error: Exception) -> str:
        message = str(error)

        if "Invalid login credentials" in message:
            return "El correo o la contraseña son incorrectos."

        if "Email not confirmed" in message:
            return "Primero debes confirmar tu correo electrónico."

        if "User already registered" in message:
            return "Ya existe una cuenta registrada con este correo."

        if "Password should be at least" in message:
            return "La contraseña debe tener al menos 6 caracteres."

        if "Unable to validate email address" in message:
            return "El correo electrónico no es válido."

        return f"No fue posible completar la operación: {message}"

    def _restore_session(self) -> bool:
        if not self.access_token or not self.refresh_token:
            return False

        supabase = get_supabase_client()

        session_response = supabase.auth.set_session(
            self.access_token,
            self.refresh_token,
        )

        session = session_response.session

        if session is None:
            return False

        user_response = supabase.auth.get_user(session.access_token)

        if user_response.user is None:
            return False

        self.access_token = session.access_token
        self.refresh_token = session.refresh_token
        self.user_id = str(user_response.user.id)
        self.user_email = user_response.user.email or ""

        return True

    @rx.event
    def register(self):
        self._clear_messages()

        email = self.email.strip().lower()

        if not email:
            self.error_message = "Escribe tu correo electrónico."
            return

        if not self.password:
            self.error_message = "Escribe una contraseña."
            return

        if len(self.password) < 6:
            self.error_message = "La contraseña debe tener al menos 6 caracteres."
            return

        if self.password != self.confirm_password:
            self.error_message = "Las contraseñas no coinciden."
            return

        self.is_loading = True
        yield

        try:
            supabase = get_supabase_client()

            response = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": self.password,
                }
            )

            if response.session is not None:
                self._save_session(response.session)
                self.is_loading = False
                yield rx.redirect("/prueba")
                return

            self.success_message = (
                "Cuenta creada. Revisa tu correo para confirmar el registro."
            )

            self.password = ""
            self.confirm_password = ""

        except ValueError as error:
            self.error_message = str(error)

        except Exception as error:
            self.error_message = self._friendly_error(error)

        self.is_loading = False
        yield

    @rx.event
    def login(self):
        self._clear_messages()

        email = self.email.strip().lower()

        if not email:
            self.error_message = "Escribe tu correo electrónico."
            return

        if not self.password:
            self.error_message = "Escribe tu contraseña."
            return

        self.is_loading = True
        yield

        try:
            supabase = get_supabase_client()

            response = supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": self.password,
                }
            )

            if response.session is None:
                self.error_message = "No se pudo iniciar la sesión."
                self.is_loading = False
                yield
                return

            self._save_session(response.session)
            self.password = ""
            self.is_loading = False

            yield rx.redirect("/prueba")

        except ValueError as error:
            self.error_message = str(error)
            self.is_loading = False
            yield

        except Exception as error:
            self.error_message = self._friendly_error(error)
            self.is_loading = False
            yield

    @rx.event
    def require_auth(self):
        """Protege la página de prueba."""
        try:
            if self._restore_session():
                return
        except Exception:
            pass

        self._clear_session()
        return rx.redirect("/")

    @rx.event
    def redirect_if_authenticated(self):
        """Evita mostrar el login cuando ya existe una sesión."""
        if not self.access_token or not self.refresh_token:
            return

        try:
            if self._restore_session():
                return rx.redirect("/prueba")
        except Exception:
            self._clear_session()

    @rx.event
    def logout(self):
        try:
            if self.access_token and self.refresh_token:
                supabase = get_supabase_client()
                supabase.auth.set_session(
                    self.access_token,
                    self.refresh_token,
                )
                supabase.auth.sign_out()
        except Exception:
            pass

        self._clear_session()
        self._clear_messages()

        return rx.redirect("/")
```

## Diseño reutilizable para login y registro

### `login_supabase/components/auth_layout.py`

```python
import reflex as rx


def auth_layout(
    title: str,
    subtitle: str,
    content: rx.Component,
) -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.center(
                    rx.box(
                        rx.text(
                            "S",
                            color="white",
                            font_size="1.6rem",
                            font_weight="bold",
                        ),
                        background="linear-gradient(135deg, #2563eb, #7c3aed)",
                        width="55px",
                        height="55px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        border_radius="16px",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.heading(title, size="7", text_align="center"),
                    rx.text(subtitle, color="gray", text_align="center"),
                    spacing="2",
                    width="100%",
                ),
                content,
                spacing="6",
                width="100%",
            ),
            width="100%",
            max_width="430px",
            padding="32px",
            box_shadow="0 20px 50px rgba(0, 0, 0, 0.10)",
        ),
        min_height="100vh",
        width="100%",
        padding="20px",
        background="linear-gradient(135deg, #eff6ff, #f5f3ff)",
    )
```

## Páginas

### `login_supabase/pages/login.py`

```python
import reflex as rx

from login_supabase.components.auth_layout import auth_layout
from login_supabase.states.auth_state import AuthState


def login_page() -> rx.Component:
    return auth_layout(
        title="Iniciar sesión",
        subtitle="Ingresa con tu cuenta de Supabase",
        content=rx.vstack(
            rx.vstack(
                rx.text("Correo electrónico", font_weight="500"),
                rx.input(
                    placeholder="correo@ejemplo.com",
                    type="email",
                    value=AuthState.email,
                    on_change=AuthState.set_email,
                    width="100%",
                    size="3",
                ),
                spacing="2",
                width="100%",
            ),
            rx.vstack(
                rx.text("Contraseña", font_weight="500"),
                rx.input(
                    placeholder="Escribe tu contraseña",
                    type="password",
                    value=AuthState.password,
                    on_change=AuthState.set_password,
                    width="100%",
                    size="3",
                ),
                spacing="2",
                width="100%",
            ),
            rx.cond(
                AuthState.error_message != "",
                rx.text(
                    AuthState.error_message,
                    color="red",
                    background="#fef2f2",
                    border="1px solid #fecaca",
                    padding="12px",
                    border_radius="8px",
                    width="100%",
                ),
            ),
            rx.button(
                "Iniciar sesión",
                on_click=AuthState.login,
                loading=AuthState.is_loading,
                width="100%",
                size="3",
            ),
            rx.hstack(
                rx.text("¿No tienes una cuenta?", color="gray"),
                rx.link("Crear cuenta", href="/registro", font_weight="600"),
                justify="center",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
    )
```

### `login_supabase/pages/registro.py`

```python
import reflex as rx

from login_supabase.components.auth_layout import auth_layout
from login_supabase.states.auth_state import AuthState


def registro_page() -> rx.Component:
    return auth_layout(
        title="Crear cuenta",
        subtitle="Regístrate utilizando tu correo electrónico",
        content=rx.vstack(
            rx.vstack(
                rx.text("Correo electrónico", font_weight="500"),
                rx.input(
                    placeholder="correo@ejemplo.com",
                    type="email",
                    value=AuthState.email,
                    on_change=AuthState.set_email,
                    width="100%",
                    size="3",
                ),
                spacing="2",
                width="100%",
            ),
            rx.vstack(
                rx.text("Contraseña", font_weight="500"),
                rx.input(
                    placeholder="Mínimo 6 caracteres",
                    type="password",
                    value=AuthState.password,
                    on_change=AuthState.set_password,
                    width="100%",
                    size="3",
                ),
                spacing="2",
                width="100%",
            ),
            rx.vstack(
                rx.text("Confirmar contraseña", font_weight="500"),
                rx.input(
                    placeholder="Repite tu contraseña",
                    type="password",
                    value=AuthState.confirm_password,
                    on_change=AuthState.set_confirm_password,
                    width="100%",
                    size="3",
                ),
                spacing="2",
                width="100%",
            ),
            rx.cond(
                AuthState.error_message != "",
                rx.text(
                    AuthState.error_message,
                    color="red",
                    background="#fef2f2",
                    border="1px solid #fecaca",
                    padding="12px",
                    border_radius="8px",
                    width="100%",
                ),
            ),
            rx.cond(
                AuthState.success_message != "",
                rx.text(
                    AuthState.success_message,
                    color="green",
                    background="#f0fdf4",
                    border="1px solid #bbf7d0",
                    padding="12px",
                    border_radius="8px",
                    width="100%",
                ),
            ),
            rx.button(
                "Crear cuenta",
                on_click=AuthState.register,
                loading=AuthState.is_loading,
                width="100%",
                size="3",
            ),
            rx.hstack(
                rx.text("¿Ya tienes una cuenta?", color="gray"),
                rx.link("Iniciar sesión", href="/", font_weight="600"),
                justify="center",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
    )
```

### `login_supabase/pages/prueba.py`

```python
import reflex as rx

from login_supabase.states.auth_state import AuthState


def prueba_page() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading("Página protegida", size="6"),
                    rx.text(
                        "Esta página solamente se muestra al iniciar sesión.",
                        color="gray",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.button(
                    "Cerrar sesión",
                    on_click=AuthState.logout,
                    color_scheme="red",
                    variant="soft",
                ),
                width="100%",
                align="center",
            ),
            background="white",
            border_bottom="1px solid #e5e7eb",
            padding="20px 30px",
            width="100%",
        ),
        rx.center(
            rx.card(
                rx.vstack(
                    rx.badge("Sesión activa", color_scheme="green", size="2"),
                    rx.heading("Inicio de sesión correcto", size="8", text_align="center"),
                    rx.text(
                        "Bienvenido a la página de prueba.",
                        color="gray",
                        font_size="1.1rem",
                    ),
                    rx.divider(),
                    rx.vstack(
                        rx.text("Correo del usuario", color="gray", font_size="0.9rem"),
                        rx.text(AuthState.user_email, font_weight="600"),
                        spacing="1",
                        align="center",
                    ),
                    rx.vstack(
                        rx.text("ID de Supabase", color="gray", font_size="0.9rem"),
                        rx.code(AuthState.user_id),
                        spacing="1",
                        align="center",
                    ),
                    spacing="5",
                    align="center",
                    width="100%",
                ),
                width="100%",
                max_width="650px",
                padding="40px",
            ),
            flex="1",
            width="100%",
            padding="30px",
        ),
        display="flex",
        flex_direction="column",
        min_height="100vh",
        width="100%",
        background="#f8fafc",
    )
```

## Archivo principal

### `login_supabase/login_supabase.py`

```python
import reflex as rx

from login_supabase.pages.login import login_page
from login_supabase.pages.prueba import prueba_page
from login_supabase.pages.registro import registro_page
from login_supabase.states.auth_state import AuthState


app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="blue",
        radius="large",
    )
)

app.add_page(
    login_page,
    route="/",
    title="Iniciar sesión",
    on_load=AuthState.redirect_if_authenticated,
)

app.add_page(
    registro_page,
    route="/registro",
    title="Crear cuenta",
    on_load=AuthState.redirect_if_authenticated,
)

app.add_page(
    prueba_page,
    route="/prueba",
    title="Página protegida",
    on_load=AuthState.require_auth,
)
```

## Tabla de Supabase para este proyecto

El formulario actual solo solicita correo y contraseña. Por ello, la tabla adicional guardará el identificador y correo del usuario.

En **Supabase → SQL Editor → New query**, ejecuta este código:

```sql
-- Tabla de información adicional para el proyecto Reflex
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text unique not null,
  created_at timestamp with time zone default now()
);

-- Activa Row Level Security
alter table public.profiles enable row level security;

-- Cada usuario únicamente ve su información
create policy "Usuario consulta su propio perfil"
on public.profiles
for select
to authenticated
using ((select auth.uid()) = id);

-- Cada usuario únicamente puede modificar su información
create policy "Usuario actualiza su propio perfil"
on public.profiles
for update
to authenticated
using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

-- Función que crea el perfil después del registro
create function public.crear_perfil_usuario()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email);

  return new;
end;
$$;

-- Trigger que se ejecuta automáticamente al crear un usuario
create trigger al_crear_usuario_auth
after insert on auth.users
for each row
execute procedure public.crear_perfil_usuario();
```

## Flujo del sistema

1. La persona entra a `/registro` y escribe correo, contraseña y confirmación.
2. Reflex ejecuta `AuthState.register()`.
3. Supabase crea el usuario dentro de `auth.users`.
4. El trigger `al_crear_usuario_auth` crea un registro en `public.profiles`.
5. Si la confirmación de correo está desactivada, la sesión se crea y la aplicación redirige a `/prueba`.
6. Si la confirmación de correo está activada, se muestra un mensaje para revisar el correo.
7. Al iniciar sesión correctamente, Reflex guarda los tokens en cookies y redirige a `/prueba`.
8. Al abrir `/prueba`, `require_auth()` valida la sesión con Supabase. Si no es válida, redirige al login.

## Configuración recomendada en Supabase

1. Ve a **Authentication → Providers → Email** y confirma que Email esté habilitado.
2. Para pruebas rápidas, puedes desactivar **Confirm email** temporalmente.
3. Copia la URL y clave publishable o anon de **Connect** o **Project Settings → API**.
4. Colócalas en `.env`.
5. Ejecuta el SQL anterior una sola vez.

## Problemas comunes

| Error | Causa probable | Solución |
|---|---|---|
| `Falta SUPABASE_URL` | No existe `.env` o no tiene la URL. | Crea `.env` en la carpeta principal y coloca la URL. |
| `Falta SUPABASE_KEY` | Falta la clave de Supabase. | Copia la clave anon o publishable en `.env`. |
| `Invalid login credentials` | Correo o contraseña incorrectos. | Verifica los datos o registra una cuenta nueva. |
| `Email not confirmed` | La confirmación por correo está activa. | Confirma el correo antes de iniciar sesión. |
| `User already registered` | El correo ya está registrado. | Inicia sesión con esa cuenta. |
| Error 500 al registrarte | Error en el trigger o tabla de Supabase. | Revisa que hayas ejecutado correctamente el SQL de `profiles`. |

