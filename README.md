# Web based based Hour Counter

We have a laser cutter at our space and wanted to track how long and often it runs. So we connected an ESP8266 to it, that measures the time it's running and posts it to this API thing here.

## API endpoints
We're sort of REST conform, but not really, due to simplifications on the ESP

### ```GET /api/device```
Returns a list of all devices being tracked, and their usage counts

### ```GET /api/device/<device name>```
Gets the usage counts of a specific device

### ```POST /api/device/<device name>```
Adds a new usage entry to the specified device. The duration of usage is to be passed as the "time" parameter in the URL, in seconds.

Example: ```curl -X PUT http://hourcounter.hackerspace.example/api/device/laser01/?time=42```

## Setup
We decided to run the counter in a docker container. The database all usage data is tracked in, is stored in the ```/data``` volume.

```
docker build -t munichmakerlab/hourcounter .

docker run -d \
  --name=hourcounter \
  -v /data/hourcounter:/data \
  -e "VIRTUAL_HOST=hourcounter,hourcounter.intern.munichmakerlab.de" \
  munichmakerlab/hourcounter
```
