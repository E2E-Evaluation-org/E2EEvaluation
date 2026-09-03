"""
Analysis from Becker et al. 2017:
Synthesizing Job-Level Dependencies for Automotive Multi-rate Effect Chains.
https://doi.org/10.1016/j.sysarc.2017.09.004
Also used in Becker et al. 2016:
Synthesizing Job-Level Dependencies for Automotive Multi-rate Effect Chains
https://doi.org/10.1109/RTCSA.2016.41
(Analysis presented here is without job-level dependencies)

Implementation is based on a Java implementation provided by Matthias Becker

- implicit
- periodic

(see also the file: BeckerFast.py)
"""


import math
from tasks.task import Task
from tasks.job import Job
from cechains.chain import CEChain
from enum import Enum
from utilities.scheduler import Schedule_Analyzer

Init_Type = Enum(
    'Init_Type',
    'NO_INFORMATION RESPONSE_TIMES SCHED_TRACE LET'
)


class DPT_job(Job):

    def __init__(self, task, occurrence, chain, init_type):
        super().__init__(task, occurrence)

        self.chain = chain

        self.init_type = init_type

        self.rmin = None
        self.rmax = None
        self.dmin = None
        self.dmax = None

        self.start = None
        self.finish = None

        self.next = None

        if init_type == Init_Type.SCHED_TRACE:
            self.schedule = chain.base_ts.schedules['wcet']
            self.ana = Schedule_Analyzer(self.schedule, chain.base_ts.hyperperiod())

        self.reset_intervals()


    
    def reset_intervals(self):
        
        if self.init_type == Init_Type.NO_INFORMATION:
            self.rmin = self.get_release()
            self.rmax = self.get_deadline() - self.task.wcet
            self.dmin = self.get_release() + self.task.wcet
            self.dmax = self.get_deadline() + self.task.period

        elif self.init_type == Init_Type.RESPONSE_TIMES:
            self.rmin = self.get_release()
            self.rmax = self.rmin + self.chain.base_ts.wcrts[self.task] - self.task.wcet
            self.dmin = self.rmin + self.task.wcet
            self.dmax = self.rmin + self.task.period + self.chain.base_ts.wcrts[self.task]

        elif self.init_type == Init_Type.SCHED_TRACE:
            self.rmin = self.ana.start(self.task, self.occurrence)
            self.rmax = self.rmin
            self.dmin = self.ana.finish(self.task, self.occurrence)
            self.dmax = self.ana.finish(self.task, self.occurrence + 1)

        elif self.init_type == Init_Type.LET:
            self.rmin = self.get_release()
            self.rmax = self.rmin
            self.dmin = self.get_release() + self.task.period
            self.dmax = self.dmin + self.task.period
    

    def reset_rmin(self):
        
        if self.init_type == Init_Type.NO_INFORMATION:
            self.rmin = self.get_release()
            self.dmin = self.rmin + self.task.wcet

        elif self.init_type == Init_Type.RESPONSE_TIMES:
            self.rmin = self.get_release()
            self.dmin = self.rmin + self.task.wcet

        elif self.init_type == Init_Type.SCHED_TRACE:
            self.rmin = self.ana.start(self.task, self.occurrence)
            self.dmin = self.ana.finish(self.task, self.occurrence)

        elif self.init_type == Init_Type.LET:
            self.rmin = self.get_release()
            self.dmin = self.dmax


    def push_rmin(self, time):
        if time > self.rmin:
            self.rmin = time
            self.dmin = self.rmin + self.task.wcet


    def produces_data_for(self, successor):
        return successor.rmax >= self.dmin and successor.rmin < self.dmax
    
    def __str__(self):
        return f"task period: {self.task.period}\noccurrence: {self.occurrence}\nrmin: {self.rmin}\nrmax: {self.rmax}\ndmin: {self.dmin}\ndmax: {self.dmax}\nstart: {self.start}\nfinish: {self.finish}\nnext: {self.next}"


class DPT_Vertex:

    def __init__(self, dpt_job):
        self.dpt_job = dpt_job
        self.max_branch_age = None
        self.final_node = False
        self.incomming = []         # list of all incomming edges   [(vertex, valid)]
        self.outgoing = []          # list of all outgoing edges    [(vertex, valid)]
    
    def set_branch_age(self, root_node, init_type):
        if init_type == Init_Type.LET:
            self.max_branch_age = self.dpt_job.dmin - root_node.dpt_job.rmin
        else:
            self.max_branch_age = self.dpt_job.rmax + self.dpt_job.task.wcet - root_node.dpt_job.rmin

    def is_root(self):
        return len(self.incomming) == 0
    
    def is_leaf(self):
        return len(self.outgoing) == 0


class DataPropagationTree:

    def __init__(self, ce_chain, all_jobs, init_type):
        self.chain = ce_chain
        self.init_type = init_type
        self.dpt_jobs = all_jobs
        self.root = None
        self.vertex_list = []

    def initialize_variables(self):
        ...


