# BVH
Class to work with BVH files. Although part of larger personal projects, this is intended to be 'helper' code that is clean and simple, so that others can either use the class directly or modify to their needs.

BVHData - Class to read and display (in a simple format) BVH files

Usage Example:

bvhFileName = 'Example.bvh'
bvhObject = BVHData()
bvhObject.bvhRead(bvhFileName)
bvhObject.bvhDraw()
