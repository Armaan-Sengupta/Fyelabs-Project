# Processing Lidar Data
A project where I work with LIDAR data as part of a working interview.

Explanation of each file:
1. **main**: Completes all tasks from 1-9, but dependant on preprocessed files “CaliforniaCleaned” and “CaliforniaNoGround” and DeNoiseData
2. **cleanData**: Removes all points of a specified classification, responsible for creating “CaliforniaCleaned” and “CaliforniaNoGround”
3. **DeNoiseData**: voxel downsizes and removes outliers, main function calls functions in this file
4. **kinematics**: used specifically for question 10
5. **SegmentObjects**: code responsible for partial attempt of 11a
6. **findFurthestPoint**: code that separately is responsible for question 11b
7. **Just view**: first bit of code written, kept since it was useful to just open and visualize point clouds


I found an open source lidar map from https://opentopography.org/ of a city in california. I then used laspy to process the file, and then visualised it using open3d libraries:
![2d3ea93e-68b2-4cdf-9522-dda5fe1a01ee](https://user-images.githubusercontent.com/39814137/219804765-3c0b8afa-36d1-42b1-ba3c-2f33ede2e8ac.png)



## Cleaning up the LIDAR data

#### Removing arieal anomolies

As we can clearly see from the California data set there are several anomalies in the sky which are severely skewing the visibility of our data. To remedy this, there are two easy ways to do this. One would be to simply remove any data points above a certain height, say above 10,000. The second method relies on the fact that .las files include classification information for each point in the dataset. In our particular dataset all of the anomalies in the sky (possibly birds) are classified as code 1, meaning unclassified. From the laspy documentation we can see that each point in fact has the following info.

![Fye Labs Project Report](https://user-images.githubusercontent.com/39814137/219805125-a70643c1-c170-4564-b8c0-714ee5e98e98.png)

Our California data is in point format 1, so we get additional gps time data. For the duration of this project only the x,y,z and classification dimensions were used for each point. Based on having the classification ID for each point I was able to remove each point that had classification 1 (unassigned), thereby getting rid of the aerial anomalies.


When this code is run, we get a new file called “CaliforniaCleaned”. Re-running our visualization code on this new file we get the following:

![Fye Labs Project Report (1)](https://user-images.githubusercontent.com/39814137/219805198-6be20ead-cf69-4f5f-832b-abe03901a8c9.png)

We can actually tell now that the data set represents an urban residential community, which was previously unclear! Although the data visually looks good there are still steps that need to be taken before it can be usefully used in some algorithms.

#### Reducing the number of data points

In our efforts to “clean the data” one of the first steps to take is reducing the number of points in our dataset. This is because with such a large number of points algorithms would not be very fast. To do this I implemented a technique called voxel down sampling. Voxel down sampling works by first splitting up the entire data set into: 
n x n x n voxels, where n represents the size of the voxel cube. Then for each voxel in the dataset you compute the centroid, the average of all the points contained within that voxel, and replace all the points in the voxel by a single point located at the centroid. The larger you make n the more reduction of points will occur. Take a look at a comparison below:

![image](https://user-images.githubusercontent.com/39814137/219805661-ab6c87a1-8c86-49cf-a53f-0e92f9af7960.png)

As we can see the density of points is significantly reduced. Depending on what operations I am doing on the dataset I will apply this filter with varying voxel sizes.

#### Removing outliers

While this data is already looking a lot better, then the next step is to remove outlier points. Visually this most easily manifests itself as small floating points in space, truly just noise. I have highlighted a few examples in the image below:

![Fye Labs Project Report (2)](https://user-images.githubusercontent.com/39814137/219806163-ad2c7ef6-476a-4ad4-bc3e-5a9b4766c7cb.png)


The way outliers are typically removed is their distance to their neighbors is calculated, and if it does not fall within a certain radius the point is considered an outlier. The problem with this is in our data set these outlier points often come in groups of 8-10 points (even after voxel downsizing). This means they would be considered close enough to each other and not get flagged. Instead what I implemented was statistical outlier removal. This removes points who’s average distance from n neighbors is less than the average for every other point in the data set, by some fixed standard deviation, d. The higher n is, the more accurate (up to a point of course) the filter will be, but this will increase compute time, and the lower d is the more aggressive the filter will be. With some experimentation I found that a value of n=50 and d=2.0 worked well. I did this experimentation by highlighting what the program though the outlier points were in red, and everything else (inliers) in grey:

![image](https://user-images.githubusercontent.com/39814137/219806414-b6a275f0-f623-4326-9573-95f04a516e88.png)

![image](https://user-images.githubusercontent.com/39814137/219806557-b5fadff6-05f6-41a8-9a02-a9560af45c2e.png)


When I was satisfied with this “preview” of it’s detections I went through the data set and removed all the points that were identified as outliers. Doing so resulted in the following point cloud:

![Fye Labs Project Report (3)](https://user-images.githubusercontent.com/39814137/219806717-4ac26bed-9bd7-4191-9805-15131d09d00d.png)

Admittedly it is hard to tell a difference, but if you go back and compare it to the image where I pointed out the floating noise you will see that the majority of it is gone. I will point out one specific example, which by the way is the special point from earlier (purely because it was on the edge of the data set and so easier for me to get a direct view of).
![image](https://user-images.githubusercontent.com/39814137/219807513-a75bfbb3-e26e-45f2-a77e-c6af04b6848c.png)

![Fye Labs Project Report (4)](https://user-images.githubusercontent.com/39814137/219806899-8274ae3b-2cb7-4b19-b260-d24af44682e9.png)


##Region of Interest Cropping

To crop the data to a specific ROI I had to first set up a coordinate system, since this data set did not lie anywhere near (0,0,0). To do this I decided the center of the dataset would be my (0,0,0), and so I found the average of the point cloud in the x, y, and z. I then specified a 3D dimensional box centered about this origin with variable side length (I set it to 1000). That yielded the following cropping of the initial point cloud:

![Fye Labs Project Report (5)](https://user-images.githubusercontent.com/39814137/219807220-c34cc2d4-7101-437d-b386-e1a4ee21b38f.png)

![image](https://user-images.githubusercontent.com/39814137/219807395-857b9987-ebec-4454-8296-d15f5a5d3ed4.png)

## Removing ground

In this dataset ground was classified as per the classification table above in the document. So removing ground was actually fairly straight forward, and required almost no extra work since I had made a program already to remove the aerial anomalies, so simply running this program on the current dataset and specifying a value of 2 for ground allowed me to remove it. If the ground was not categorized another option might have been to go to each point in the data, and remove the lowest point there, which would allow for a dynamically changing topography in terms of the height of the ground. However, in this case, it was a fairly trivial operation, and the resultant point cloud can be seen:

![image](https://user-images.githubusercontent.com/39814137/219807758-c7244a12-9f77-42e2-b247-ebf462ff60b9.png)


## Calculating the centroid of the ROI

Calculating the centroid of the ROI involved essentially taking the average of all of the points in the ROI in the x, y, and z dimensions. This is something similar we did before when defining our origin, now the difference simply being that the only points that are considered are the ones inside the ROI. Still the same numpy mean function can be utilized along the zero axis and the point can be added to our 3D visualization. It should be noted that this represents the center of mass assuming everything in the point cloud has the same mass, which it does not. Thus because there is no way to determine mass based on LIDAR data (reflectiveness would not be a good measure) I would be unable to calculate the center of mass. However the average position (the centroid) I did calculate and is seen below; and if you were to claim that everything had equal density, then this would also be the center of mass.

![image](https://user-images.githubusercontent.com/39814137/219808018-23336ef7-ff1b-4eed-8ed2-092281a3a844.png)
![image](https://user-images.githubusercontent.com/39814137/219808070-7a6279f0-0bda-44eb-8c3b-21d84ecac0ca.png)

## Furthest point computation

Personally this was my favorite part of the entire project. In this section the task was to determine a point in the ROI that is the farthest distance from any other point in the rest of the data. Because the ROI contains 8,598 points and the entire data set contains 3,443,405 points, checking each one against another would yield a lot of combinations (~30 billion), and would functionally be O(n^2) in time complexity. As the data set got larger this would mean the time taken to compute this would rise drastically. In an effort to try to make this faster and more scalable I came up with the following algorithm. 

1. Voxel down size and clean up all outlier points (just like before)
2. Find top furthest points from ROI center, say furthest 200
3. Check every point in the ROI against each of the furthest points

#### Clean up the Data

First is to obviously voxel down sample the data should it be very dense, but this does not help much if the data you are working with is simply massive in scale, you can only down size so much before you will begin losing critical data. Still, lets down size both our total map, and our ROI to get the following:

General:
3443405 points → 76753 points with a voxel size of 150

ROI:
8598 points → 1773 points with a voxel size of 300

This already reduces our brute force computations from 30 billion to 100 million. But we can and have to do better, since this is still an O(n^2) problem even if we made n smaller.

#### Find top 200 furthest points

The next step follows with the logic that since the ROI is a subset of the general data set, if we find the top, say 200, points that are furthest from the center of the ROI we know that the furthest point in the ROI will be to one of those 200 points. While I haven't proven this, it should not be too hard to believe this is true, I will show a diagram later as well. If you want a lower chance of missing the furthest distance point, you can simply calculate more points, we will see shortly that for our data set this won't be needed. I was able to find the furthest 200 points by checking the distance from every point in the data set to the ROI center point, which is only in the tens of thousands of calculations. I stored all these distances in a list and sorted the list, and grabbed the last 200 entries. For clarity sake I then added all top 200 furthest points to our 3D view, which yields this:

![image](https://user-images.githubusercontent.com/39814137/219809301-6195ac34-76e2-4f6e-b4ae-af460c936c2e.png)

This is a birds eye view of the entire point cloud. The pink circle is the center point of the ROI, and the smaller cluster of purple points in each corner is each of the top 200 points. It makes sense now that since our ROI center is **roughly** in the middle that our furthest points would be at each corner. However, I could have chosen an ROI anywhere else and this would still work. The reason I wanted to plot these 200 points is now it should be easier to understand that we don't need more than 200 points, since for this dataset the furthest point to any point inside the ROI must be one of those purple points at the corners. 


#### Check against every point in the ROI

The final step is to now check the distance of each of these 200 points against the ones in our ROI. It can be argued that this is no longer an O(n^2) operation and is rather O(n) since the number 200 should not increase linearly with an increasing size of data set. The way I checked each distance was with two nested loops, one that recursed over all the ROI points and the other over the top 200 points. The largest distance, furthest point inside the ROI, and furthest general point were both stored. This is now only in hundreds of thousands of operations, a lot better than billions. Running this algorithm yields the following result:

![image](https://user-images.githubusercontent.com/39814137/219809770-f36ebd9b-b495-455e-97a1-4854f92c96f7.png)

Purple points are the two furthest points, red line is the distance between them, white box is ROI

![image](https://user-images.githubusercontent.com/39814137/219809922-37290a56-b5ec-4350-961a-920a04a3f6ff.png)

Purple points are the furthest points and the red line is the distance between them

This yields the following result:

Top distance: 27990.9 units
Furthest point general: [6.44638525e+06 2.22990918e+07 4.68500000e+02] units
Furthest point ROI: [6.42519508e+06 2.23173801e+07 5.25161407e+02] units
