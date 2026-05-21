# Note su Docker delta-bit

- Per esporre tensorborad al di fuore del container, è necessario esporre la porta 6006 (o quella configurata) e mappare questa porta al momento del run del container. Ad esempio:

```bash
docker run -it -p 6006:6006 delta-bit:latest
```
interno al container, è possibile avviare tensorboard con:

```bash
tensorboard --logdir=logs --host=0.0.0.0 --port=6006
```
A questo punto dal link [http://0.0.0.0:6006/](http://0.0.0.0:6006/) sarà possibile accedere a tensorboard dal browser del host.


# Note su Docker compose delta-bit

per lannciare il singolo container:

```bash
docker compose run tf