import os

def kill():
	os.system("ps aux | grep ython | grep repo_manager | awk '{print $2}' | xargs kill -9")

if __name__ == '__main__':
	kill()
	os.system('nohup python3 -u repo_manager.py &')
	os.system('touch nohup.out')
	os.system('tail -F nohup.out')