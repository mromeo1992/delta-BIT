from fastapi import FastAPI
import json
import os



app2 = FastAPI()

@app2.post("/predict")
def predict():
    #predizione
    conf_img = "/data/config/config.json"
    config_img_data = json.load(open(conf_img))
    from .predict_vim import predict_vim
    predict_vim(config_img_data)

@app2.get('/viewer')
def viewer(path: str):
    import nibabel as nib
    import matplotlib.pylab as plt
    import io, base64

    if not os.path.exists(path):
        return ui.label("File not found")

    img = nib.load(path).get_fdata()
    slice_img = img[:, :, img.shape[2] // 2]

    fig = plt.figure()
    plt.imshow(slice_img.T, cmap='gray', origin='lower')
    plt.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    encoded = base64.b64encode(buf.read()).decode('utf-8')

    return f'<img src="data:image/png;base64,{encoded}"/>'