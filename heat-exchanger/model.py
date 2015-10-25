import logging
import numpy as np
from scipy.integrate import odeint

from utils.stopwatch import Stopwatch

# noinspection PyPep8Naming
class Model(object):
    def __init__(self, parameters=None, time = None):
        logging.info("Created model")

        self.params = parameters if parameters is not None else Model.init_params()
        logging.info("Parameters map: %s.", self.params)

        self.tick_time = time if time is not None else 1  # seconds
        logging.info("Using tick time %ss.", self.tick_time)

        self.T_PM = 0.
        self.T_ZCO = 0.
        logging.info("Setting initial values for T_PM=%f, T_ZCO=%f", self.T_PM, self.T_ZCO)

    @staticmethod
    def init_params():
        parameters = {'M_M': 1.,
                      'c_wym': 1.,
                      'F_ZM': 1.,
                      'g_w': 1.,
                      'c_w': 1.,
                      'k_w': 1.,
                      'M_CO': 1.,
                      'F_ZCO': 1.}
        return parameters

    def tick(self, T_ZM, T_PCO, time=None):
        if time is None:
            time = self.tick_time

        logging.info('Ticking with values T_ZM=%f, T_PCO=%f for %d seconds.', T_ZM, T_PCO, time)

        sw = Stopwatch()
        sw.start()

        y0 = np.array([self.T_PM, self.T_ZCO])
        t = np.array([0, time])
        # t = np.linspace(0, time)  # diff is about +30% in time

        Xp = odeint(Model.solve, y0, t, args=(self.prepare_matrices(T_ZM, T_PCO)))

        self.T_PM, self.T_ZCO = Xp[-1]

        logging.info('New state, T_PM=%f, T_ZCO=%f, took %fs', self.T_PM, self.T_ZCO, sw.time_elapsed)
        return self.T_PM, self.T_ZCO

    def prepare_matrices(self, T_ZM, T_ZCO):
        c_w = self.params['c_w']
        F_ZM = self.params['F_ZM']
        c_wym = self.params['c_wym']
        M_CO = self.params['M_CO']
        F_ZCO = self.params['F_ZCO']
        M_M = self.params['M_M']
        k_w = self.params['k_w']
        g_w = self.params['g_w']

        a11 = -(k_w + F_ZM * c_w * g_w) / (M_M * c_wym)
        a12 = k_w / (M_M * c_wym)
        a21 = k_w / (M_CO * c_wym)
        a22 = -(k_w + F_ZCO * c_w * g_w) / (M_CO * c_wym)

        b11 = (F_ZM * c_w * g_w) / (M_M * c_wym)
        b22 = (F_ZCO * c_w * g_w) / (M_CO * c_wym)

        A = (a11, a12, a21, a22)
        B = (b11, 0, 0, b22)
        U = (T_ZM, T_ZCO)

        return A, B, U

    # noinspection PyUnusedLocal
    @staticmethod
    def solve(X, t, A, B, U):
        a11 = A[0]
        a12 = A[1]
        a21 = A[2]
        a22 = A[3]

        b11 = B[0]
        b12 = B[1]
        b21 = B[2]
        b22 = B[3]

        u1 = U[0]
        u2 = U[1]

        x1 = X[0]
        x2 = X[1]

        xp1 = a11 * x1 + a12 * x2 + b11 * u1 + b12 * u2
        xp2 = a21 * x1 + a22 * x2 + b21 * u1 + b22 * u2

        return np.array([xp1, xp2])
