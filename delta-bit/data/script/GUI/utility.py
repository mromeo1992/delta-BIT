from nicegui import app, ui
from nicegui.client import Client

import nibabel as nib
import numpy as np
from scipy.ndimage import center_of_mass

from PIL import Image
from io import BytesIO
import base64

# -------------------------
# CACHE
# -------------------------
VOLUME_CACHE = {}
SLICE_CACHE = {}
MASK_CACHE = {}

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

def load_mask(path):
    if path not in MASK_CACHE:
        m = nib.load(path).get_fdata().astype(np.uint8)
        MASK_CACHE[path] = m
    return MASK_CACHE[path]

"""def get_mask_slice(mask, axis, sl):

    if axis == 'axial':
        m = mask[:, :, sl]
    elif axis == 'coronal':
        m = mask[:, sl, :]
    else:
        m = mask[sl, :, :]

    return np.rot90(m)"""


def blend_image(img, mask):

    base = Image.fromarray(img).convert("L").convert("RGBA")

    # mask → grayscale overlay
    m = Image.fromarray(mask)

    # normalize mask to alpha
    m = np.array(m).astype(np.uint8)
    m = (m > 0).astype(np.uint8) * 120  # intensity controllata

    alpha = Image.fromarray(m).convert("L")

    overlay = Image.new("RGBA", base.size, (255, 0, 0, 0))
    overlay.putalpha(alpha)

    # merge
    return Image.alpha_composite(base, overlay)


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



def open_viewer(path, mask_path=None):

    volume = load_volume(path)

    mask_volume = None

    if mask_path is not None:
        mask_volume = load_mask(mask_path)
        xc , yc, zc = center_of_mass(mask_volume)
        xc, yc, zc = int(xc), int(yc), int(zc)
    else:
        xc , yc , zc = volume.shape[0]//2, volume.shape[1]//2, volume.shape[2]//2

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
    
    def get_mask_slice(axis, sl):

        if mask_volume is None:
            return None

        if axis == 'axial':
            m = mask_volume[:, :, sl]
        elif axis == 'coronal':
            m = mask_volume[:, sl, :]
        else:
            m = mask_volume[sl, :, :]

        return np.rot90(m)    

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
                value=zc
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

                # -------------------------
                # MASK (if available)
                # -------------------------
                if mask_volume is not None:
                    mask = get_mask_slice(
                        projection_select.value,
                        int(slice_slider.value)
                    )
                    final = blend_image(img, mask)
                else:
                    final = Image.fromarray(img).convert("RGBA")


                #pil = Image.fromarray(img)

                # small performance boost (avoid recompute)
                image.set_source(final)

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
                    slice_slider.value = zc
                elif axis == 'coronal':
                    slice_slider.max = y - 1
                    slice_slider.value = yc
                else:
                    slice_slider.max = x - 1
                    slice_slider.value = xc

                #slice_slider.value = slice_slider.max // 2

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
                    #new_value = zc
                elif projection_select.value == 'coronal':
                    max_v = y - 1
                    #new_value = yc
                else:
                    max_v = x - 1
                    #new_value = xc

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