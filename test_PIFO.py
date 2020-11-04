#!/usr/bin/env python

import random
import simpy
from hwsim_utils import HW_sim_object, PIFO

"""
Testbench for the PIFO object
"""
class PIFO_tb(HW_sim_object):
    def __init__(self, env, period):
        super(PIFO_tb, self).__init__(env, period)

        # create the pipes used for communication with the PIFO object
        self.pifo_r_in_pipe = simpy.Store(env)
        self.pifo_r_out_pipe = simpy.Store(env)
        self.pifo_w_in_pipe = simpy.Store(env)
        self.pifo_w_out_pipe = simpy.Store(env)

        # instantiate the PIFO object
        self.pifo = PIFO(env, period, self.pifo_r_in_pipe, self.pifo_r_out_pipe, self.pifo_w_in_pipe, self.pifo_w_out_pipe, maxsize=128, write_latency=1, read_latency=2, init_items=[])

        self.run()

    def run(self):
        """
        Register the testbench's processes with the simulation environment
        """
        self.env.process(self.rw_pifo_sm())

    def rw_pifo_sm(self):
        """
        State machine to push all test data then read it back
        """
        data_words = random.sample(range(0, 20), 10)

        # push all data
        for word in data_words:
            print ('@ {:04d} - pushed data word {}'.format(self.env.now, word))
            self.pifo_w_in_pipe.put(word)
            yield self.pifo_w_out_pipe.get()

        # pop all items
        for i in range(len(data_words)):
            # submit pop request (value in put is a don't care)
            self.pifo_r_in_pipe.put(1) 
            word = yield self.pifo_r_out_pipe.get()
            print ('@ {:04d} - popped data word {}'.format(self.env.now, word))


def main():
    # create the simulation environment
    env = simpy.Environment()
    period = 1 # amount of simulation time / clock cycle
    pifo_tb = PIFO_tb(env, period)
 
    # run the simulation for 100 simulation seconds (100 clock cycles)
    env.run(until=100)


if __name__ == "__main__":
    main()

