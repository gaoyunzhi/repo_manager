import threading
import yaml
import time
import datetime
import random
import subprocess
import os

INTERVAL = 10 * 60
schedule = {}

def log(text):
	print('%d:%d %s\n' % (datetime.datetime.now().hour, datetime.datetime.now().minute, text))

def runCommand(command):
	r = subprocess.Popen(command, shell=True, stdin=None, 
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return (r.stdout.read().decode("utf-8").strip() + 
		r.stdout.read().decode('utf-8').strip())

def running(name):
	r = runCommand('ps aux | grep ython | grep %s' % name)
	return len(r.split('\n')) > 1 

def kill(name):
	command = "ps aux | grep ython | grep %s | awk '{print $2}' | xargs kill -9" % name
	print('kill', name, command)
	os.system(command)

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
	return dt.hour > 12

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
		os.system('cd ../%s && nohup python3 %s.py %s &' % (
			dirname, setup_file, ' '.join(args)))
		log('rerun: ' + runner_name)

def repo_fetch(dirname):
	repo_fetch = runCommand('cd ../%s && git fetch origin && git rebase origin/master && git push -u -f' % dirname)
	result = ('up to date' not in repo_fetch and 
		'commit or stash them' not in repo_fetch)
	if result:
		print('repo fetch', dirname)
	return result

def process(dirname, runner_name, config, dep_installed):
	if not config.get('no_auto_commit'):
		runCommand('cd ../%s && git add . && git commit -m commit && git push -u -f' % dirname)

	if (repo_fetch(dirname) or dep_installed) and okToRestart(config):
		kill(runner_name)

	if config.get('restart_per_hour'):
		restart_interval = float(config.get('restart_per_hour'))
		if random.random() < INTERVAL * 1.0 / (60 * 60 * restart_interval):
			kill(runner_name)

	if (not running(runner_name)) and (dirname, runner_name) not in schedule:
		schedule[(dirname, runner_name)] = \
			time.time() + config.get('pause_before_restart', 0) * 60

def loopImp():
	for _ in range(5):
		kill('setup')
		kill('nohup.out')
		kill('tail')

	dep_installed = 'Successfully installed' in runCommand(
		'pip3 install --user -r all_dependencies.txt --upgrade')

	if dep_installed:
		print('dep installed')

	with open('config.yaml') as f:
		config = yaml.load(f, Loader=yaml.FullLoader)
	repo_names = readFile('repo_names')

	for dirname in repo_names:
		runner_name = repo_names[dirname]
		process(dirname, runner_name, 
			config.get(runner_name, {}), dep_installed)

	processSchedule(config)

def loop():
	loopImp()
	threading.Timer(INTERVAL, loop).start() 

if __name__ == '__main__':
	loop()