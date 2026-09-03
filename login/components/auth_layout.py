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
                    rx.heading(
                        title,
                        size="7",
                        text_align="center",
                    ),
                    rx.text(
                        subtitle,
                        color="gray",
                        text_align="center",
                    ),
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