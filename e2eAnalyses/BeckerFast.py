"""
A faster implementation of the analyses by Becker et al.:

Becker et al. 2017:
Synthesizing Job-Level Dependencies for Automotive Multi-rate Effect Chains.
https://doi.org/10.1016/j.sysarc.2017.09.004
Becker et al. 2016:
Synthesizing Job-Level Dependencies for Automotive Multi-rate Effect Chains
https://doi.org/10.1109/RTCSA.2016.41
(Analysis presented here is without job-level dependencies)

Implementation is copied from https://github.com/tu-dortmund-ls12-rt/end-to-end_inter
with only minor adjustments

(see also the file: Becker2017.py)
"""


from cechains.chain import CEChain
from tasks.task import Task
from math import ceil
from utilities.scheduler import Schedule_Analyzer
from enum import Enum

Init_Type = Enum(
    'Init_Type',
    'NO_INFORMATION RESPONSE_TIMES SCHED_TRACE LET'
)


class DPT:

    def __init__(self, chain, occurrence, init_type):
        self.chain = chain
        self.init_type = init_type

        if init_type == Init_Type.SCHED_TRACE:
            self.schedule = chain.base_ts.schedules['wcet']
            self.ana = Schedule_Analyzer(self.schedule, chain.base_ts.hyperperiod())

        self.occurrences = self.build_tree(0, occurrence)


    # ===== Help functions =====
    def Rmin(self, tsk: Task, idx: int):
        if self.init_type == Init_Type.NO_INFORMATION:
            return tsk.phase + idx * tsk.period
        elif self.init_type == Init_Type.RESPONSE_TIMES:
            return tsk.phase + idx * tsk.period
        elif self.init_type == Init_Type.SCHED_TRACE:
            return self.ana.start(tsk, idx)
        elif self.init_type == Init_Type.LET:
            return tsk.phase + idx * tsk.period


    def Rmax(self, tsk: Task, idx: int):
        if self.init_type == Init_Type.NO_INFORMATION:
            return self.Rmin(tsk, idx) + tsk.period - tsk.wcet
        elif self.init_type == Init_Type.RESPONSE_TIMES:
            return self.Rmin(tsk, idx) + self.chain.base_ts.wcrts[tsk] - tsk.wcet
        elif self.init_type == Init_Type.SCHED_TRACE:
            return self.Rmin(tsk, idx)
        elif self.init_type == Init_Type.LET:
            return self.Rmin(tsk, idx)


    def Dmin(self, tsk: Task, idx: int):
        if self.init_type == Init_Type.NO_INFORMATION:
            return self.Rmin(tsk, idx) + tsk.wcet
        elif self.init_type == Init_Type.RESPONSE_TIMES:
            return self.Rmin(tsk, idx) + tsk.wcet
        elif self.init_type == Init_Type.SCHED_TRACE:
            return self.ana.finish(tsk, idx)
        elif self.init_type == Init_Type.LET:
            return self.Rmin(tsk, idx) + tsk.period


    def Dmax(self, tsk: Task, idx: int):
        if self.init_type == Init_Type.NO_INFORMATION:
            return self.Rmax(tsk, idx + 1) + tsk.wcet
        elif self.init_type == Init_Type.RESPONSE_TIMES:
            return self.Rmax(tsk, idx + 1) + tsk.wcet
        elif self.init_type == Init_Type.SCHED_TRACE:
            return self.ana.finish(tsk, idx + 1)
        elif self.init_type == Init_Type.LET:
            return self.Dmin(tsk, idx) + tsk.period


    def build_tree(self, current_position: int, current_job_idx: int):
        if current_position + 1 >= self.chain.length():
            return [current_job_idx]

        current_task: Task = self.chain[current_position]
        next_task: Task = self.chain[current_position + 1]

        # With this index the below property is safely fulfilled:
        next_job_idx = (
            ceil((self.Dmax(current_task, current_job_idx) - next_task.phase) / next_task.period)
            - 1
        )

        while not self.Rmin(next_task, next_job_idx) < self.Dmax(current_task, current_job_idx):
            next_job_idx = next_job_idx - 1

        next_job_idx = max(next_job_idx, 0)

        # Note that in https://doi.org/10.1016/j.sysarc.2017.09.004 it is not specified what happens if there is no reachable job due to large phase of next_task.
        # We assume that in that case the build_tree function returns a shorter tree than expected.
        if self.Rmin(next_task, next_job_idx) >= self.Dmax(current_task, current_job_idx):
            # No reachable job
            return []

        while self.Rmin(next_task, next_job_idx + 1) < self.Dmax(current_task, current_job_idx):
            next_job_idx = next_job_idx + 1

        return [current_job_idx] + self.build_tree(current_position + 1, next_job_idx)
    
    
    def length(self):
        return len(self.occurrences)


    def age(self):
        return self.Rmax(self.chain[self.length()-1], self.occurrences[self.length()-1]) + self.chain[self.length()-1].wcet - self.Rmin(self.chain[0], self.occurrences[0])


# ===== Analysis =====
def beckerFast(chain: CEChain, init_type):
    hp = chain.hyperperiod()
    max_phase = chain.max_phase()
    ages = []
    ind_job = 0

    while chain[0].period * ind_job <= hp + max_phase:
        tree = DPT(chain, ind_job, init_type)
        if tree.length() == chain.length():
            ages.append(tree.age())
        ind_job = ind_job + 1

    return max(ages)


def beckerFast_NO_INFORMATION(chain):
    return beckerFast(chain, Init_Type.NO_INFORMATION)

def beckerFast_RESPONSE_TIMES(chain):
    return beckerFast(chain, Init_Type.RESPONSE_TIMES)

def beckerFast_SCHED_TRACE(chain):
    return beckerFast(chain, Init_Type.SCHED_TRACE)

def beckerFast_LET(chain):
    return beckerFast(chain, Init_Type.LET)
