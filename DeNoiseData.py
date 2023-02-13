import laspy
import open3d as o3d
import numpy as np

DEBUG=True

def debug(var):
    if DEBUG:
        print(var)

def display_inlier_outlier(cloud, ind):
    inlier_cloud = cloud.select_by_index(ind)
    outlier_cloud = cloud.select_by_index(ind, invert=True)

    print("Showing outliers (red) and inliers (gray): ")
    outlier_cloud.paint_uniform_color([1, 0, 0])
    inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
    o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])

def remove_outliers(geom,size,numberNeihgbors,deviation):

    #downsample the data
    geom = geom.voxel_down_sample(voxel_size=size)

    #remove statistical outliers (remove returns 2 things, the new list removed of the outliers, and the list of the inliers)
    temp, inliers = geom.remove_statistical_outlier(nb_neighbors=numberNeihgbors,std_ratio=deviation)

    return (geom,inliers)


def main():
    #read file
    las = laspy.read(input("Enter file name: ")+".las")



    #convert to numpy array
    debug("Formatting data")
    point_data = np.stack([las.X, las.Y, las.Z], axis=0).transpose((1, 0))
    #point_data = np.stack([las.X, las.Y, las.Z], axis=1) #more efficent way to do this
    

    #just setup the 3d stuff
    geom = o3d.geometry.PointCloud()
    geom.points = o3d.utility.Vector3dVector(point_data)
    debug("Data formatted")

    down_size = int(input("Enter voxel down sample size: "))
    neighbors = int(input("Enter number of neighbors: "))
    stdDeviation = float(input("Enter standard deviation: "))
    debug("Computing outliers...")

    geom, inliers  = remove_outliers(geom,down_size,neighbors,stdDeviation)
    display_inlier_outlier(geom, inliers)
    

if __name__ == "__main__":
    main()