# BVH
Classes, functions and code to work with BVH files

BVHData - Class to read BVH files. 

Usage Example:

bvhFileName = 'Example.bvh'

bvhObject = BVHData()

rootNode = bvhObject.bvhRead(bvhFileName)
