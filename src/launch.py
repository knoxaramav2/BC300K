from display import get_display
from state_broker import StateBroker

if __name__ == '__main__':
    print('Starting...')
    get_display()
    StateBroker().run()
    