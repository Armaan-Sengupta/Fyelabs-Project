import math
import matplotlib.pyplot as plt


averagePointList = [[1,1,1], [1,1,1], [1,1,1], [1,1,1], [1,1,1], [1,1,1], [1,1,1], [1,1,1], [1,1,1], [2,2,2],
[2,2,2], [2,2,2], [2,2,2], [2,2,2], [2,2,2], [2,2,2], [2,2,2], [2,2,2], [5,5,5], [2,2,2], [2,2,2], [2,2,2], [2,2,2],
[2,2,2], [2,2,2], [2,2,2], [3,3,3], [4,4,4], [5,5,5], [6,6,6], [7,7,7], [7,7,7], [7,7,7], [7,7,7], [7,7,7], [7,7,7],
[7,7,7], [7,7,7], [7,7,7], [7,7,7], [0.5,0.5,0.5], [0.5,0.5,0.5], [0.5,0.5,0.5], [0.5,0.5,0.5], [0.5,0.5,0.5],
[0.5,0.5,0.5], [0.5,0.5,0.5], [0.5,0.5,0.5], [0.5,0.5,0.5], [0.5,0.5,0.5], [0.5,0.5,0.5], [0.5,0.5,0.5],
[0.5,0.5,0.5], [0.5,0.5,0.5]]

"""
ASUMPTIONS: (as of 11:50am 2023-02-12 no further information provided)
1. The points represent the position of an object recorded at a fixed time interval apart
2. The time interval is the same for all points (i.e. the points are evenly spaced)
3. The time interval is 1s
4. The points are in order of time
5. The points are in the same reference frame (i.e. the same coordinate system)
"""

timeInterval = 0.2 #seconds
distanceFromStart=[] #seperation 

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

for point in averagePointList:
    distanceFromStart.append(distance(point, averagePointList[0]))

velocities=[]
for i in range(1, len(distanceFromStart)-1):
    velocities.append((distanceFromStart[i+1]-distanceFromStart[i])/timeInterval)

acelelerations=[]
for i in range(1, len(velocities)-1):
    acelelerations.append((velocities[i+1]-velocities[i])/timeInterval)

  
# x axis values
x = list(range(0, len(distanceFromStart)))

for i in range(0,len(x)):
    x[i] = x[i]*timeInterval
  
# plotting the points 
plt.subplot(1, 3, 1) # row 1, col 2 index 1
plt.plot(x, distanceFromStart,label="Distance from start")
plt.xlabel('Time (s)')
plt.ylabel('Distance from start (m)')
plt.title('Distance from start vs time')
plt.legend()


plt.subplot(1, 3, 2) # row 1, col 2 index 2
plt.plot(x[1:-1], velocities, label="Velocity")
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.title('Velocity vs time')
plt.legend()


plt.subplot(1, 3, 3) # row 1, col 2 index 1
plt.plot(x[2:-2], acelelerations, label="Acceleration")
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s^2)')
plt.title('Acceleration vs time')
plt.legend()

# function to show the plot
plt.show()