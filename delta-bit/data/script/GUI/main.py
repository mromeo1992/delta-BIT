from nicegui import ui


from script.GUI.pages import home, gui


@ui.page('/')
def index():
    home.home_page()


@ui.page('/query')
def query():
    gui.query()


@ui.page('/finetune')
def finetune():
    ui.notify("Ti piacissi! 800A")


ui.run(
    title='DeLTA-BIT',
    host='0.0.0.0',
    port=8080
)