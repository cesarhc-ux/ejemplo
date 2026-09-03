import os

import reflex as rx

from login.services.supabase_client import get_supabase_client


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
            self.error_message = (
                "La contraseña debe tener al menos 6 caracteres."
            )
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