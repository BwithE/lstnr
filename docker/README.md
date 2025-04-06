# LSTNR DOCKERIZED

I created this to make deploying my Attack-Box easy and convenient.

LSTNR starts on port 443

An UPPY webserver starts on port 80 in the background, which recieves GET/POST requests to transfers files.

Tools can be found in /opt/tools within the container.

# TOOLS
- linpeas.sh
- pspy64
- winPEASx64.exe

# TO DO
- Will be adding more tools that need to be transferred to TGT

# USAGE
```
sudo bash build-lstnr.sh
```
