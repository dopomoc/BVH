# BVH
Class to work with BVH files. Will read a file, place it into a convinient format, and allow for fast display/playback of the sequence.

NB - two samples files included in this repo from the CMU dataset. Modify the __main__ function accordingly if run as a program.

BVHData Class - v1.0

Utility class for BVH Files
Written by Darren Cosker 2020

Usage Example:
    <p>bvhFileName = 'Example.bvh'</p>
    <p>bvhObject = BVHData()</p>
    <p>bvhObject.bvhRead(bvhFileName)</p>
    <p>bvhObject.bvhDraw()</p>

The bvhObject.root then starts the hierarchy of joints/nodes with associated data:<br>
    - Children (list of Nodes)<br>
    - Num channels for this node<br>
    - Names of channels in the node<br>
    - Animation data for the channel<br>
    - Offset for the joint<br>
    - Name of the joint<br>
    - Transformation matrix for the joint<br>
    - Joint coordinates<br>
    <br>
Other notes:<br>
    - Will read a BVH file into a hierarchical format<br>
    - Will store animation sequences for joints in place in a np array<br>
    - Of course, to understand this code you have to first understand how a <br>
    - BVH file is constructed. I would start with these excellent resources:<br>
        https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/BVH.html<br>
        http://www.dcs.shef.ac.uk/intranet/research/public/resmes/CS0111.pdf<br>
