# BVH
Class to work with BVH files. Although part of larger personal projects, this is intended to be 'helper' code that is clean and simple, so that others can either use the class directly or modify to their needs in an easy manner. Due to this, the code when run is pretty verbose - with lots of 'prints' - so people can see what is going on at different time steps. Of course this makes it slower so remove the prints if used in earnest!

BVHData - Class to read and display (in a simple format) BVH files

Usage Example:

bvhFileName = 'Example.bvh' <br>
bvhObject = BVHData() <br>
bvhObject.bvhRead(bvhFileName) <br>
bvhObject.bvhDraw()
