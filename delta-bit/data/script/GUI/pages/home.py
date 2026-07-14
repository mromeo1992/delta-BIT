from nicegui import ui


def home_page():

    with ui.column().classes(
        'w-full items-center'
    ):

        ui.label("🧠 DeLTA-BIT").classes("text-2xl")


        ui.label(
            'DeLTA-BIT (Deep Learning framework TrActography based for BraIn Targeting) is a AI tool tu support Focused Ultrasound Surgery (FUS) and Deep Brain Stimulation (DBS) procedures in Essential Tremor patients. It is based on a deep learning model for the automatic segmentation of the Vim nucleus from T1 weighted MRI data.'
        ).classes(
            'text-3xl font-bold'
        )


        ui.label(
            'The tool allows to query the model for Vim segmentation and to fine-tune the model on new data.'
        ).classes(
            'text-lg'
        )

        ui.label("This tool is to be used for research purposes only and is not intended for clinical use. Any use for clinical purposes is at the user's own risk.").classes(
            'text-lg text-red-600')

        ui.label("Please cite the following paper if you use this tool in your research: https://doi.org/10.48550/arXiv.2312.15462").classes(
            'text-lg text-gray-600')
        ui.space()

        ui.label("Select an option below to proceed:").classes(
            'text-lg font-bold'
        )

        with ui.row():

            ui.button(
                'Model Query',
                icon='search',
                on_click=lambda: ui.navigate.to('/query')
            ).classes(
                'w-48 h-16'
            )


            ui.button(
                'Fine-tuning',
                icon='model_training',
                on_click=lambda: ui.navigate.to('/finetune')
            ).classes(
                'w-48 h-16'
            )