from flask import Flask, request, jsonify
from flask_cors import cross_origin
from datetime import datetime, timedelta
from peewee import *

app = Flask(__name__)
app.secret_key = "oedshfoisuhlaskjfhalskdfjhas"

db = SqliteDatabase('hourcounter.db')

class BaseModel(Model):
	class Meta:
		database = db

class Device(BaseModel):
	name = CharField()

	def getUsage(self):
		total = CounterEntry.select(fn.Sum(CounterEntry.duration)).where(CounterEntry.device == self).scalar()
		total_last_hour = CounterEntry.select(fn.Sum(CounterEntry.duration)).where(CounterEntry.device == self, CounterEntry.timestamp > (datetime.now() - timedelta(hours=1))).scalar() or 0
		total_today = CounterEntry.select(fn.Sum(CounterEntry.duration)).where(CounterEntry.device == self, CounterEntry.timestamp > datetime.now().replace(hour=0, minute=0,second=0)).scalar() or 0

		return {
			"total": total,
			"last_hour": total_last_hour,
			"today": total_today
		};

	def lastEntry(self):
		entry = CounterEntry.select().where(CounterEntry.device == self).order_by(CounterEntry.timestamp.desc()).get()
		return { "timestamp": entry.timestamp, "duration": entry.duration }

class CounterEntry(BaseModel):
	device = ForeignKeyField(Device)
	duration = IntegerField()
	timestamp = DateTimeField(default=datetime.now)

db.create_tables([Device, CounterEntry], True)

@app.before_request
def before_request_handler():
	db.connect()

@app.teardown_request
def after_request_handler():
	if not db.is_closed():
		db.close()

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
@cross_origin()
def getDeviceInfo(name):
	try:
		device = Device.get(name=name)
	except:
		return "not found"

	data = {
		"device": device.name,
		"usage": device.getUsage(),
		"last_job": device.lastEntry()
	}
	return jsonify(data)

@app.route("/api/device", methods=['GET'])
@cross_origin()
def getDevicesInfo():
	data = []

	for device in Device.select():
		data.append({
			"device": device.name,
			"usage": device.getUsage(),
			"last_job": device.lastEntry()
		});

	return jsonify(data)
