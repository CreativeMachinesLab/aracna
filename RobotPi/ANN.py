import sys
import math
from decimal import Decimal

class Link:
	'neural network link object from nodes source to dest'

	def __init__(self, nodeA, nodeB, w):
		self.dest = nodeB
		self.source = nodeA
		self.weight = w

	def set_link(self, nodeA, nodeB, w):
		'''sets the link to nodeA -> nodeB'''
		self.source = nodeA
		self.dest = nodeB
		self.weight = w

	def set_weight(self, w):
		'''sets the link's weight '''
		self.weight = float(w)

	def get_link(self):
		return self.source, " ", self.dest," ", self.weight

	def get_source(self):
		return self.source

	def get_dest(self):
		return self.dest

	def get_weight(self):
		return self.weight
class Node:
	'a neural network node. defiened by id'
	def __init__(self):
		self.id = 0.0
		self.bias = 0.0
		self.activation = 0.0
		self.oldactiv = 0.0
		self.oldactiv2 = 0.0
		self.incom = [] #incoming links. list of type Link objects
		self.activsum = 0.0
		self.output = 0.0

	def __init__(self, nid):
		self.id = int(nid)
		self.activation = 0.0
		self.oldactiv = 0.0
		self.oldactiv2 = 0.0
		self.incom = [] #incoming links. list of type Link objects
		self.activsum = 0.0
		self.output = 0.0

	def __init__(self, nid, bias):
		self.id = int(nid)
		self.bias = float(bias)
		self.activation = 0.0
		self.oldactiv = 0.0		
		self.oldactiv2 = 0.0
		self.incom = [] #incoming links. list of type Link objects
		self.activsum = 0.0
		self.output = 0.0

	def __init__(self, nid, bias, tc):
		self.id = int(nid)
		self.bias = float(bias)
		self.activation = 0.0
		self.oldactiv = 0.0
		self.oldactiv2 = 0.0
		self.timeconst = float(tc)
		self.incom = [] #incoming links. list of type Link objects
		self.activsum = 0.0
		self.output = 0.0

	#GETTERS
	def get_id(self): return self.id
	
	def get_bias(self):	return self.bias

	def get_timeconst(self):	return self.timeconst
	
	def get_oldactiv(self):	return self.oldactiv

	def get_oldactiv2(self):	return self.oldactiv2

	def get_activation(self):	return self.activation

	def get_activsum(self):	return self.activsum

	def	get_output(self): return self.output

	def get_incom(self):	return self.incom

	#SETTERS
	def set_activation(self, val):	
		#self.oldactiv = self.activation
		self.activation = float(val)
	
	def set_oldactiv(self, val):	self.oldactiv = float(val)

	def set_oldactiv2(self, val):	self.oldactiv2 = float(val)

	def set_activsum(self, val):	self.activsum = float(val)

	def set_output(self, val):	self.output = float(val)
	
	def add_incom(self, source, weight):
		self.incom.append( Link(source, self.id, float(weight)))
		#print "add incom to", self.get_id(), " src= ", source, "weight= ", float(weight)


