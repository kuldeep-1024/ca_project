import argparse
import time

import m5
from m5.objects import Root

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import DiskImageResource, KernelResource
from gem5.utils.requires import requires


requires(
    isa_required=ISA.X86,
    coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL,
    kvm_required=False,
)

benchmark_choices = [
    "blackscholes", "bodytrack", "canneal", "dedup", "facesim", "ferret", 
    "fluidanimate", "freqmine", "raytrace", "streamcluster", "swaptions", 
    "vips", "x264"
]

size_choices = ["simsmall", "simmedium", "simlarge"]

parser = argparse.ArgumentParser(
    description="An example configuration script to run the npb benchmarks."
)

parser.add_argument(
    "--benchmark",
    type=str,
    required=True,
    help="Input the benchmark program to execute.",
    choices=benchmark_choices,
)

parser.add_argument(
    "--size",
    type=str,
    required=True,
    help="Simulation size the benchmark program.",
    choices=size_choices,
)
args = parser.parse_args()


from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)

cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="32kB",
    l1d_assoc=4,
    l1i_size="32kB",
    l1i_assoc=4,
    l2_size="256kB",
    l2_assoc=4,
    num_l2_banks=2,

)


memory = DualChannelDDR4_2400(size="3GB")


processor = SimpleProcessor(isa=ISA.X86, cpu_type=CPUTypes.O3, num_cores=4)


board = X86Board(
    clk_freq="3GHz", 
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

command = (
    f"cd /home/gem5/parsec-benchmark;"
    + "source env.sh;"
    + f"parsecmgmt -a run -p {args.benchmark} -c gcc-hooks -i {args.size} -n 2;"
    + "sleep 5;"
    + "m5 exit;"
)

local_kernel_path = "/home/daev/Desktop/ca project/parsec/linux-stable/vmlinux-4.19.83" 
local_disk_image_path = "/home/daev/Desktop/ca project/parsec/disk-image/parsec/parsec-image/parsec"

board.set_kernel_disk_workload(
    kernel=KernelResource(local_path=local_kernel_path),  
    disk_image=DiskImageResource(local_path=local_disk_image_path),  
    readfile_contents=command,
)


def handle_workbegin():
    print("Done booting Linux")
    print("Resetting stats at the start of ROI!")
    m5.stats.reset()
    processor.switch()
    yield False


def handle_workend():
    print("Dump stats at the end of the ROI!")
    m5.stats.dump()
    yield True


simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.WORKBEGIN: handle_workbegin(),
        ExitEvent.WORKEND: handle_workend(),
    },
)

globalStart = time.time()

print("Running the simulation")
print("Using O3 CPU")

m5.stats.reset()

simulator.run()

print("All simulation events were successful.")

print("Done with the simulation")
print()
print("Performance statistics:")

print("Simulated time in ROI: " + (str(simulator.get_roi_ticks()[0])))
print(
    "Ran a total of", simulator.get_current_tick() / 1e12, "simulated seconds"
)
print(
    "Total wallclock time: %.2fs, %.2f min"
    % (time.time() - globalStart, (time.time() - globalStart) / 60)
)

