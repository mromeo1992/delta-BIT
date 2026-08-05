from nicegui import ui, app

from fastapi import Request
from fastapi.responses import Response

import httpx

from script.GUI.pages import home, gui, ftune


@app.api_route(
    "/tensorboard/{path:path}",
    methods=["GET", "POST"]
)
async def tensorboard_proxy(
    request: Request,
    path: str
):

    async with httpx.AsyncClient() as client:

        response = await client.request(
            method=request.method,
            url=f"http://tf:6006/{path}",
            headers=dict(request.headers),
            content=await request.body()
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers={
            "content-type":
                response.headers.get(
                    "content-type",
                    "text/html"
                )
        }
    )



@ui.page('/')
def index():
    home.home_page()


@ui.page('/query')
def query():
    gui.query()


@ui.page('/finetune')
def finetune():
    ftune.finetune()


ui.run(
    title='DeLTA-BIT',
    host='0.0.0.0',
    port=8080
)