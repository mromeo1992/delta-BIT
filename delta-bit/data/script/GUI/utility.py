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

    #default axis value

    axis= "axial"

    TF_URL = "http://tf:9000/view"
    TF_URL2 = "http://tf:9000//imsize"




    with ui.dialog().props('maximized') as dialog:

        with ui.element('div').style(
            '''
            width: 70vw;
            height: 80vh;
            display: flex;
            flex-direction: column;
            background: white;
            align-items: center;
            justify-content: center;
            '''
        ):
            
            projection_select = ui.select(
                options=['axial', 'sagittal', 'coronal'],
                value='axial',
                label='Projection'
            ).classes('w-48')            

            ui.label('MRI Viewer').classes('text-h6')

            slice_slider = ui.slider(
                min=0,
                max=100,
                value=50
            ).props('label').classes('w-96')

            slice_label = ui.label('Slice: {}'.format(slice_slider.value))
            
            '''requests.post(
                    TF_URL2,
                    json={
                        'path': path,
                        'axis': projection_select.value
                    }
                ),'''            

        # CREA UNA SOLA IMMAGINE
            image = ui.image().style('''
                width: 40%;
                height: 90%;
                object-fit: contain;
            ''')

            def update_image():

                r = requests.post(
                    TF_URL,
                    json={
                        'path': path,
                        'axis': projection_select.value,
                        'slice' : int(slice_slider.value)

                    }
                )

                if r.status_code != 200:
                    ui.notify(r.text)
                    return

                img_b64 = r.json()['image']

                # AGGIORNA L'IMMAGINE ESISTENTE
                image.set_source(
                    'data:image/png;base64,' + img_b64
                )

            projection_select.on_value_change(
                lambda _: update_image()
            )

            slice_slider.on_value_change(
                lambda _: update_image()
            )

            update_image()

        ui.button('Close', on_click=dialog.close)




    dialog.open()