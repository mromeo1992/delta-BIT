# Installazione

## Installazione su Linux
per essere installato delta-bit richiede che docker sia installato e attivo sul sistema, per installare docker su linux è possibile seguire la guida ufficiale: https://docs.docker.com/engine/install/. L'uso della gpu richiede inoltre l'installazione di nvidia-docker, per installarlo è possibile seguire la guida ufficiale: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html.

comando di installazione (dalla cartella ./delta-bit/delta-bit):
```bash
sh install_docker.sh
```

## Installazione su Windows
per essere installato delta-bit richiede che docker sia installato e attivo sul sistema, per installare docker su windows è possibile seguire la guida ufficiale: https://docs.docker.com/desktop/install/windows-install/. L'uso della gpu richiede inoltre l'installazione di nvidia-docker, per installarlo è possibile seguire la guida ufficiale: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html.

cliccare sul file install_docker_for_windows.bat presente nella cartella ./delta-bit/delta-bit per avviare l'installazione di docker e nvidia-docker.


# Esecuzione

## Esecuzione su Linux
per eseguire delta-bit è sufficiente eseguire il comando:
```bash
sh run_delta_bit.sh
```

### comandi specifici
- per eseguire delta-bit senza uso gpu è possibile eseguire il comando:
```bash
docker compose -f docker-compose.yml up
```
## Esecuzione su Windows
per eseguire delta-bit è sufficiente eseguire il file run_delta_bit_windows.bat


## Installazione su server
delta-bit può essere installato su server ed eseguito da remoto. La procedure di installazione è la stessa descritta precedentemente. Per eseguire da remoto in sicurezza è necessario che il server sia configurato per accettare connessioni ssh e che il firewall sia configurato per permettere le connessioni sulla porta 22. A questo punto per accedere da remoto è necessario dare il comando:
```bash
ssh -L 8080:localhost:8080 username@server_ip
```
ciò permetterà di accedere all'interfaccia web di delta-bit all'indirizzo http://localhost:8080 dal proprio computer.


