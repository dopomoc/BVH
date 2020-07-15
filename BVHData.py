'''
BVHData Class - v1.0

Utility class for BVH Files
Written by Darren Cosker 2020

Usage Example:
    bvhFileName = 'Example.bvh'
    bvhObject = BVHData()
    bvhObject.bvhRead(bvhFileName)
    bvhObject.bvhDraw()

The rootNode then starts the hierarchy of joints/nodes with associated data:
    - Children (list of Nodes)
    - Num channels for this node
    - Names of channels in the node
    - Animation data for the channel
    - Offset for the joint
    - Name of the joint
    - Transformation matrix for the joint
    - Joint coordinates
    
Other notes:
    - Will read a BVH file into a hierarchical format
    - Will store animation sequences for joints in place in a np array
    - Of course, to understand this code you have to first understand how a 
    - BVH file is constructed. I would start with these excellent resources:
        https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/BVH.html
        http://www.dcs.shef.ac.uk/intranet/research/public/resmes/CS0111.pdf
'''

import numpy as np
import sys
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import math
import time
import matplotlib.animation as animation

class Node:
    
    def __init__(self):
        self.childNodes = []
        self.numChannels = 0
        self.channelNames = []
        self.animation = [] # this is rotation information for joints
        self.offset = []
        self.name = "Joint Name"   
        self.transMats = []           
        self.jointCoords = []

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
        self.animationPreview = []
        self.totalJoints = 0
        self.plotMinMax = []
        self.jointPlots = []
        self.bonePlots = []
        
    
    def bvhRead(self, bvhFileName):
        
        '''
        # Open BVH file and read the MOTION first then the HIERARCHY.
        # I'm doing this so that when I create the Node hierarchy I can store the
        # motion data for a Node on the fly in the first pass (and not have to DFS)
        # the hierarchy again later, adding the MOTION data.
        
        '''
        print('Reading BVH File..', bvhFileName)
        
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
            
                # What order is the rotation in? Re-order animation data to X, Y, Z if required
                xRotPos = rootNode.channelNames.index('Xrotation')
                yRotPos = rootNode.channelNames.index('Yrotation')
                zRotPos = rootNode.channelNames.index('Zrotation')                
            
                # Make transformation matrix for this node
                for frame in range(self.totalFrames):
                    #rootNode.transMats.append(self.makeTransMat(rootNode.animation[frame,3:], rootNode.animation[frame,0:3]))
                    newRot = [rootNode.animation[frame,xRotPos], rootNode.animation[frame,yRotPos], rootNode.animation[frame,zRotPos] ]
                    rootNode.transMats.append(self.makeTransMat(newRot, rootNode.animation[frame,0:3]))
                    thisMat = rootNode.transMats[frame]
                    rootNode.jointCoords.append([thisMat[0,3],thisMat[1,3],thisMat[2,3]])
            
                # Associate this with main root of the BVH class
                self.root = rootNode
                self.totalJoints += 1
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
        
        #return rootNode
        
            
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
    
        # What order is the rotation in? Re-order animation data to X, Y, Z if required
        xRotPos = jointNode.channelNames.index('Xrotation')
        yRotPos = jointNode.channelNames.index('Yrotation')
        zRotPos = jointNode.channelNames.index('Zrotation')
    
        # Make transformation matrices for this node (mult by parent transMat)
        for frame in range(self.totalFrames):
            parentTrans = self.nodeStack[-1].transMats[frame]             
            
            newRot = [jointNode.animation[frame,xRotPos], jointNode.animation[frame,yRotPos], jointNode.animation[frame,zRotPos] ]
            
            if jointNode.numChannels==3:
                # There is no additional translation of the bone, so just use offset for translation
                #jointNode.transMats.append(np.matmul(parentTrans,self.makeTransMat(jointNode.animation[frame,0:3], jointNode.offset)))   
                jointNode.transMats.append(np.matmul(parentTrans,self.makeTransMat(newRot, jointNode.offset)))                   
                
            else:
                # There is an additional translation of the bone, so just offset + the translation
                newTrans = [jointNode.offset[i] + jointNode.animation[frame][i] for i in range(len(jointNode.offset))]
                #jointNode.transMats.append(self.makeTransMat(jointNode.animation[frame,3:], newTrans))
                #jointNode.transMats.append(np.matmul(parentTrans,self.makeTransMat(jointNode.animation[frame,3:],newTrans)))   
                jointNode.transMats.append(np.matmul(parentTrans,self.makeTransMat(newRot,newTrans)))   
            
            
            thisMat = jointNode.transMats[-1]
            jointNode.jointCoords.append([thisMat[0,3],thisMat[1,3],thisMat[2,3]])             
        
        # Make this joint a child of whatever is top of the stack
        self.nodeStack[-1].childNodes.append(jointNode)    
        self.totalJoints += 1
        
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
    
        # Make transformation matrices for this node (mult by parent transMat)
        for frame in range(self.totalFrames):
            parentTrans = self.nodeStack[-1].transMats[frame]             
            endNode.transMats.append(np.matmul(parentTrans,self.makeTransMat([0,0,0], endNode.offset)))            
            thisMat = endNode.transMats[-1]
            endNode.jointCoords.append([thisMat[0,3],thisMat[1,3],thisMat[2,3]]) 
    
        # Make this joint a child of whatever is top of the stack
        self.nodeStack[-1].childNodes.append(endNode)    
        self.totalJoints += 1
    
        return endNode

    def makeRotMat(self, axisAngles):
        
        # Make a composite rotation matrix from axis angles x,y,z
        Rx = np.zeros((3,3))
        Ry = np.zeros((3,3))
        Rz = np.zeros((3,3))
        
        xRad = math.radians(axisAngles[0])
        yRad = math.radians(axisAngles[1])
        zRad = math.radians(axisAngles[2])
        
        Rx[0,0] = 1
        Rx[1,1] = math.cos(xRad)
        Rx[1,2] = - math.sin(xRad)
        Rx[2,1] = math.sin(xRad)
        Rx[2,2] = math.cos(xRad)
        
        Ry[0,0] = math.cos(yRad)
        Ry[0,2] = math.sin(yRad)
        Ry[1,1] = 1
        Ry[2,0] = - math.sin(yRad)
        Ry[2,2] = math.cos(yRad)
        
        Rz[0,0] = math.cos(zRad)
        Rz[0,1] = - math.sin(zRad)
        Rz[1,0] = math.sin(zRad)
        Rz[1,1] = math.cos(zRad)
        Rz[2,2] = 1        
        
        return np.matmul(Rx,np.matmul(Ry,Rz))

    def makeTransMat(self, axisAngles, transOffsets):
                
        # Make a composite rotation matrix from axis angles x,y,z
        Rx = np.zeros((3,3))
        Ry = np.zeros((3,3))
        Rz = np.zeros((3,3))
        transform = np.zeros((4,4))
        
        xRad = math.radians(axisAngles[0])
        yRad = math.radians(axisAngles[1])
        zRad = math.radians(axisAngles[2])
        
        Rx[0,0] = 1
        Rx[1,1] = math.cos(xRad)
        Rx[1,2] = - math.sin(xRad)
        Rx[2,1] = math.sin(xRad)
        Rx[2,2] = math.cos(xRad)
        
        Ry[0,0] = math.cos(yRad)
        Ry[0,2] = math.sin(yRad)
        Ry[1,1] = 1
        Ry[2,0] = - math.sin(yRad)
        Ry[2,2] = math.cos(yRad)
        
        Rz[0,0] = math.cos(zRad)
        Rz[0,1] = - math.sin(zRad)
        Rz[1,0] = math.sin(zRad)
        Rz[1,1] = math.cos(zRad)
        Rz[2,2] = 1        
        
        transform[:3,:3] = np.matmul(Rx,np.matmul(Ry,Rz))
        transform[3,3] = 1    
        transform[0:3,3] = transOffsets
        
        return transform
    

    def bvhDraw(self, frameStep=1):
        '''
        # Draw BVH file:
        #
        #   frameStep - for large fps files (>200?) rendering can slow a little so sometimes might be 
        #               useful to have a frameStep parameter
        #
        # First, pre-calculate the joints/bones and place them in a list by recursively 
        # moving through the hiererachy. This is as opposed to estimating 3D positions
        # from the hierarchy for each frame and printing. 
        # Once in a suitable format, FuncAnimation can be used for fast rendering.
        '''
                
        rootNode = self.root
        frame = 0
        frameStart = 0
        frameEnd = self.totalFrames                
        
        # Recursively read the Nodes from the BVH Object and store parent to children connections creating a bone list.
        # This makes for easier drawing
        for frame in range(frameStart,frameEnd,frameStep):
                        
            currentJointCoords = rootNode.jointCoords[frame]            
        
            # If there are children to the root, then start recursion to read the hierarchy
            if len(rootNode.childNodes) > 0:
                for i in range(len(rootNode.childNodes)):                    
                    self.preCalculateBone(rootNode.childNodes[i], currentJointCoords, frame)               
        
        # Get min and max values for x, y and z axis
        minX, maxX, minY, maxY, minZ, maxZ = 0,0,0,0,0,0
        allX, allY, allZ = [],[],[]
        
        for iter in range(len(self.animationPreview)):
            thisBone = self.animationPreview[iter]
            for inner in range(2):
                allX.append(thisBone[0][inner])
                allY.append(thisBone[1][inner])
                allZ.append(thisBone[2][inner])
        
        minX = min(allX)
        maxX = max(allX)
        minY = min(allY)
        maxY = max(allY)
        minZ = min(allZ)
        maxZ = max(allZ)
           
        print('Drawing BVH..')
        self.fig = plt.figure()
        
        # NB swapping Y and Z as Y is up and not Z
        self.ax = self.fig.add_subplot(projection="3d",xlim=(minX, maxX), ylim=(minZ, maxZ), zLim=(minY,maxY))
                     
        # Create plot objects per bone that can be updated with data in the drawSkeleton func (via FuncAnimation)
        # This makes for super fast rendering
        for jointNum in range(self.totalJoints):
            # 3D plots can't contain empty arrays - so have to initialise
            self.jointPlots.append(self.ax.plot3D([0,0],[0,0],[0,0],'blue'))
            self.bonePlots.append(self.ax.plot3D([0,0],[0,0],[0,0],'ro'))
        
        self.ani = animation.FuncAnimation(self.fig, self.drawSkeleton, interval=1, repeat=False)
        plt.show()



    def drawSkeleton(self, frame):
        
        if frame> len(self.animationPreview):
            self.ani.event_source.stop()
            
        for jointNum in range(self.totalJoints):
                
            thisJoint = self.animationPreview[(frame*self.totalJoints) + jointNum]                
            
            # NB there is no .set_data() for 3 dimensional data. So have to update
            # x and y using .set_data() and then z using set_3d_properties
            self.jointPlots[jointNum][0].set_data(thisJoint[0],thisJoint[2])
            self.jointPlots[jointNum][0].set_3d_properties(thisJoint[1])
            self.bonePlots[jointNum][0].set_data(thisJoint[0],thisJoint[2])
            self.bonePlots[jointNum][0].set_3d_properties(thisJoint[1])

    def preCalculateBone(self, currentNode, lastJointCoords, frame):        
        
        # Put all the bones in a list recursively to make drawing easier
        # While there are children to process, do one, then recurse to process further down the hierarchy
        if len(currentNode.childNodes) > 0:
                       
            currentJoint = currentNode.jointCoords[frame]   
            self.animationPreview.append([[lastJointCoords[0],currentJoint[0]],[lastJointCoords[1],currentJoint[1]],[lastJointCoords[2],currentJoint[2]]])            
        
            for i in range(len(currentNode.childNodes)):
                self.preCalculateBone(currentNode.childNodes[i], currentJoint, frame)
            else:
                return
        else:            
            currentJoint = currentNode.jointCoords[frame]
            self.animationPreview.append([[lastJointCoords[0],currentJoint[0]],[lastJointCoords[1],currentJoint[1]],[lastJointCoords[2],currentJoint[2]]])            
            
        

if __name__ == '__main__':
    print('BVHData \'main\' is running the default demo..')
    print('Run as a program, this will run through basic usage.')
    print('System inputs', sys.argv)

    # Default file to load for demo
    #bvhFileName = 'skeleton.bvh'
    bvhFileName = 'MartinFreestyle.bvh'
    bvhObject = BVHData()
    bvhObject.bvhRead(bvhFileName)
    bvhObject.bvhDraw(1) #takes frameStep parameter
    
