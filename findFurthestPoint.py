import laspy
import open3d as o3d
import numpy as np
import math
import itertools
import DeNoiseData

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

FILENAME="CaliforniaCleaned"
DEBUG=True

def debug(var):
    if DEBUG:
        print(var)

def make_line_object(p1, p2,colors):
    points = [p1,p2]
    lines = [[0, 1]]

    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(points)
    line_set.lines = o3d.utility.Vector2iVector(lines)
    line_set.colors = o3d.utility.Vector3dVector(colors)
    return line_set

#read file
print("Please wait file reading...")
las = laspy.read(FILENAME+".las")
print("...read success!")

#print number of points in las

debug("Formatting data")
#convert to numpy array
point_data = np.stack([las.X, las.Y, las.Z], axis=1) #more efficent way to do this

#print points in point data
debug("Total points in data set: "+str(len(point_data)))


#just setup the 3d stuff
geom = o3d.geometry.PointCloud()
geom.points = o3d.utility.Vector3dVector(point_data)
debug("Data formatted")

#Denoise the data: downsample the data and remove outliers
debug("Cleaning data...")
geom, index = DeNoiseData.remove_outliers(geom,150,50,2.0)
geom = geom.select_by_index(index)
debug("Data cleaned!")

#print number of points in geom
debug("After cleaning number of points in data set: "+str(len(geom.points)))

fullGeom = geom #save the full geom for later

#cropping the data
centerOrigin = point_data.mean(axis=0) #we will use the mean of the data as the origin point. (x,y,z) -> (red, green, blue) representation of axis colors
centerOrigin[2] = point_data[:,2].min()+300 #set the z value to the lowest z value in the data (the ground), plus 300 centimeters so we can see it clearly
SIDE_OF_BOUNDING_CUBE = 10000 #in centimeters
SIDE_OF_BOUNDING_CUBE*=0.5 #we want half the length of the bounding box since we will be symetrically adding and subtracting from the center point


#                        (x_min,                                    x_max)                                             (y_min,                                            y_max)                      (z_min, z_max)
bounds = [[int(centerOrigin[0]-SIDE_OF_BOUNDING_CUBE), int(centerOrigin[0]+SIDE_OF_BOUNDING_CUBE)], [int(centerOrigin[1]-SIDE_OF_BOUNDING_CUBE), int(centerOrigin[1]+SIDE_OF_BOUNDING_CUBE)], [0,point_data.max(axis=0)[2]]]  # set the bounds
bounding_box_points = list(itertools.product(*bounds))  # create limit points
bounding_box = o3d.geometry.AxisAlignedBoundingBox.create_from_points(o3d.utility.Vector3dVector(bounding_box_points))  # create bounding box object

geom = geom.crop(bounding_box)  # crop the data

input("Set up done, begin processing?")


#quality settings
VOXEL_SIZE = 300  # size of the voxel in centimeters
topx = 200 #how many furthest points to check against the ROI

print("Number of points in ROI downsampled from "+str(len(geom.points)),end=" ")

geom = geom.voxel_down_sample(voxel_size=VOXEL_SIZE)  # downsample the data because this will be checked against all furthest points in the full data set

print("to: "+str(len(geom.points))+" based on a voxel size of "+str(VOXEL_SIZE))

#convert our two locations to np arrays
ROI = np.asarray(geom.points)
FULL = np.asarray(fullGeom.points)


#so, plan, there are thousands of points in the ROI, and millions in the full data set, checking every combination will take a long time (10^1,000,000 combinations)
#so we will check everypoint just with respect to the center point of the ROI, and make a list of the top x furthest points. Then we will check those points against the full ROI.

distances=[] #list of the top x distances, and their index in the ROI
i=0
for point in FULL:
    distances.append([i,distance(point, centerOrigin)])
    i+=1

debug("Distances calculated, sorting...")

distances.sort(key=lambda x: x[1]) #sort the list by the distance
distances = distances[-topx:] #get the top x distances
debug(f"Top {topx} distances calculated, now checking against ROI...")


"""
#uncomment to show all top x distances
# Create an empty Open3D visualizer
vis = o3d.visualization.Visualizer()
vis.create_window()
vis.add_geometry(fullGeom)

point = centerOrigin
mesh_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=500)
mesh_sphere.paint_uniform_color([0.92, 0.5, 0.94])
mesh_sphere.translate(point)
vis.add_geometry(mesh_sphere)


for index in distances:
    point = FULL[index[0]]
    mesh_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=100)
    mesh_sphere.paint_uniform_color([0.62, 0.12, 0.94])
    mesh_sphere.translate(point)
    vis.add_geometry(mesh_sphere)
    
vis.update_renderer()
vis.run()
"""


topDistance=0
furthestPointROI=[0,0,0]
furthestPointGeneral=[0,0,0]
iterations=0
#now we have the top x distances, we will check them against the all the points in the ROI
for point in ROI:
    for index in distances:
        dist=distance(FULL[index[0]], point)
        if topDistance < dist:
            topDistance = dist #replace the distance with the new distance
            furthestPointGeneral = FULL[index[0]] #replace the furthest point with the new furthest point
            furthestPointROI = point #replace the furthest point with the new furthest point
        iterations+=1

print(f"{iterations} points checked and based on that...")
print("Top distance: "+str(topDistance))
print("Furthest point ROI: "+str(furthestPointROI))
print("Furthest point general: "+str(furthestPointGeneral))

radiusOfPoint=300
colorOfPoint=[0.62, 0.12, 0.94]

#furthest general point
mesh_sphere_general = o3d.geometry.TriangleMesh.create_sphere(radius=radiusOfPoint)
mesh_sphere_general.compute_vertex_normals()
mesh_sphere_general.paint_uniform_color(colorOfPoint)
mesh_sphere_general.translate(furthestPointGeneral)

#furthest point in ROI
mesh_sphere_roi = o3d.geometry.TriangleMesh.create_sphere(radius=radiusOfPoint)
mesh_sphere_roi.compute_vertex_normals()
mesh_sphere_roi.paint_uniform_color(colorOfPoint)
mesh_sphere_roi.translate(furthestPointROI)

#draw line between the two points
points = [furthestPointGeneral,furthestPointROI]
lines = [[0, 1]]
colors = [[1, 0, 0]]

line_set = o3d.geometry.LineSet()
line_set.points = o3d.utility.Vector3dVector(points)
line_set.lines = o3d.utility.Vector2iVector(lines)
line_set.colors = o3d.utility.Vector3dVector(colors)


#set fullGeom grey
fullGeom.paint_uniform_color([0.2, 0.2, 0.2])

o3d.visualization.draw_geometries([fullGeom,mesh_sphere_general,mesh_sphere_roi,line_set,bounding_box], window_name="Armaan 3D Lidar Data", width=1920, height=1080)

