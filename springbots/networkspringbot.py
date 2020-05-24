"""
This module extends the Springbot class to alow
its objects to be sent via xmlrpc or other methods over
network by translating(two ways) the object itself to a simpler
structure based on dictionary and tuples.
"""

from .springbot import Springbot
from .gear import Spring, Node
import exceptions

#
# NetworkSpringbot class
#
class NetworkSpringbot(Springbot):
    """
    Extends evolvable springbot to add marshal and unmarshal methods to
    send more easily through network like xmlrpc
    """

    def marshal(self):
        """
        Transforms the springbot into a dictionary
        """
        springbot_d = {}
        for key, value in self._info.items():
            springbot_d[key] = value

        springbot_d['nodes'] = tuple({'id': node.id,
                'pos' : (node.pos.x, node.pos.y),
                'vel': (node.vel.x, node.vel.y),
                'acc': (node.acc.x, node.acc.y)} for node in self.nodes)

        springbot_d['springs'] = tuple({'from': spring.a.id, 'to': spring.b.id,
                        'amplitude': spring.amplitude, 'offset': spring.offset,
                        'normal': spring.normal} for spring in self.springs)

        return springbot_d


    def unmarshal(self, dic):
        """
        Reads a dictionary into this springbot
        """
        self.nodes = []
        self.springs = []

        for node_d in dic['nodes']:
            newnode = Node(node_d['pos'], node_d['vel'], node_d['acc'])
            newnode.id = node_d['id']
            self.nodes.append(newnode)

        for spring_d in dic['springs']:
            id_a = spring_d['from']
            id_b = spring_d['to']

            for node in self.nodes:
                if node.id == id_a:
                    a = node
                    break
            else:
                raise exceptions.IndexError("node id %d(from) not found\n" % (id_a))

            # Procura id B
            for node in self.nodes:
                if node.id == id_b:
                    b = node
                    break
            else:
                raise exceptions.IndexError("node id %d(to) not found\n" % (id_b))

            self.springs.append(Spring(a, b, spring_d['amplitude'], spring_d['offset'], spring_d['normal']))

        del dic['nodes']
        del dic['springs']
        self._info = dict(dic)

        return self
