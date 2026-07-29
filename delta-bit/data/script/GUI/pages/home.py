from nicegui import ui


@ui.page('/goodbye')
def goodbye():
    with ui.column().classes('w-full h-screen items-center justify-center'):
        ui.icon('warning').classes('text-7xl text-red-600')
        ui.label('You have chosen to leave this application.').classes(
            'text-3xl font-bold'
        )
        ui.label(
            'This application is intended for research purposes only.'
        ).classes('text-lg text-gray-600')


def home_page():

    # ---------------- Splash Screen ----------------
    with ui.dialog().props('persistent') as disclaimer:
        with ui.card().classes('w-[650px] p-8'):
            ui.icon('warning').classes('text-6xl text-orange-600 self-center')

            ui.label('Research Use Only').classes(
                'text-3xl font-bold self-center'
            )

            ui.separator()

            ui.label(
                "This tool is to be used for research purposes only and "
                "is not intended for clinical use.\n\n"
                "Any use for clinical purposes is at the user's own risk."
            ).classes('text-lg text-center')

            with ui.row().classes('w-full justify-center gap-6 mt-4'):
                ui.button(
                    'I understand',
                    icon='check',
                    color='positive',
                    on_click=disclaimer.close,
                ).classes('w-48')

                ui.button(
                    'Leave',
                    icon='logout',
                    color='negative',
                    on_click=lambda: ui.navigate.to('/goodbye'),
                ).classes('w-48')

    disclaimer.open()

    # ---------------- Main Page ----------------

    with ui.column().classes(
        'w-full items-center max-w-5xl mx-auto gap-6 p-8'
    ):

        ui.label("🧠 DeLTA-BIT").classes(
            "text-6xl font-extrabold text-black-700"
        )

        ui.label(
            "Deep Learning framework TrActography based for BraIn Targeting"
        ).classes(
            "text-2xl text-gray-600 italic text-center"
        )

        with ui.card().classes("w-full p-6 shadow-xl"):

            ui.label(
                "DeLTA-BIT (Deep Learning framework TrActography based for BraIn Targeting) "
                "is an AI tool to support Focused Ultrasound Surgery (FUS) and "
                "Deep Brain Stimulation (DBS) procedures in Essential Tremor patients. "
                "It is based on a deep learning model for the automatic segmentation "
                "of the Vim nucleus from T1-weighted MRI data."
            ).classes("text-xl")

            ui.separator()

            ui.label(
                "The tool allows users to query the model for Vim segmentation "
                "and to fine-tune the model on new data."
            ).classes("text-lg")

            ui.label(
                "This tool is for research purposes only and is not intended "
                "for clinical use."
            ).classes("text-lg text-red-600 font-semibold")

            with ui.row().classes("items-center gap-2"):
                ui.label("Please cite:")
                ui.link(
                    "https://doi.org/10.48550/arXiv.2312.15462",
                    "https://doi.org/10.48550/arXiv.2312.15462",
                    new_tab=True,
                ).classes("text-blue-600 underline")

        ui.label("Select an option below to proceed").classes(
            "text-xl font-bold"
        )

        with ui.row().classes("gap-8"):

            ui.button(
                "Model Query",
                icon="search",
                on_click=lambda: ui.navigate.to("/query"),
            ).classes("w-56 h-20 text-lg")

            ui.button(
                "Fine-tuning",
                icon="model_training",
                on_click=lambda: ui.navigate.to("/finetune"),
            ).classes("w-56 h-20 text-lg")