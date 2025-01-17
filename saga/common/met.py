from typing import Dict, List, Optional, Hashable 
import networkx as nx
import numpy as np

from ..base import Scheduler, Task
from ..utils.tools import check_instance_simple

class METScheduler(Scheduler):
    def __init__(self, machine_capacities: Dict[Hashable, float]) -> None:
        super().__init__()
        self.machine_availabilities = {machine: 0 for machine in machine_capacities.keys()}  # At start, all machines are available
        self.machine_capacities = machine_capacities

    def schedule(self, network: nx.Graph, task_graph: nx.DiGraph) -> Dict[Hashable, List[Task]]:
        check_instance_simple(network, task_graph)
        assignments = {}

        for task_node in task_graph.nodes:
            # Get execution times for this task on all machines
            execution_times = [(machine_node, network[task_node][machine_node]['weight']) for machine_node in network[task_node].keys()]

            # Sort machines by execution time (ascending)
            execution_times.sort(key=lambda x: x[1])

            # Find the machine with the earliest availability after considering execution time
            min_machine = min(execution_times, key=lambda x: x[1] + self.machine_availabilities[x[0]])[0]

            # The task will start when the machine becomes available
            start_time = self.machine_availabilities[min_machine]

            # The task will end after its duration
            end_time = start_time + task_graph.nodes[task_node]['weight']

            # Create a new Task instance for this task
            task = Task(node=min_machine, name=str(task_node), start=start_time, end=end_time)

            # Update the machine's availability
            self.machine_availabilities[min_machine] = end_time

            # Assign the task to the machine
            if min_machine in assignments:
                assignments[min_machine].append(task)
            else:
                assignments[min_machine] = [task]

        return assignments
