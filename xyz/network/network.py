#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-09-03 11:15:09
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-03 21:24:34
'''

class Network:
    """A class method for creating a network .
    """
    def __init__(self):

        self.__top_module = ""
        self.__inputs = set()
        self.__outputs = set()
        self.__nodes = set()
        self.__register_inputs = set()
        self.__register_outputs = set()
        self.__ro_to_ri: dict = {}

        # __signals is a list of all the __nodes in the network in the topological order
        # this is private and should not be modified directly
        self.__signals = []

        self.__const0 = set()
        self.__const1 = set()

        # node fanins return the set of fanins of a node
        #  - note that only __nodes can be looked up in this dictionary
        #  - __signals are not safe when directly looked up
        self.__node_fanins: dict = {}
        self.__node_funcs: dict = {}

        self.__node_fanouts: dict = {}

        self.__submodules = {}
        
    def get_name(self):
        """Returns name of the module .

        :return: [description]
        :rtype: [type]
        """
        return self.__top_module
    
    def set_name(self, name: str):
        """AI is creating summary for set_name

        :param name: [description]
        :type name: str
        """
        self.__top_module = name
        
    def get_func(self, node: str):
        """Returns the function func for the given node

        :param node: [description]
        :type node: str
        :return: [description]
        :rtype: [type]
        """
        return self.__node_funcs[node]
        
    def ro_to_ris(self):
        """Returns a dictionary mapping from ro to 

        :return: [description]
        :rtype: [type]
        """
        return self.__ro_to_ri

    def is_po(self, signal: str) -> bool:
        """Returns True if signal is a POINT .

        :param signal: [description]
        :type signal: str
        :return: [description]
        :rtype: bool
        """
        return signal in self.__outputs

    def is_pi(self, signal: str) -> bool:
        """Returns True if signal is a valid signal .

        :param signal: [description]
        :type signal: str
        :return: [description]
        :rtype: bool
        """
        return signal in self.__inputs

    def is_ro(self, signal: str) -> bool:
        """Returns True if signal is a RPC signal .

        :param signal: [description]
        :type signal: str
        :return: [description]
        :rtype: bool
        """
        return signal in self.__register_outputs

    def is_ri(self, signal: str) -> bool:
        """Returns True if signal is a RRI .

        :param signal: [description]
        :type signal: str
        :return: [description]
        :rtype: bool
        """
        return signal in self.__register_inputs

    def num_nodes(self) -> int:
        """Returns the number of nodes in the graph .

        :return: [description]
        :rtype: int
        """
        return len(self.__nodes)

    def num_latch(self) -> int:
        """AI is creating summary for num_latch

        :return: [description]
        :rtype: int
        """
        return len(self.__register_outputs)

    def num_pis(self) -> int:
        """Returns the number of pis in the network .

        :return: [description]
        :rtype: int
        """
        return len(self.__inputs)

    def num_pos(self) -> int:
        """The number of outputs in the model .

        :return: [description]
        :rtype: int
        """
        return len(self.__outputs)

    # the CO (combinational __outputs are the primary __outputs and the register inupts)
    def is_co(self, signal: str) -> bool:
        """Returns True if signal is a co - op code .

        :param signal: [description]
        :type signal: str
        :return: [description]
        :rtype: bool
        """
        return signal in self.__outputs or signal in self.__register_inputs

    # the CI (combinational inptus are the primary __inputs and the register __outputs)
    def is_ci(self, signal: str) -> bool:
        """Returns True if signal is a combinational input .

        :param signal: [description]
        :type signal: str
        :return: [description]
        :rtype: bool
        """
        return (
            signal in self.__inputs
            or signal in self.__register_outputs
            or signal in self.__const0
            or signal in self.__const1
        )

    def topological_traversal(self) -> set:
        """The topological traversal set of signals in the graph .

        :return: [description]
        :rtype: set
        """
        return self.__signals

    def constants(self):
        """Returns a list of all constant constants .

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__const0 | self.__const1)

    def cos(self):
        """The list of all outputs .

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__outputs | self.__register_inputs)

    def cis(self):
        """Returns a list of all the combinational inputs.

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__inputs | self.__register_outputs | self.__const0 | self.__const1)

    def constant0s(self):
        """Returns a list of constant 0s .

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__const0)

    def constant1s(self):
        """The list of constant 1s .

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__const1)

    def pis(self) -> list:
        """The list of pis in the order of the PIs .

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__inputs)

    def pos(self):
        """Returns a sorted list of all outputs in the order they are sorted .

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__outputs)

    def ris(self):
        """The list of register inputs sorted by the receiver .

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__register_inputs)

    def ros(self):
        """The list of RRS outputs sorted by register outputs .

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__register_outputs)

    def fanins(self, signal: str):
        """Returns a list of the fanins of a specified signal .

        :param signal: [description]
        :type signal: str
        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__node_fanins[signal])
    
    def get_nodes(self):
        """Get the list of nodes sorted by their indices .

        :return: [description]
        :rtype: [type]
        """
        return sorted(self.__nodes)

    # sort __signals in a topological order
    # TODO: support runtime modification and maintain the topogical order
    def traverse(self):
        """Traverse the CIS .
        """
        self.__signals = []
        for signal in self.cis():
            assert signal not in self.__signals
            self.__signals.append(signal)


        for signal in self.cos():
            self.trav_rec(signal)

        for signal in self.__signals:
            self.__node_fanouts[signal] = set()

        # prepare fanouts: this should be recomputed after each network modification
        for signal in self.__signals:
            if signal in self.__node_fanins:
                for f in self.fanins(signal):
                    self.__node_fanouts[f].add(signal)

    # topological traversal, used to sort the __signals in a topological order
    def trav_rec(self, signal: str, pending_signals: set = set()):
        """recursive recursion recursively

        :param signal: [description]
        :type signal: str
        :param pending_signals: [description], defaults to set()
        :type pending_signals: set, optional
        """
        if signal in self.__signals:
            return
        
        if signal not in self.__node_fanins:
            print(f"recursion stoped at node {signal}")
            exit()

        pending_signals.add(signal)

        for f in self.fanins(signal):
            assert f != signal, f"node {signal} is its own fanin"
            if f not in self.__signals:
                if f in pending_signals:
                    # we have a loop
                    # print(f"recursion stoped at node {signal}")
                    # print(f"pending signals: {pending_signals}")
                    return
                self.trav_rec(f)

        pending_signals.remove(signal)
        self.__signals.append(signal)

    def num_fanouts(self, signal: str):
        """Returns the number of fanouts in the node .

        :param signal: [description]
        :type signal: str
        :return: [description]
        :rtype: [type]
        """
        return len(self.__node_fanouts[signal])

    #
    # graph modifications
    #
    def create_pi(self, name: str):
        """Create a input with the given name .

        :param name: [description]
        :type name: str
        """
        assert name not in self.__inputs and "the input to create already exists"
        self.__inputs.add(name)

    def create_po(self, name: str):
        """Create a new output .

        :param name: [description]
        :type name: str
        """
        assert name not in self.__outputs and "the output to create already exists"
        self.__outputs.add(name)

    def create_ri(self, name: str):
        """Create a new RRI input

        :param name: [description]
        :type name: str
        """
        assert (
            name not in self.__register_inputs
            and "the register input to create already exists"
        )
        self.__register_inputs.add(name)

    def create_ro(self, name: str):
        """Create a new register output with the given name .

        :param name: [description]
        :type name: str
        """
        assert (
            name not in self.__register_outputs
            and "the register output to create already exists"
        )
        self.__register_outputs.add(name)

    def create_node(self, name: str, fanins: set, func: list):
        """Create a new node with the given name, fanins and function .

        :param name: [description]
        :type name: str
        :param fanins: [description]
        :type fanins: set
        :param func: [description]
        :type func: list
        """
        assert name not in self.__nodes and "the node to create already exists"
        self.__nodes.add(name)
        self.__node_fanins[name] = set(list(fanins)[:])  # deep copy
        self.__node_funcs[name] = func[:]  # deep copy
        self.__node_fanouts[name] = set()

    def create_and(self, f1: str, f2: str, name: str):
        """Create and connect a node with f1 and f2 .

        :param f1: [description]
        :type f1: str
        :param f2: [description]
        :type f2: str
        :param name: [description]
        :type name: str
        """
        self.create_node(name=name, fanins=set([f1, f2]), func=["11 1"])

    def create_or(self, f1: str, f2: str, name: str):
        """Create or update a node with a or - 1 .

        :param f1: [description]
        :type f1: str
        :param f2: [description]
        :type f2: str
        :param name: [description]
        :type name: str
        """
        self.create_node(name=name, fanins=set([f1, f2]), func=["1- 1", "-1 1"])

    def create_buf(self, fin: str, fout: str):
        """create a buffer for writing fout

        :param fin: [description]
        :type fin: str
        :param fout: [description]
        :type fout: str
        """
        self.create_node(name=fout, fanins=set([fin]), func=["1 1"])

    def create_latch(self, ri: str, ro: str):
        """Creates a Latch with the given RAP and R .

        :param ri: [description]
        :type ri: str
        :param ro: [description]
        :type ro: str
        """
        self.__register_inputs.add(ri)
        self.__register_outputs.add(ro)
        self.__ro_to_ri[ro] = ri
