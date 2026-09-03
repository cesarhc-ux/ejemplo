import reflex as rx

from login.components.auth_layout import auth_layout
from login.states.auth_state import AuthState


def login_page() -> rx.Component:
    return auth_layout(
        title="Iniciar sesión",
        subtitle="Ingresa con tu cuenta ",
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
                rx.text(
                    "¿No tienes una cuenta?",
                    color="gray",
                ),
                rx.link(
                    "Crear cuenta",
                    href="/registro",
                    font_weight="600",
                ),
                justify="center",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
    )