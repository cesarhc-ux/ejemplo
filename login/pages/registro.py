import reflex as rx

from login.components.auth_layout import auth_layout
from login.states.auth_state import AuthState


def registro_page() -> rx.Component:
    return auth_layout(
        title="Crear cuenta",
        subtitle="Regístrate utilizando tu correo electrónico",
        content=rx.vstack(
            rx.vstack(
                rx.text(
                    "Correo electrónico",
                    font_weight="500",
                ),
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
                rx.text(
                    "Contraseña",
                    font_weight="500",
                ),
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
                rx.text(
                    "Confirmar contraseña",
                    font_weight="500",
                ),
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
                rx.text(
                    "¿Ya tienes una cuenta?",
                    color="gray",
                ),
                rx.link(
                    "Iniciar sesión",
                    href="/",
                    font_weight="600",
                ),
                justify="center",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
    )