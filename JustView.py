import laspy
import open3d as o3d
import numpy as np

"""
By: Armaan Sengupta
Date: 2023-02-12
Fyelabs LIDAR Project
Note: This does not complete any of the questions. It is a very simple script that just reads the file and displays it in 3d
"""

FILENAME="Pennsylvania"

#read file
print("Please wait file reading...")
las = laspy.read(FILENAME+".las")
print("...read success!")

print("Formatting data...")
#grab the point data only (x,y,z) and convert it to a numpy array
point_data = np.stack([las.X, las.Y, las.Z], axis=0).transpose((1, 0))

#print number  of points in las
print("Total points in data set: "+str(len(point_data)))

#print min and max points (z axis)
print("Min Z: "+str(point_data[:,2].min()))
print("Max Z: "+str(point_data[:,2].max()))

#print the las file point format
print("Point Format: "+str(las.point_format))


#just setup the 3d stuff
geom = o3d.geometry.PointCloud()
geom.points = o3d.utility.Vector3dVector(point_data)

print("...Data formatted")
#output windows
o3d.visualization.draw_geometries([geom], window_name="Armaan 3D Lidar Data", width=1920, height=1080)


