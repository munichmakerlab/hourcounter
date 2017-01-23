from flask import Flask, request, jsonify, render_template
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

	def getStats(self):
		hourly_query = CounterEntry.select(fn.Sum(CounterEntry.duration).alias('total'), fn.strftime("%H", CounterEntry.timestamp).alias('hour')).where(CounterEntry.device == self).group_by(SQL('hour'))
		hourly = {}
		for entry in hourly_query:
			hourly[int(entry.hour)] = entry.total

		dow_query = CounterEntry.select(fn.Sum(CounterEntry.duration).alias('total'), fn.strftime("%w", CounterEntry.timestamp).alias('dow')).where(CounterEntry.device == self).group_by(SQL('dow'))
		dow=  {}
		for entry in dow_query:
			dow[entry.dow] = entry.total

		return { "hour": hourly, "dow": dow }

	def getDaily(self):
		daily_query = CounterEntry.select(fn.Sum(CounterEntry.duration).alias('total'), fn.strftime("%Y-%m-%d", CounterEntry.timestamp).alias('day')).where(CounterEntry.device == self).group_by(SQL('day'))
		daily = {}
		for entry in daily_query:
			daily[entry.day] = entry.total

		return daily

	def getJobs(self,page=1, limit=100):
		jobs_raw = self.counterentries.order_by(CounterEntry.timestamp.desc()).paginate(page,limit)

		jobs=[]

		for job in jobs_raw:
			jobs.append({"duration": job.duration, "timestamp": job.timestamp})
		return jobs

class CounterEntry(BaseModel):
	device = ForeignKeyField(Device, related_name='counterentries')
	duration = IntegerField()
	timestamp = DateTimeField(default=datetime.now)

db.create_tables([Device, CounterEntry], True)

@app.before_request
def before_request_handler():
	db.connect()

@app.teardown_request
def after_request_handler(exc):
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

@app.route("/api/device/<string:name>/stats", methods=['GET'])
@cross_origin()
def getDeviceStats(name):
	try:
		device = Device.get(name=name)
	except:
		return "not found"

	data = device.getStats()

	return jsonify(data)

@app.route("/api/device/<string:name>/jobs", methods=['GET'])
@app.route("/api/device/<string:name>/jobs/<int:page>", methods=['GET'])
@cross_origin()
def getDeviceJobs(name, page=1):
	try:
		device = Device.get(name=name)
	except:
		return "not found"

	return jsonify(device.getJobs(page))

@app.route("/api/device/<string:name>/daily", methods=['GET'])
@cross_origin()
def getDeviceDaily(name):
	try:
		device = Device.get(name=name)
	except:
		return "not found"

	data = device.getDaily()

	return jsonify(data)

@app.route("/", methods=['GET'])
def uiIndex():
	devices = Device.select();
	return render_template('index.html', devices=devices)

@app.route("/device/<string:name>", methods=['GET'])
def uiDevice(name):
	try:
		device = Device.get(name=name)
	except:
		return "not found"
	return render_template('device.html', device=device)
