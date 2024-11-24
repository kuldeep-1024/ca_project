

**`COMPUTER Architecture`**  
**`CSE511`**

`Project 02 Final-Evaluation`  
**`4x4_Multi-Core_System_Using_MESI_&_VI_Protocol`**

`Contributors:`

`KULDEEP SINGH(2021328)`  
`DAEVAANG KHAIRWAL(2020369)`

`Evaluator:`

`Naorem Akshaykumar`


# for more and better details----- read parsec/FINAL REPORT CA PROJECT.pdf 

**To Build The Gem5 With MESI Protocol:**

Necessary dependency :  
sudo apt install build-essential git m4 scons zlib1g zlib1g-dev libprotobuf-dev protobuf-compiler libprotoc-dev libgoogle-perftools-dev python-dev python

Cloning the gem5:  
git clone [https://github.com/gem5/gem5](https://github.com/gem5/gem5)  
cd gem 5

Building the build with MESI protocol:   
scons defconfig build/X86\_MESI build\_opts/X86  
scons setconfig build/X86\_MESI RUBY\_PROTOCOL\_MESI\_TWO\_LEVEL**\=**y SLICC\_HTML**\=**y  
scons build/X86\_MESI/gem5.opt

**Parsec installation:**

Create a virtual environment :  
virtualenv \-p python3 venv  
source venv/bin/activate

Installing dependencies:  
pip install gem5art-artifact gem5art-run gem5art-tasks	

Make a dir disk-image:   
	cd disk-image/parsec-benchmark  
git clone [https://github.com/cirosantilli/parsec-benchmark.git](https://github.com/darchr/parsec-benchmark.git)

Building m5 :  
	cd gem5/utils/m5/  
	scons build/x86/gem.opt

create file parsec-install.sh

create post-installation.sh

create runscript.sh

Create parsec.json

With this you are ready to create a disk image for x86 parsec

Now,

Install packer:

cd disk-image/  
wget https://releases.hashicorp.com/packer/1.4.3/packer\_1.4.3\_linux\_amd64.zip  
unzip packer\_1.4.3\_linux\_amd64.zip

Now build the disk image with the following commands :

PACKER\_LOG=1 ./packer validate parsec/parsec.json  
PACKER\_LOG=1 ./packer build parsec/parsec.json

**NOTE:The image will be created in the parsec-image folder with the name parsec.** 

**cmd code for**   
**./build/X86\_MESI/gem5.opt ../configuration.py --benchmark swaptions --size simsmall \> /home/daev/Desktop/output.txt**

**./build/X86\_MESI/gem5.opt ../configuration.py --benchmark facesim --size simsmall \> /home/daev/Desktop/output.txt**



# CODE TILL MID EVALUATION

### **1\. Defining the MESITwoLevelCache Class**

This class sets up a two-level MESI (Modified-Exclusive-Shared-Invalid) cache system with L1 and L2 caches and coherence controllers.

class MESITwoLevelCache(RubySystem):

    def \_\_init\_\_(self):

        if buildEnv\['PROTOCOL'\] \!= 'MESI\_Two\_Level':

            fatal("This system assumes MESI\_Two\_Level\!")

        super(MESITwoLevelCache, self).\_\_init\_\_()

        self.\_numL2Caches \= 4

* **Purpose**: Initializes the MESI cache system.  
* **Key Point**: Checks if the protocol is MESI\_Two\_Level; if not, it raises an error.  
* **Attributes**: Sets \_numL2Caches to 4, meaning there are 4 L2 caches.

---

### **2\. Setting up the Cache System and Controllers**

This setup method creates the network and cache controllers, associating them with CPUs and memory.

def setup(self, system, cpus, mem\_ctrls, dma\_ports, iobus):

    self.network \= MyNetwork(self)

    self.number\_of\_virtual\_networks \= 5

    self.controllers \= \\

        \[L1Cache(system, self, cpu, self.\_numL2Caches) for cpu in cpus\] \+ \\

        \[L2Cache(system, self, self.\_numL2Caches) for \_ in range(self.\_numL2Caches)\] \+ \\

        \[DirController(self, system.mem\_ranges, mem\_ctrls)\] \+ \\

        \[DMAController(self) for \_ in range(len(dma\_ports))\]

* **Purpose**: Sets up the network, virtual networks, and controllers.  
* **Components**:  
  * **L1Cache**: Created for each CPU.  
  * **L2Cache**: A list of L2 caches (4 in total).  
  * **DirController**: A directory controller, responsible for maintaining coherence across all L2 caches.  
  * **DMAController**: Direct Memory Access controllers, linked to the dma\_ports.

---

### **3\. L1Cache Class**

Defines the L1 cache controller with separate instruction and data caches.

class L1Cache(L1Cache\_Controller):

    def \_\_init\_\_(self, system, ruby\_system, cpu, num\_l2Caches):

        super(L1Cache, self).\_\_init\_\_()

        self.L1Icache \= RubyCache(size='32kB', assoc='4', start\_index\_bit=block\_size\_bits, is\_icache=True)

        self.L1Dcache \= RubyCache(size='32kB', assoc='4', start\_index\_bit=block\_size\_bits, is\_icache=False)

* **Purpose**: Defines separate instruction (L1Icache) and data (L1Dcache) caches.  
* **Attributes**:  
  * **size**: 32 KB for both instruction and data caches.  
  * **assoc**: 4-way associativity.

---

### **4\. L2Cache Class**

Defines the L2 cache controller with a unified cache for instructions and data.

class L2Cache(L2Cache\_Controller):

    def \_\_init\_\_(self, system, ruby\_system, num\_l2Caches):

        super(L2Cache, self).\_\_init\_\_()

        self.L2cache \= RubyCache(size='256kB', assoc=4, start\_index\_bit=self.getBlockSizeBits(system, num\_l2Caches))

* **Purpose**: Sets up the L2 cache as a unified cache with a larger capacity.  
* 

---

### **5\. Directory Controller (DirController)**

This controller maintains coherence across L2 caches.

class DirController(Directory\_Controller):

    def \_\_init\_\_(self, ruby\_system, ranges, mem\_ctrls):

        if len(mem\_ctrls) \> 1:

            panic("This cache system can only be connected to one mem ctrl")

        super(DirController, self).\_\_init\_\_()

        self.directory \= RubyDirectoryMemory()

        self.memory\_out\_port \= mem\_ctrls\[0\].port

* Directory controller for coherence.

---

### **6\. MyNetwork Class**

This class represents a simple network interconnecting the controllers.

class MyNetwork(SimpleNetwork):

    def connectControllers(self, controllers):

        self.routers \= \[Switch(router\_id=i) for i in range(len(controllers))\]

        self.ext\_links \= \[SimpleExtLink(link\_id=i, ext\_node=c, int\_node=self.routers\[i\]) for i, c in enumerate(controllers)\]

*  Connects all cache controllers via routers and links.

---

### **7\. O3Core Class**

Defining an out-of-order CPU core with branch prediction and reorder buffer (ROB) parameters.

class O3Core(RubySystem):

    def \_\_init\_\_(self, cpu\_id):

        super(O3Core, self).\_\_init\_\_()

        self.cpu \= RiscvO3CPU(cpu\_id=cpu\_id)

        self.cpu.branchPred \= TournamentBP()

        self.cpu.branchPred.localPredictorSize \= 2048

* Configures a single RISC-V out-of-order core.  
* **Branch Predictor**: Uses a tournament predictor for accuracy.**Reorder Buffer (ROB)**: Allows speculative execution.

---

### **8\. System Configuration**

Defining the full system with CPU, memory, and cache configuration.

system \= System()

system.clk\_domain \= SrcClockDomain(clock="1GHz")

system.mem\_ranges \= \[AddrRange("512MB")\]

system.cpu \= \[O3Core(i) for i in range(4)\]

*  Sets up the main system configuration.  
* **Components**:  
  * **Clock**: 1 GHz clock for timing.  
  * **Memory Range**: 512MB.  
  * **CPUs**: Creates four out-of-order cores.

---

### **9\. Setting up Workloads**

Assigning a workload (a simple RISC-V binary) to each CPU.

binary \= os.path.join(thispath, "../../../", "tests/test-progs/hello/bin/RISCV/linux/hello")

process \= Process()

process.cmd \= \[binary\]

for cpu in system.cpu:

    cpu.workload \= process

    cpu.createThreads()

---

### **10\. Running the Simulation**

Initializes the simulation and runs until completion.

root \= Root(full\_system=False, system=system)

m5.instantiate()

exit\_event \= m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit\_event.getCause()}")

Output  
![][image1]  
![][image2]
