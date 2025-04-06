docker build -t lstnr .
docker run -it --name lstnr -p 21:21 -p 80:80 -p 443:443 -p 445:445 -p 4444:4444 lstnr
