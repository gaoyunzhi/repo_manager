import os
import sys

def kill():
	os.system("ps aux | grep ython | grep repo_manager | awk '{print $2}' | xargs kill -9")

if __name__ == '__main__':
	kill()
	if 'kill' in sys.argv:
		return
	os.system('nohup python3 -u repo_manager.py &')
	os.system('touch nohup.out')
	os.system('tail -F nohup.out')