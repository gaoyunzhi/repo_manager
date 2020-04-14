import os
import threading

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

def kill():
	os.system("ps aux | grep ython | grep setup | awk '{print $2}' | xargs kill -9")

def loopImp():
	r = os.system('pip3 install --user all_dependencies.txt --upgrade')
	print(r)
	config = readFile('config')
	repo_names = readFile('repo_names')

def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

if __name__ == '__main__':
	kill()
	loop()