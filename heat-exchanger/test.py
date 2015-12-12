import logging
import time
from exchanger import model, communication

logging_level = logging.DEBUG

def init_logger():
    format_style = '%(asctime)s %(levelname)s %(filename)s: %(message)s'
    logging.basicConfig(format=format_style, level=logging_level)
    logging.info("Initialized logger")

def main():
    exchanger = model.Model(time=1)
    exchanger.update_parameters({'k_w': 25000, 'F_zm': 40., 'F_zco': 45, 'T_zm': 120., 'T_pco': 30.})
    for i in range(1000):
        exchanger.tick(1)
        state = exchanger.get_state()
        print(state['T_pm'], state['T_zco'])
        exchanger.update_parameters({'T_pco': state['T_zco'] *.98})
        # time.sleep(0.1)

if __name__ == '__main__':
    main()