# helpers

def compute_upper_bound(chain):
        time = 0

        num_inital_jobs = chain.hyperperiod() / chain[0].period   # TODO maybe not chain.hyperperiod() but chain.base_ts.hyperperiod()
        time += (math.floor(num_inital_jobs) - 1) * chain[0].period

        for task in chain:
            time += 2 * task.period

        return time

def get_all_jobs(chain, init_type):
    dpt_jobs = []

    bound = compute_upper_bound(chain)

    for task in chain:

        jobcount = math.floor(bound / task.period)
        for i in range(jobcount):
            dpt_jobs.append(DPT_job(task, i, chain, init_type))

    return dpt_jobs


# Analysis

def analyze_data_age(ce_chain, init_type):
    all_jobs = get_all_jobs(ce_chain, init_type)
    initial_jobs = get_initial_jobs(all_jobs, ce_chain)
    dpts = []
    max_data_age = 0
    #print(len(all_jobs))

    for initial_job in initial_jobs:
        dpt = DataPropagationTree(ce_chain, all_jobs, init_type)
        dpt.root = DPT_Vertex(initial_job)
        dpt.vertex_list.append(dpt.root)
        max_data_age = max(recursive_dpt(dpt, dpt.root, ce_chain, init_type), max_data_age)
        dpts.append(dpt)

    return max_data_age


def recursive_dpt(
    dpt : DataPropagationTree, 
    vertex : DPT_Vertex, 
    chain : CEChain,
    init_type
):
    
    if vertex.dpt_job.task == chain[-1]:
        # end of chain is reached
        
        leaf_node = vertex
        leaf_node.final_node = True
        root_node = dpt.root
        leaf_node.set_branch_age(root_node, init_type)

        data_age = leaf_node.max_branch_age

        ... # maybe something missing here, but reference code looks weird

        return data_age

    current_task_index = chain.index(vertex.dpt_job.task)    
    successor_task = chain[current_task_index+1]
    possible_successors = get_possible_successors(dpt, vertex, successor_task)
    max_data_age = 0.0

    if possible_successors == []:
        return max_data_age

    # simple but effective way to speed up analysis; 
    # original implimentation iterates over all possible successors

    if init_type == Init_Type.NO_INFORMATION:
        # simple but effective way to speed up analysis; 
        # original implementation iterates over all possible successors
        possible_successors = [possible_successors[-1]]


    for successor in possible_successors:
        successor.push_rmin(vertex.dpt_job.dmin)
        v = append_job_to_graph(dpt, vertex, successor)
        assert(v!=None)
        data_age = recursive_dpt(dpt, v, chain, init_type)
        if data_age != None:
            max_data_age = max(data_age, max_data_age)
        successor.reset_rmin()

    return max_data_age


def mark_invalid_edges():
    ...

def get_root(dpt_vertex : DPT_Vertex):
    current_vertex = dpt_vertex
    while not current_vertex.is_root():
        current_vertex = current_vertex.incomming[0][0]
    return current_vertex


def get_possible_successors(dpt : DataPropagationTree, dpt_vertex : DPT_Vertex, successor : Task):
    successors = [job for job in dpt.dpt_jobs if job.task == successor and dpt_vertex.dpt_job.produces_data_for(job)]

    #if successors == []:
        #print(dpt_vertex.dpt_job)
        #print("successor period", successor.period)

    return successors



def get_initial_jobs(all_jobs, chain):
    #last_instance = chain.hyperperiod() / chain[0].period
    initial_jobs = [job for job in all_jobs if job.task == chain[0]]
    return initial_jobs


def append_job_to_graph(dpt : DataPropagationTree, source : DPT_Vertex, destination_job : DPT_job):
    destination = get_vertex(dpt, destination_job)

    # only create a new vertex if there is no vertex with that job in the graph already
    if destination == None:
        destination = DPT_Vertex(destination_job)
        dpt.vertex_list.append(destination)

    if source.outgoing.count((destination, True)) == 0:
        source.outgoing.append((destination, True))

    return destination


# searches the graph for a vertex with the given dpt_job
def get_vertex(dpt : DataPropagationTree, dpt_job : DPT_job):

    vertices = [vertex for vertex in dpt.vertex_list if vertex.dpt_job == dpt_job]

    if len(vertices) == 1:
        return vertices[0]
    elif len(vertices) == 0:
        return None

        

def get_chains():
    ...

def get_jobs():
    ...

def get_source_nodes():
    ...




def becker17_NO_INFORMATION(chain):
    return analyze_data_age(chain, Init_Type.NO_INFORMATION)

def becker17_RESPONSE_TIMES(chain):
    time = analyze_data_age(chain, Init_Type.RESPONSE_TIMES)
    return time

def becker17_SCHED_TRACE(chain):
    return analyze_data_age(chain, Init_Type.SCHED_TRACE)

def becker17_LET(chain):
    return analyze_data_age(chain, Init_Type.LET)
