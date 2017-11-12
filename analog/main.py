import time
from potentiometer import Potentiometer

def main():
    pot = Potentiometer(on_header=True)
    while True:
        time.sleep(0.5)
        print(pot.read())
    

if __name__ == '__main__':
    main()
