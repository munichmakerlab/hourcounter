# Web based based Hour Counter

We have a laser cutter at our space and wanted to track how long and often it runs. So we connected an ESP8266 to it, that measures the time it's running and posts it to this API thing here.

## UI endpoints

### ```GET /```
Index page, lists all devices registered.

### ```GET /device/<device name>```
Usage details for a specific device.

## API endpoints
We're sort of REST conform, but not really, due to simplifications on the ESP

### ```GET /api/device```
Returns a list of all devices being tracked, and their usage counts

### ```GET /api/device/<device name>```
Gets the usage counts of a specific device

### ```POST /api/device/<device name>```
Adds a new usage entry to the specified device. The duration of usage is to be passed as the "time" parameter in the URL, in seconds.

Example: ```curl -X PUT http://hourcounter.hackerspace.example/api/device/laser01/?time=42```

### ```GET /api/device/<device name>/jobs```
### ```GET /api/device/<device name>/jobs/<page>```
Gets all usage entries for a specific device, paged by 100 entries each.

### ```GET /api/device/<device name>/daily```
Get device usage by day, for a specific device.

### ```GET /api/device/<device name>/stats```
Gets usage statistics of a specific device, by hour and day of the week

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
