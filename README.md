# BVH
Class to work with BVH files. Will read a file, place it into a convinient format, and allow for fast display/playback of the sequence.

NB - two samples files included in this repo from the CMU dataset. Modify the __main__ function accordingly if run as a programme.

BVHData Class - v1.0

Utility class for BVH Files
Written by Darren Cosker 2020

Usage Example:
    <p>bvhFileName = 'Example.bvh'</p>
    <p>bvhObject = BVHData()</p>
    <p>bvhObject.bvhRead(bvhFileName)</p>
    <p>bvhObject.bvhDraw()</p>

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
