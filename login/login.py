import reflex as rx

from login.pages.login import login_page
from login.pages.prueba import prueba_page
from login.pages.registro import registro_page
from login.states.auth_state import AuthState


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