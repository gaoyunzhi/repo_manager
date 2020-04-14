import os
import threading
import yaml

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

def loopImp():
	r = os.popen('pip3 install --user -r all_dependencies.txt --upgrade').read()
	if 'Successfully installed' in r:
		print('~~~Successfully installed~~')
	else:
		print('no new')
	with open('config.yaml') as f:
		config = yaml.load(f, Loader=yaml.FullLoader)
	repo_names = readFile('repo_names')
	for dirname in repo_names:
		runner_name = repo_names[dirname]
		config = config.get(runner_name, {})
		print(config.get('no_auto_commit'))
		if not config.get('no_auto_commit'):
			os.popen('cd ../%s && git add . && git commit -m commit && git push -u -f' % dirname)
		r = os.popen('cd ../%s && git fetch origin && git rebase origin/master && git push -u -f' % dirname)
		print('pull result', r)



def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

if __name__ == '__main__':
	loop()