import requests


TF_URL = "http://tf:9000"


def start_tensorboard():

    try:
        response = requests.post(
            f"{TF_URL}/tensorboard/start",
            timeout=5
        )

        return response.json()

    except Exception as e:
        print(
            f"TensorBoard start error: {e}"
        )

        return None



def stop_tensorboard():

    try:
        response = requests.post(
            f"{TF_URL}/tensorboard/stop",
            timeout=5
        )

        return response.json()

    except Exception as e:
        print(
            f"TensorBoard stop error: {e}"
        )

        return None



def tensorboard_status():

    try:

        response = requests.get(
            f"{TF_URL}/tensorboard/status",
            timeout=5
        )

        return response.json()

    except Exception as e:

        print(
            f"TensorBoard status error: {e}"
        )

        return {
            "running": False
        }