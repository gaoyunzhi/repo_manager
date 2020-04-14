import os
import threading
import yaml

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
			result[x[0]] = ' '.join(x[1:])
	return result

def process(dirname, runner_name, config):
	if not config.get('no_auto_commit'):
		os.popen('cd ../%s && git add . && git commit -m commit && git push -u -f' % dirname)
	r = os.popen('cd ../%s && git fetch origin && git rebase origin/master && git push -u -f' % dirname).read()
	if ('up to date' not in r or dep_installed) and not config.get('no_restart'):
		kill(runner_name)

def loopImp():
	r = os.popen('pip3 install --user -r all_dependencies.txt --upgrade').read()
	dep_installed = 'Successfully installed' in r

	with open('config.yaml') as f:
		config = yaml.load(f, Loader=yaml.FullLoader)

	repo_names = readFile('repo_names')

	for dirname in repo_names:
		runner_name = repo_names[dirname]
		config = config.get(runner_name, {})
		process(dirname, runner_name, config)
			







def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

if __name__ == '__main__':
	loop()