import os
import threading
import yaml
import time
import datetime

INTERVAL = 10
schedule = {}

def running(name):
	r = os.popen('ps aux | grep ython | grep %s' % name).read()
	# if not running, we will have one empty line, one grep line
	return len(r.split('\n')) > 2 

def kill(name):
	os.system("ps aux | grep ython | grep %s | awk '{print $2}' | xargs kill -9" % name)

def readFile(fn):
	result = {}
	with open(fn + '.txt') as f:
		for x in f.readlines():
			x = x.strip()
			if not x:
				continue
			x = x.split()
			result[x[0]] = x[1]
	return result

def isAfternoon():
	dt = datetime.datetime.now()
	return dt.time() > datetime.time(12)

def okToRestart(config):
	if config.get('restart_only_afternoon'):
		return isAfternoon()
	return True

def processSchedule(configs):
	for key in list(schedule.keys()):
		if schedule[key] > time.time():
			continue
		del schedule[key]
		dirname, runner_name = key
		if running(runner_name):
			continue
		config = configs.get(runner_name, {})
		setup_file = config.get('custom_setup_name', 'setup')
		args = ['notail']
		if config.get('restart_only_afternoon'):
			args.append('skip')
		r = os.popen('cd ../%s && python3 %s.py %s' % (
			dirname, setup_file, ' '.join(args))).read()

def process(dirname, runner_name, config, dep_installed):
	if not config.get('no_auto_commit'):
		os.popen('cd ../%s && git add . && git commit -m commit && git push -u -f' % dirname).read()

	r = os.popen('cd ../%s && git fetch origin && git rebase origin/master && git push -u -f' % dirname).read()
	if ('up to date' not in r or dep_installed) and okToRestart(config):
		kill(runner_name)

	if (not running(runner_name)) and (dirname, runner_name) not in schedule:
		schedule[(dirname, runner_name)] = \
			time.time() + config.get('pause_before_restart', 0) * 60

def loopImp():
	r = os.popen('pip3 install --user -r all_dependencies.txt --upgrade').read()
	dep_installed = 'Successfully installed' in r

	with open('config.yaml') as f:
		config = yaml.load(f, Loader=yaml.FullLoader)

	repo_names = readFile('repo_names')

	for dirname in repo_names:
		runner_name = repo_names[dirname]
		process(dirname, runner_name, config.get(runner_name, {}), dep_installed)

	processSchedule(config)

def loop():
	loopImp()
	threading.Timer(INTERVAL, loop).start() 

if __name__ == '__main__':
	print('START')
	loop()