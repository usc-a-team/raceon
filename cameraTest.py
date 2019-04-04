from picamera.array import PiYUVArray, PiRGBArray
from picamera import PiCamera
from scipy.signal import find_peaks, butter, filtfilt
import time
import matplotlib.pyplot as plt
import skimage as ski
import numpy as np

res = (640,480)
b, a = butter(3, 0.02)

camera = PiCamera()

# Check the link below for the combinations between mode and resolution
# https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
camera.sensor_mode = 7
camera.resolution = res
camera.framerate = 20

# Initialize the buffer and start capturing
rawCapture = PiYUVArray(camera, size=res)
stream = camera.capture_continuous(rawCapture, format="yuv", use_video_port=True)

# Measure the time needed to process 300 images to estimate the FPS
N = 300
k = 0
t = time.time()

for f in stream:
    # Get the intensity component of the image (a trick to get black and white images)
    I = f.array[:, :, 0]
    #plt.imshow(I)
    
    # Reset the buffer for the next image
    rawCapture.truncate(0)
    
    # Select a horizontal line in the middle of the image
    L = I[240, :]

    # Smooth the transitions so we can detect the peaks 
    Lf = filtfilt(b, a, L)

    # Find peaks which are higher than 0.5
    p = find_peaks(Lf, height=128)
    
    # Print peaks
    # print(p)
    
    # p should have THREE peaks per frame/image. The range is from 0 to ~ 640. 
    # If the car is perfecly center, I THINK, we should have a 0 peak a 320ish peak and a 640ish peak
    
    # So here we should steer and then update to the next frame.
    
    # Increment the number of processed frames
    k += 1
    if k > N:
        break

time_elapsed = time.time() - t
print("Elapsed {:0.2f} seconds, estimated FPS {:0.2f}".format(time_elapsed, N / time_elapsed))

stream.close()
rawCapture.close()
camera.close()

# Plot the pixel intensities along the selected line
#plt.plot(L, label="raw")
#plt.plot(Lf, label="filtered")
#plt.ylim([0, 300])
#plt.legend()
