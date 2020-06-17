'''
BVHData Class - v1.0

Utility class for BVH Files
Written by Darren Cosker 2020

Usage Example:
    bvhFileName = 'Example.bvh'
    bvhObject = BVHData()
    rootNode = bvhObject.bvhRead(bvhFileName)

The rootNode then starts the hierarchy of joints/nodes with associated data:
    - Children (list of Nodes)
    - Num channels for this node
    - Names of channels in the node
    - Animation data for the channel
    - Offset for the joint
    - Name of the joint
    
Other notes:
    - Will read a BVH file into a hierarchical format
    - Will store animation sequences for joints in place in a np array
    - Of course, to understand this code you have to first understand how a 
    - BVH file is constructed. I start with these excellent resources:
        https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/BVH.html
        http://www.dcs.shef.ac.uk/intranet/research/public/resmes/CS0111.pdf
'''

import numpy as np
import sys


class Node:
    
    def __init__(self):
        self.childNodes = []
        self.numChannels = 0
        self.channelNames = []
        self.animation = []
        self.offset = []
        self.name = "Joint Name"              

class BVHData:

    def __init__(self, bvhFileName = 'Empty'):
        self.root = Node()
        self.lineIter=0
        self.allLines = []
        self.nodeStack = []
        self.allMotion = []
        self.channelTicker = 0 
        self.totalFrames = 0
        self.fileName = bvhFileName
        self.frameTime = 0
    
    def bvhRead(self, bvhFileName):
        print('Reading BVH File..', bvhFileName)
       
        # Open BVH file and read the MOTION first then the HIERARCHY.
        # I'm doing this so that when I create the Node hierarchy I can store the
        # motion data for a Node on the fly in the first pass (and not have to DFS)
        # the hierarchy again later, adding the MOTION data.

        bvhFile = open(bvhFileName)
                      
        self.allLines = bvhFile.read().split("\n") # Split each line by \n
        numLines = len(self.allLines) 
        nodeCount = 0        


        ##############################################
        # Read MOTION into a numpy array
        findFRAMEStart = 0 # just a little pointer to where the FRAME/animation data starts
        for motionIter in range(numLines-1):
            line = self.allLines[motionIter].split()
            
            if(line[0]=='MOTION'): 
                findFRAMEStart = motionIter
            
        # Read MOTION header information
        motionIter = findFRAMEStart
        motionIter += 1
            
        line = self.allLines[motionIter].split()
        motionIter += 1
        self.totalFrames = int(line[1])
           
        line = self.allLines[motionIter].split()
        motionIter += 1
        self.frameTime = float(line[2])
        motionIter += 1
    
        # Initialise a np array of zeros for the motion data so we can slice it 
        # nicely later when reading the hierarchy and add it to each node on the fly
        self.allMotion = np.zeros((self.totalFrames,len(self.allLines[motionIter].split())))
        print('Shape of MOTION', np.shape(self.allMotion))
        counter = 0
    
        while(motionIter < numLines-1):
            line = self.allLines[motionIter].split()    
            self.allMotion[counter,:] = line # stack the lines nicely into the array
            motionIter += 1
            counter += 1
        
        #############################################
        # Read HIERARCHY into a Node hierarchy
        # Push (append) JOINTS (and End Site) to a stack. When you see a }, then Pop joints off.
        # Always add a new Node as a child to whatever is currently top of the stack.
        
        # Get current line and split into 'words'
        self.lineIter = 0 
        line = self.allLines[self.lineIter].split()
    
        while(line[0]!='MOTION'):
        
            # Get current line and split into 'words'
            line = self.allLines[self.lineIter].split()
        
            if line[0] == "ROOT":
                nodeCount += 1
                print('ROOT', self.lineIter, 'Count', nodeCount)
                # Get root data
                rootNode = Node()
                self.nodeStack.append(rootNode) # Push to top of stack
                        
                rootNode.name = line[1]
                self.lineIter += 2 # Skip the {
                line = self.allLines[self.lineIter].split()
            
                rootNode.offset = [float(line[1]), float(line[2]), float(line[3])]
                self.lineIter += 1
                line = self.allLines[self.lineIter].split()
            
                rootNode.numChannels = int(line[1])
                for i in range(2, rootNode.numChannels+2): # +2 because have CHANNEL Num then vals
                    rootNode.channelNames.append(line[i])
            
                # Slice through the MOTION array getting animation data for the root
                rootNode.animation = self.allMotion[:,self.channelTicker:self.channelTicker + rootNode.numChannels]
                self.channelTicker += rootNode.numChannels
            
                # Associate this with main root of the BVH class
                self.root = rootNode
                
                # End root data - ok, so JOINT's start next
            
            if line[0] == "JOINT":
                nodeCount += 1
                print('JOINT', line[1], 'Line', self.lineIter, 'Count', nodeCount)
                # Create a joint and add it to the top of the stack.
                # Increment global lineIter as we go so we are 
                # in the right place in the BVH file all the time for any call
                self.nodeStack.append(self.addJoint())
            
            if line[0] == "End":
                
                # Create an end node
                nodeCount += 1
                print('JOINT (End Site)', self.lineIter, 'Count', nodeCount)
                self.nodeStack.append(self.addEndSite())
        
            if line[0] == "}":
        
                if(self.nodeStack):
                    # Pop the stack, so that new children are added to the correct node
                    nodeCount -= 1
                    print('Pop Joint - Count', nodeCount)
                    self.nodeStack.pop()
                else:
                    print('Stack empty')
                    print(self.nodeStack)
    
            self.lineIter += 1
        
        return rootNode
        
            
    def addJoint(self):        
        
        # Read JOINT NAME, OFFSET, CHANNEL  and Animation for this joint
        jointNode = Node()
        line = self.allLines[self.lineIter].split()
    
        jointNode.name = line[1]
        self.lineIter += 2 # Skip the {
        line = self.allLines[self.lineIter].split()
            
        jointNode.offset = [float(line[1]), float(line[2]), float(line[3])]
        self.lineIter += 1
        line = self.allLines[self.lineIter].split()
            
        jointNode.numChannels = int(line[1])
        for i in range(2,jointNode.numChannels+2): # +2 because have CHANNEL Num then vals
            jointNode.channelNames.append(line[i])
        
        # Slice through the MOTION array getting animation data for this joint
        jointNode.animation = self.allMotion[:,self.channelTicker:self.channelTicker + jointNode.numChannels]
        self.channelTicker += jointNode.numChannels    
        
        # Make this joint a child of whatever is top of the stack
        self.nodeStack[-1].childNodes.append(jointNode)    
   
        return jointNode

    def addEndSite(self):
    
        # Read JOINT NAME, OFFSET, CHANNEL  and Animation for this joint
        endNode = Node()
        endNode.name = "End Site"
        endNode.numChannels = 0
        
        self.lineIter += 2 # Skip the {
        line = self.allLines[self.lineIter].split() #line is not global, so read again from allLines (which *is* global)
        endNode.offset = [float(line[1]), float(line[2]), float(line[3])]
        
        # Slice through the MOTION array getting animation data for this joint
        endNode.animation = self.allMotion[:,self.channelTicker:self.channelTicker + endNode.numChannels]
        self.channelTicker += endNode.numChannels 
    
        # Make this joint a child of whatever is top of the stack
        self.nodeStack[-1].childNodes.append(endNode)    
    
        return endNode



if __name__ == '__main__':
    print('BVHData \'main\' is running the default demo..')
    print('Run as a program, this will run through basic usage.')
    print('System inputs', sys.argv)

    # Default file to load for demo
    bvhFileName = 'MartinFreestyle.bvh'
    bvhObject = BVHData()
    rootNode = bvhObject.bvhRead(bvhFileName)
    
    
    