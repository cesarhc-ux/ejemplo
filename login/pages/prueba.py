import reflex as rx

from login.states.auth_state import AuthState


def prueba_page() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading(
                        "Página protegida",
                        size="6",
                    ),
                    rx.text(
                        "Hola que tal esto es una prueba de registro y login.",
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
                    rx.badge(
                        "Sesión activa",
                        color_scheme="green",
                        size="2",
                    ),
                    rx.heading(
                        "Inicio de sesión correcto",
                        size="8",
                        text_align="center",
                    ),
                    rx.text(
                        "Bienvenido a la página de prueba.",
                        color="gray",
                        font_size="1.1rem",
                    ),
                    rx.divider(),
                    rx.vstack(
                        rx.text(
                            "Correo del usuario",
                            color="gray",
                            font_size="0.9rem",
                        ),
                        rx.text(
                            AuthState.user_email,
                            font_weight="600",
                        ),
                        spacing="1",
                        align="center",
                    ),
                    rx.vstack(
                        rx.text(
                            "ID de Supabase",
                            color="gray",
                            font_size="0.9rem",
                        ),
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