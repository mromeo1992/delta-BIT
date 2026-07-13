from nicegui import app, ui
from nicegui.client import Client

import nibabel as nib
import numpy as np
from scipy.ndimage import center_of_mass

from PIL import Image
from io import BytesIO
import base64
import time

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
        m = nib.load(path)
        m = nib.as_closest_canonical(m)
        m = m.get_fdata().astype(np.uint8)
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

"""
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
    return Image.alpha_composite(base, overlay)"""


def load_volume(path):

    if path not in VOLUME_CACHE:

        volume = nib.load(path)
        volume = nib.as_closest_canonical(volume)
        volume = volume.get_fdata()

        volume = volume.astype(np.float32)

        volume -= volume.min()

        if volume.max() > 0:
            volume /= volume.max()

        volume = (volume * 255).astype(np.uint8)

        VOLUME_CACHE[path] = volume

    return VOLUME_CACHE[path]


"""def render_slice(slice_img):

    img = Image.fromarray(slice_img)

    buffer = BytesIO()

    img.save(buffer, format='PNG', optimize=True)

    return (
        'data:image/png;base64,' +
        base64.b64encode(buffer.getvalue()).decode()
    )"""


"""
def normalize_volume(vol):
    vol = vol.astype(np.float32)
    vol -= vol.min()
    if vol.max() > 0:
        vol /= vol.max()
    return (vol * 255).astype(np.uint8)"""

"""
def get_slice(volume, axis, sl):
    if axis == 'axial':
        img = volume[:, :, sl]
    elif axis == 'coronal':
        img = volume[:, sl, :]
    else:
        img = volume[sl, :, :]

    if native:
        img=img[:,::-1]
    return np.rot90(img)"""



