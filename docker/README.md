# LSTNR DOCKERIZED

I created this to make deploying my Attack-Box easy and convenient.

By default, LSTNR starts on port 443. It then forwards all common ports through the host to the container.

An UPPY webserver can be started on port 80 in the background, which recieves GET/POST requests to transfers files.

The web server gets wonky after the first few get/post, so stopping and restarting it works.

Tools can be found in /opt/tools within the container.

# TOOLS
- linpeas.sh
- pspy64
- winPEASx64.exe

# TO DO
- Will be adding more tools that need to be transferred to TGT
- Need to fix HTTP server timing out

# USAGE
```
sudo bash build-lstnr.sh
```
