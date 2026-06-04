from nicegui import app, ui
from nicegui.client import Client

import nibabel as nib
import numpy as np

from PIL import Image
from io import BytesIO
import base64

# -------------------------
# CACHE
# -------------------------
VOLUME_CACHE = {}
SLICE_CACHE = {}

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


def load_volume(path):

    if path not in VOLUME_CACHE:

        volume = nib.load(path).get_fdata()

        volume = volume.astype(np.float32)

        volume -= volume.min()

        if volume.max() > 0:
            volume /= volume.max()

        volume = (volume * 255).astype(np.uint8)

        VOLUME_CACHE[path] = volume

    return VOLUME_CACHE[path]


def render_slice(slice_img):

    img = Image.fromarray(slice_img)

    buffer = BytesIO()

    img.save(buffer, format='PNG', optimize=True)

    return (
        'data:image/png;base64,' +
        base64.b64encode(buffer.getvalue()).decode()
    )


SLICE_CACHE = {}

def normalize_volume(vol):
    vol = vol.astype(np.float32)
    vol -= vol.min()
    if vol.max() > 0:
        vol /= vol.max()
    return (vol * 255).astype(np.uint8)


def get_slice(volume, axis, sl):
    if axis == 'axial':
        img = volume[:, :, sl]
    elif axis == 'coronal':
        img = volume[:, sl, :]
    else:
        img = volume[sl, :, :]
    return np.rot90(img)



def open_viewer(path):

    volume = load_volume(path)
    x, y, z = volume.shape

    current_axis = "axial"

    import time

    last_render = 0

    # -------------------------
    # SLICE ENGINE
    # -------------------------
    def get_slice(axis, sl):

        if axis == 'axial':
            img = volume[:, :, sl]

        elif axis == 'coronal':
            img = volume[:, sl, :]

        else:
            img = volume[sl, :, :]

        return np.rot90(img)

    # -------------------------
    # FAST CACHE (optional but crucial for smooth scroll)
    # -------------------------
    slice_cache = {}

    def get_cached_slice(axis, sl):

        key = (axis, sl)

        if key in slice_cache:
            return slice_cache[key]

        img = get_slice(axis, sl)
        slice_cache[key] = img
        return img

    # -------------------------
    # UI
    # -------------------------
    with ui.dialog().props('maximized') as dialog:#.props('maximized') as dialog:

        """with ui.column().style('''
            width: 100%;
            height: 100%;
            background: white;
            align-items: center;
            justify-content: center;
        '''):"""
        with ui.element('div').style('''
            width: 80vw;
            height: 90vh;
            display: flex;
            background: white;
            flex-direction: column;
            align-items: center;
            justify-content: center;                                     
            
        '''):

            projection_select = ui.select(
                options=['axial', 'sagittal', 'coronal'],
                value='axial',
                label='Projection'
            ).classes('w-48')

            ui.label('MRI Viewer').classes('text-h6')

            slice_slider = ui.slider(
                min=0,
                max=z - 1,
                value=z // 2
            ).props('label').classes('w-96')

            slice_label = ui.label()

            # -------------------------
            # IMAGE (no base64 bottleneck logic)
            # -------------------------
            image = ui.image().props('fit=contain').classes('w-full grow min-h-0').style('''
                will-change: transform;
            ''')

            # -------------------------
            # SMOOTH RENDER ENGINE
            # -------------------------
            def update_image():

                nonlocal last_render

                now = time.time()

                # soft throttle (30–40 FPS cap)
                if now - last_render < 0.025:
                    return

                last_render = now

                img = get_cached_slice(
                    projection_select.value,
                    int(slice_slider.value)
                )

                # IMPORTANT: direct numpy → PIL (NO base64)
                from PIL import Image

                pil = Image.fromarray(img)

                # small performance boost (avoid recompute)
                image.set_source(pil)

                slice_label.set_text(
                    f'Slice: {int(slice_slider.value)}'
                )

            # -------------------------
            # AXIS CHANGE
            # -------------------------
            def change_axis(axis):

                nonlocal current_axis

                current_axis = axis

                if axis == 'axial':
                    slice_slider.max = z - 1
                elif axis == 'coronal':
                    slice_slider.max = y - 1
                else:
                    slice_slider.max = x - 1

                slice_slider.value = slice_slider.max // 2

                update_image()

            projection_select.on_value_change(
                lambda e: change_axis(e.value)
            )

            slice_slider.on_value_change(
                lambda _: update_image()
            )

            # -------------------------
            # ULTRA SMOOTH WHEEL (NO JITTER, NO INERTIA)
            # -------------------------
            last_wheel_time = 0

            def on_wheel(e):

                nonlocal last_wheel_time

                now = time.time()

                # anti jitter trackpad
                if now - last_wheel_time < 0.01:
                    return

                last_wheel_time = now

                delta = e.args.get("deltaY", 0)

                # adaptive sensitivity (IMPORTANT)
                step = 1 if delta > 0 else -1

                new_value = int(slice_slider.value) + step

                # clamp
                if projection_select.value == 'axial':
                    max_v = z - 1
                elif projection_select.value == 'coronal':
                    max_v = y - 1
                else:
                    max_v = x - 1

                new_value = max(0, min(max_v, new_value))

                slice_slider.value = new_value

                update_image()

            image.on("wheel", on_wheel)

            # -------------------------
            # INITIAL
            # -------------------------
            update_image()

        ui.button('Close', on_click=dialog.close)

    dialog.open()