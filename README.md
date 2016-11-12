´´´
docker build -t munichmakerlab/hourcounter .

docker run -d \
  --name=hourcounter \
  -v /data/hourcounter:/data \
  -e "VIRTUAL_HOST=hourcounter,hourcounter.intern.munichmakerlab.de" \
  munichmakerlab/hourcounter
´´´
