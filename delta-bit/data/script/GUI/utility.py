from nicegui import app, ui
from nicegui.client import Client
import requests


@app.post('/notify')
async def notify(payload: dict):

    msg = payload.get('message', '')

    for client in Client.instances.values():

        await client.run_javascript(f'''
            Quasar.Notify.create({{
                message: "{msg}",
                color: "positive"
            }})
        ''')

    return {'ok': True}




def open_viewer(path):

    TF_URL = "http://tf:9000/view"

    r = requests.post(TF_URL, json={'path': path})
    img_b64 = r.json()['image']

    with ui.dialog().props('maximized') as dialog:

        with ui.element('div').style(
            '''
            width: 80vw;
            height: 80vh;
            display: flex;
            flex-direction: column;
            background: white;
            align-items: center;
            justify-content: center;
            '''
        ):

            ui.label('MRI Viewer').classes('text-h6')

            ui.image(
                'data:image;base64,' + img_b64
            ).style(
                '''
                flex: 1;
                width: 50%;
                height: 60%;
                object-fit: contain;
                display: block;
                margin: auto;
                '''
            )
            ui.button('Close', on_click=dialog.close)

    dialog.open()