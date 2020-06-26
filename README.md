# BVH
Class to work with BVH files. Although part of larger personal projects, this is intended to be 'helper' code that is clean and simple, so that others can either use the class directly or modify to their needs in an easy manner. Due to this, the code when run is pretty verbose - with lots of 'prints' - so people can see what is going on at different time steps. Of course this makes it slower so remove the prints if used in earnest!

NB - two samples files included in this repo from the CMU dataset.

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
