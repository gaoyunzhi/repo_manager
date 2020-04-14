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

def loopImp():
	r = os.system('pip3 install --user -r all_dependencies.txt --upgrade')
	print(r)
	config = readFile('config')
	repo_names = readFile('repo_names')

def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

if __name__ == '__main__':
	loop()