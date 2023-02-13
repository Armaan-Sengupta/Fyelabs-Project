import laspy
import open3d as o3d
import numpy as np
import math
import itertools
import DeNoiseData

"""
By: Armaan Sengupta
Date: 2023-02-12
Fyelabs LIDAR Project
Dependant: DeNoiseData.py
Libraries used: laspy, open3d, numpy, math, itertools
"""

FILENAME="CaliforniaNoGround"
DEBUG=True

def debug(var):
    if DEBUG:
        print(var)

#read file
print("Please wait file reading...")
las = laspy.read(FILENAME+".las")
print("...read success!")

debug("Formatting data")
#convert to numpy array
point_data = np.stack([las.X, las.Y, las.Z], axis=1) #more efficent way to convert than the doccumentation says



#just setup the 3d stuff
geom = o3d.geometry.PointCloud()
geom.points = o3d.utility.Vector3dVector(point_data)
debug("Data formatted")

#Denoise the data: downsample the data and remove outliers
debug("Cleaning data...")
geom, index = DeNoiseData.remove_outliers(geom,0.05,50,2.0)
geom = geom.select_by_index(index)
debug("Data cleaned!")

#cropping the data
centerOrigin = point_data.mean(axis=0) #we will use the mean of the data as the origin point. (x,y,z) -> (red, green, blue) representation of axis colors
centerOrigin[2] = point_data[:,2].min()+300 #set the z value to the lowest z value in the data (the ground), plus 300 centimeters so we can see it clearly
SIDE_OF_BOUNDING_CUBE = 10000 #in centimeters
SIDE_OF_BOUNDING_CUBE*=0.5 #we want half the length of the bounding box since we will be symetrically adding and subtracting from the center point


#                        (x_min,                                    x_max)                                             (y_min,                                            y_max)                      (z_min, z_max)
bounds = [[int(centerOrigin[0]-SIDE_OF_BOUNDING_CUBE), int(centerOrigin[0]+SIDE_OF_BOUNDING_CUBE)], [int(centerOrigin[1]-SIDE_OF_BOUNDING_CUBE), int(centerOrigin[1]+SIDE_OF_BOUNDING_CUBE)], [0, math.inf]]  # set the bounds
bounding_box_points = list(itertools.product(*bounds))  # create limit points (8 vertices of the bounding cube)
bounding_box = o3d.geometry.AxisAlignedBoundingBox.create_from_points(o3d.utility.Vector3dVector(bounding_box_points))  # create bounding box object

geom = geom.crop(bounding_box)  # crop the data


mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1000, origin=[centerOrigin[0], centerOrigin[1], 500]) #draw the origin frame

#calculate the average position of all the remaining points
centerOfMass = np.asarray(geom.points).mean(axis=0) #this can be considered the center of mass of the data assuming the mass is uniform (which it is not)

#draw our center of mass sphere and put it in the right spot
mesh_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=200)
mesh_sphere.compute_vertex_normals()
mesh_sphere.paint_uniform_color([0.62, 0.12, 0.94])
mesh_sphere.translate(centerOfMass)
print("Center of mass (purple sphere): ", centerOfMass)


debug("All done!")
o3d.visualization.draw_geometries([geom,mesh_frame,mesh_sphere], window_name="Armaan 3D Lidar Data", width=1920, height=1080)