def open_viewer(path, mask_path=None):

    volume = load_volume(path)
    x, y, z = volume.shape

    # -------------------------
    # MASK (optional)
    # -------------------------
    mask_volume = None
    if mask_path is not None:
        mask_volume = load_mask(mask_path)
        try:
            xc, yc, zc = center_of_mass(mask_volume)
            xc, yc, zc = int(xc), int(yc), int(zc)
        except:
            xc, yc, zc = x // 2, y // 2, z // 2
    else:
        xc, yc, zc = x // 2, y // 2, z // 2

    # -------------------------
    # STATE
    # -------------------------
    current_axis = "axial"
    last_render = 0
    last_wheel_time = 0

    zoom = 1.0
    pan_x = 0
    pan_y = 0

    is_dragging = False
    last_mouse = {"x": 0, "y": 0}

    # -------------------------
    # SLICE ENGINE
    # -------------------------
    def get_slice(axis, sl):

        if axis == 'axial':
            img = volume[:, :, sl]
            img = np.fliplr(np.rot90(img[:,:]))
        elif axis == 'coronal':
            img = volume[:, sl, :]
            img = np.fliplr(np.rot90(img[:,:]))
        else:
            img = volume[sl, :, :]
            img = np.rot90(img[:,:])
        
        return img

    def get_mask_slice(axis, sl):

        if mask_volume is None:
            return None

        if axis == 'axial':
            m = mask_volume[:, :, sl]
            m = np.fliplr(np.rot90(m[:,:]))
        elif axis == 'coronal':
            m = mask_volume[:, sl, :]
            m = np.fliplr(np.rot90(m[:,:]))
        else:
            m = mask_volume[sl, :, :]
            m = np.rot90(m[:,:])

        return m

    # -------------------------
    # BLEND MASK
    # -------------------------
    #from PIL import Image

    def blend_image(img, mask):

        base = Image.fromarray(img).convert("L").convert("RGBA")

        m = np.array(mask).astype(np.uint8)
        m = (m > 0).astype(np.uint8) * 120  # opacity controllata

        alpha = Image.fromarray(m).convert("L")

        overlay = Image.new("RGBA", base.size, (255, 0, 0, 0))
        overlay.putalpha(alpha)

        return Image.alpha_composite(base, overlay)

    # -------------------------
    # UI
    # -------------------------
    with ui.dialog().props('maximized') as dialog:
        ui.run_javascript("""
        document.addEventListener('wheel', function(e) {
            if (e.ctrlKey) {
                e.preventDefault();
                e.stopPropagation();
            }
        }, { passive: false });
        """)        

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
            # IMAGE
            # -------------------------
            image = ui.image().props('fit=contain').classes('w-full grow min-h-0')

            # -------------------------
            # RENDER ENGINE
            # -------------------------
            def update_image():

                nonlocal last_render

                now = time.time()
                if now - last_render < 0.025:
                    return
                last_render = now

                img = get_slice(
                    projection_select.value,
                    int(slice_slider.value)
                )

                if mask_volume is not None:
                    mask = get_mask_slice(
                        projection_select.value,
                        int(slice_slider.value)
                    )
                    final = blend_image(img, mask)
                else:
                    final = Image.fromarray(img).convert("RGBA")

                # -------------------------
                # ZOOM
                # -------------------------
                if zoom != 1.0:
                    w, h = final.size
                    final = final.resize(
                        (int(w * zoom), int(h * zoom)),
                        resample=Image.Resampling.BILINEAR
                    )

                # -------------------------
                # PAN
                # -------------------------
                if zoom > 1.0:
                    w, h = final.size
                    crop_w = int(w / zoom)
                    crop_h = int(h / zoom)

                    left = int((w - crop_w) / 2 + pan_x)
                    top = int((h - crop_h) / 2 + pan_y)

                    final = final.crop((
                        left,
                        top,
                        left + crop_w,
                        top + crop_h
                    ))

                image.set_source(final)

                slice_label.set_text(
                    f"Slice: {int(slice_slider.value)}"
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

                update_image()

            projection_select.on_value_change(
                lambda e: change_axis(e.value)
            )

            slice_slider.on_value_change(
                lambda _: update_image()
            )

            # -------------------------
            # WHEEL (slice + zoom)
            # -------------------------
            def on_wheel(e):

                nonlocal last_wheel_time, zoom

                now = time.time()

                delta = e.args.get("deltaY", 0)
                ctrl = e.args.get("ctrlKey", False)

                # ZOOM MODE
                if ctrl:

                    if delta > 0:
                        zoom = max(1.0, zoom - 0.1)
                    else:
                        zoom = min(5.0, zoom + 0.1)

                    update_image()
                    return

                # SLICE MODE
                if now - last_wheel_time < 0.01:
                    return

                last_wheel_time = now

                step = 1 if delta > 0 else -1

                new_value = int(slice_slider.value) + step

                if projection_select.value == 'axial':
                    max_v = z - 1
                elif projection_select.value == 'coronal':
                    max_v = y - 1
                else:
                    max_v = x - 1

                slice_slider.value = max(0, min(max_v, new_value))
                update_image()

            # -------------------------
            # PAN EVENTS (FIX ORDER OK)
            # -------------------------
            def on_mouse_down(e):
                nonlocal is_dragging
                is_dragging = True
                last_mouse["x"] = e.args.get("clientX", 0)
                last_mouse["y"] = e.args.get("clientY", 0)

            def on_mouse_up(e):
                nonlocal is_dragging
                is_dragging = False

            def on_mouse_move(e):
                nonlocal pan_x, pan_y

                if not is_dragging or zoom == 1.0:
                    return

                x = e.args.get("clientX", 0)
                y = e.args.get("clientY", 0)

                dx = x - last_mouse["x"]
                dy = y - last_mouse["y"]

                pan_x += dx
                pan_y += dy

                last_mouse["x"] = x
                last_mouse["y"] = y

                update_image()

            # -------------------------
            # BIND EVENTS
            # -------------------------
            image.on("wheel", on_wheel)
            image.on("mousedown", on_mouse_down)
            image.on("mouseup", on_mouse_up)
            image.on("mousemove", on_mouse_move)

            # -------------------------
            # INIT
            # -------------------------
            update_image()

          

        ui.button('Close', on_click=dialog.close)
        

    dialog.open()



