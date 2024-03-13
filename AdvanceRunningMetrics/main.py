"""
This script performs analysis on load cell and microphone data related to foot strikes during running.

It loads data from load cell and microphone sensors, analyzes foot strike data, calculates various parameters related to force footstrike, determines distances traveled, and defines a function for performing Fast Fourier Transform (FFT) analysis on microphone data.

Author: Daniel Cooper
Date: 3/13/2024
"""

import numpy as np
import matplotlib.pyplot as plt

# Define the path to the dataset directory
DataRootDir = r'C:\Users\cooper\Documents\MATLAB'
Dname = 'Emily_11.3.22'
Dname = DataRootDir + '\\' + Dname
print(Dname)

row = 20

# Read load cell and microphone data
ForceData = np.load('load_cells_Data.npy')
MicData = np.load('mic_data.npy')

# FOOTSTRIKE FINDING MAX
endvalue = ForceData['footStrikeTime'][row].flatten()[~np.isnan(ForceData['footStrikeTime'][row])][-1]
endvaluenum = len(endvalue)

# Find the maximum footstrike value and its corresponding time
xmax = np.max(ForceData['footStrike'][row])
ymax = np.argmax(ForceData['footStrike'][row])

maxStrike = xmax
maxTime = ForceData['footStrikeTime'][row, ymax]

ymaxAccel = ymax * 20

# Calculate various percentages and values related to force footstrike analysis
# Analyze zones and calculate percentages
zone1_percent = ForceData['footStrikeZone1'][row, ymax] / maxStrike * 100
zone2_percent = ForceData['footStrikeZone2'][row, ymax] / maxStrike * 100
zone3_percent = ForceData['footStrikeZone3'][row, ymax] / maxStrike * 100
zone4_percent = ForceData['footStrikeZone4'][row, ymax] / maxStrike * 100
RIGHT_percent = ForceData['RIGHT'][row, ymax] / maxStrike
LEFT_percent = ForceData['LEFT'][row, ymax] / maxStrike

# Calculate other zone percentages similarly
# Calculate average percentage for front zone
FRONT_percent = (zone1_percent + zone2_percent) / 100

# Calculate values of each zone
zone1_value = ForceData['footStrikeZone1'][row, ymax]
zone2_value = ForceData['footStrikeZone2'][row, ymax]
zone3_value = ForceData['footStrikeZone3'][row, ymax]
zone4_value = ForceData['footStrikeZone4'][row, ymax]
RIGHT_value = ForceData['RIGHT'][row, ymax]
LEFT_value = ForceData['LEFT'][row, ymax]

# Calculate other zone values similarly
# Calculate right-left placement
right_left_placement = LEFT_percent * 25

# Perform calculations to determine the distance traveled and other parameters
# Calculate distance traveled using slope calculation
# Determine the distance from the front of the deck where the foot strikes occur
# Loop through foot strikes to calculate distances and plot foot strikes on a treadmill deck


zonevectorpercentage = np.array([zone1_percent, zone2_percent, zone3_percent, zone4_percent])
zonevectorvalue = np.array([zone1_value, zone2_value, zone3_value, zone4_value])
deckvector = np.array([8.3, 26.7, 28.3, 26.7, 10])

sum = 0
sum2 = 0
rise = 0
run = 0
ii = 0
b = 0
while True:
    if sum + zonevectorpercentage[ii] > 50:
        break
    else:
        sum += zonevectorpercentage[ii]
        b = sum
        sum2 += deckvector[ii]
        rise = zonevectorpercentage[ii + 1]
        run = deckvector[ii]
    ii += 1

m = rise / run
x = fact(m, b)
distance = ((x + sum2) / 100) * 60

distanceFront = 60 - (60 * FRONT_percent)

arrayX = []
arrayY = []

for j in range(len(ForceData['endTime'])):
    zone1_percentnextstrike = ForceData['footStrikeZone1'][j, ymax] / maxStrike * 100
    zone2_percentnextstrike = ForceData['footStrikeZone2'][j, ymax] / maxStrike * 100
    FRONT_percentnextstrike = (zone1_percentnextstrike + zone2_percentnextstrike) / 100
    LEFT_percentnextstrike = ForceData['LEFT'][j, ymax] / maxStrike
    distanceX = 60 - (60 * FRONT_percentnextstrike)
    distanceY = LEFT_percentnextstrike * 25
    arrayX.append(distanceX)
    arrayY.append(distanceY)

averageXdist = np.mean(arrayX)
averageYdist = np.mean(arrayY)

plt.figure()
for j in range(1, len(ForceData['endTime'])):
    zone1_percentnextstrike = ForceData['footStrikeZone1'][j, ymax] / maxStrike * 100
    zone2_percentnextstrike = ForceData['footStrikeZone2'][j, ymax] / maxStrike * 100
    FRONT_percentnextstrike = (zone1_percentnextstrike + zone2_percentnextstrike) / 100
    LEFT_percentnextstrike = ForceData['LEFT'][j, ymax] / maxStrike
    distanceX = 60 - (60 * FRONT_percentnextstrike)
    distanceY = LEFT_percentnextstrike * 25
    plt.plot([0, distance, 60], [0, 12.5, 25], 'x', color='white')
    plt.plot(distanceX, distanceY, 'x', color='red')
    plt.plot(12, np.arange(26), '.', color='blue')
plt.show()


def fact(m, b):
    return (50 - b) / m

# Define a function to calculate FFT (Fast Fourier Transform)
def FFT(FFT_MIC, FFTValues):
    # Calculate single-sided and two-sided spectrum
    P2 = np.abs(FFT_MIC / FFTValues)
    P1 = P2[:int(FFTValues / 2) + 1]
    P1[1:-1] = 2 * P1[1:-1]

    # Add zeros to the end of the two-sided spectrum
    # Also, set the first value to 0
    P2 = np.append(P2, 0)
    P1[0] = 0
    P2[0] = 0

    return P1
