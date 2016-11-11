from flask import Flask, request, jsonify
from datetime import datetime
from peewee import *

app = Flask(__name__)
app.secret_key = "oedshfoisuhlaskjfhalskdfjhas"

db = SqliteDatabase('hourcounter.db')

class BaseModel(Model):
	class Meta:
		database = db

class Device(BaseModel):
	name = CharField()

class CounterEntry(BaseModel):
	device = ForeignKeyField(Device)
	duration = IntegerField()
	timestamp = DateTimeField(default=datetime.now())

db.create_tables([Device, CounterEntry], True)

@app.route("/api/device/<string:name>", methods=['PUT'])
def newEntry(name):
	#try:
	time = int(request.args.get("time"))
	device , _= Device.get_or_create(name=name)
	CounterEntry.create(device=device, duration = time)
	#except:
#		return "error"
	return "success"

@app.route("/api/device/<string:name>", methods=['GET'])
def getDeviceInfo(name):
	try:
		device = Device.get(name=name)
	except:
		return "not found"
	return str(CounterEntry.select(fn.Sum(CounterEntry.duration)).where(CounterEntry.device == device).scalar())