class ANN:
	'a neural network which contains a list of links, source nodes, dest nodes and a hidden layer'
	def __init__(self, aid):
		self.annid = int(aid)
		self.inputs = [] #IDs of input nodes
		self.outputs = [] #IDs of output nodes
		self.hidden = [] #IDs of hidden nodes
		#self.links = [] #list of Link objects
		self.nodes = [] #list of Node objects

	def print_NN(self):
		print "INPUT IDS:"

		for innode in self.inputs:
			print innode

		print "OUTPUT IDS:"
		for outnode in self.outputs:
			print outnode
		
		print "NODES:"
		for node in self.nodes:
			print (node.get_id())
			temp = []
			for lin in node.get_incom():
				print("\t"),
				temp = map(str, lin.get_link())
				print ''.join(temp)


	def add_incoming(self, source, dest, weight):
		'''adds the source node to the destination node's incoming list'''
		for node in self.nodes:
			if (node.get_id() == int(dest)): #if we reached the destination node id
				node.add_incom(int(source), weight)

	def create_network(self, linksfile):
		'''create the neural network structure by:
		   1.reading the input and output nodes from structfile
		   2.reading the links from linksfile'''
		
		try:
		#start reading nodes and links
			input = open(linksfile, "r")
			isnode = True #read nodes first

		#read each line and extract the link values
			for line in input:
				line = line.strip() #strip away leading and trailing whitespace
				arr = line.split(':') #extract components

				if(line == "END"):
					isnode = False
				#reading list of nodes
				elif(isnode):
					#format in file: place, nid, timeconst, bias
					self.nodes.append( Node(arr[1].strip(), arr[3].strip(), arr[2].strip())) # (nid, bias, timeconst) 
					if(arr[0].strip()== "IN"):
						self.inputs.append(int(arr[1].strip()))
					elif(arr[0].strip()== "OUT"):
						self.outputs.append(int(arr[1].strip()))
				else:			
					#links.append( Link(arr[0].strip(), arr[1].strip(), arr[2].strip())) #add link
					self.add_incoming(arr[0].strip(), arr[1].strip(), arr[2].strip())
				'''	nodes in Link are of type Node
					snode = Node(arr[0]) #create a source Node
					dnode = Node(arr[1]) #create a destination Node
					links.append( Link(snode, dnode, arr[3])) '''
		
			input.close()
		except IOError as e:
			print "I/O error in linksfile({0}): {1}".format(e.errno, e.strerror)
		except ValueError as e:
			print "Error reading from linksfile({0}): {1}".format(e.errno, e.strerror)
		except Exception as e:
			print "Unexpected Error reading linksfile:" , sys.exc_info()	


	def find_node(self, nid):
		'''finds node using nid and returns Node object correspoding to that id'''
		for node in self.nodes:
			if(node.get_id() == nid):
				return node

	def is_input(self, nid):
		'''returns true if given node id is an id of an input node'''
		for i in self.inputs:
			if i == nid:
				return True
		return False

	def load_NN(self, vals):
		''' load neural network with activation values stored in 'vals' 
			return output values'''
		print(len(self.inputs))
		if( len(vals) != len(self.inputs)):
			print "incompatible input and vals sizes"
			return nil
		#loop through vals and inputs	

		for i in range(0, len(vals)):
			current = self.find_node(self.inputs[i])
			current.set_oldactiv2(current.get_oldactiv())
			current.set_oldactiv(current.get_activation())
			current.set_activation(vals[i])
			current.set_output(vals[i])

	
	def init_NN(self):
		for node in self.nodes:
			if(not(self.is_input(node.get_id()))):
				node.set_output(sigmoid(node.get_bias(), 1.0))
				#print node.get_output()

	

	def output_NN(self, dt):
		'''propagates values into NN and returns output nodes '''
		#store old activation values
		''' for node in nodes:
			node.set_oldactiv(node.get_activation())'''
		#self.nodes.sort(reverse = True)
		for node in self.nodes:
			if (not(self.is_input(node.get_id()))):
				#print "node", node.get_id()
				inlinks = node.get_incom() #returns Link objects
				activsum = 0.0
				#calculate SUM(wij * sigmoid(bias + oldactiv))
				for inlink in inlinks:
					#print "in in link: ", inlink.get_link()
					source = inlink.get_source() #id of source node
					weight = inlink.get_weight() #link weight
					srcnode = self.find_node(source) #returns source Node object
					activsum += (weight*srcnode.get_output())
					#print "activsum =+ w(", weight, ") * ", srcnode.get_output(), " : ", activsum
				
				node.set_activsum(activsum)
				#print  "nodeid: ", node.get_id(), " activsum = ", node.get_activsum()
				
		delta = 0.0

		for node in self.nodes:
			inlinks = node.get_incom()
			
			if((not self.is_input(node.get_id())) and (len(inlinks) != 0)):
				#print "node ", node.get_id()
	   			oldactiv = node.get_activation()
	   			#print "oldactiv: ", oldactiv
				delta = (dt/node.get_timeconst())* (-node.get_activation() + node.get_activsum())
				#print "nodeid:", node.get_id(), " delta=(" , dt, "/", node.get_timeconst(), ")*(", -oldactiv, "+", node.get_activsum(), ")",  " : ", delta
				node.set_oldactiv2(node.get_oldactiv())
				node.set_oldactiv(oldactiv)
				node.set_activation(oldactiv + delta)
				node.set_output(sigmoid(float(node.get_activation() + node.get_bias()), 1.0))#4.9242730000000003 #1.0
				#print "nodeid:", node.get_id(), "bias + activation = ", (node.get_activation() + node.get_bias())
				#print "nodeid:", node.get_id(), " output = sigmoid(", (node.get_activation() , "+", node.get_bias()),  "): ",node.get_output()  
				if(node.get_output() <0.0):
					node.set_output(0.0)
		
		#store output values in an list to return it	
		output = []	
		for outnode in self.outputs:
			output.append(self.find_node(outnode))
		
		return output
	
	def CTRNN_Controller(self, dt):
		'''similar to the constructor CTRNNController() in biped called first in main'''
		self.init_NN()
		#print "After init_NN()..."
		#for x in self.outputs:
		#	node = self.find_node(x)
		#	print node.get_output()

		nnoutput = []
		#print "running output_NN(.02) 50 times in CTRNN_Controller()..."
		for i in range (0, 50):
			nnoutput = self.output_NN(dt)
			if(i == -6):
				#nnoutput = self.output_NN(dt)
				for n in nnoutput:
					print n.get_output()
				print "After running self.output_NN(", dt, ") ", (i+1), " time" 
	
		return nnoutput

def sigmoid(incoming, slope): 
	'''applies sigmoid function on input and returns the output'''
	try: 
		#print "sigmoid(", incoming, "):", (1/(1+(math.exp(-(slope*incoming)))))
		if (incoming <-227.0)and (slope > 0):
			return 1.0
		val = -(slope*incoming)
		if val < -227.0:
			return 1.0
		return (1/(1+(math.exp(val))))
		
	except Exception as e:
		print "incoming: ", incoming, " slope: ", slope, "\t", e


