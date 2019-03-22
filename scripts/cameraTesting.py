from picamera.array import PiYUVArray, PiRGBArray
from picamera import PiCamera
from scipy.signal import find_peaks, butter, filtfilt
import time
import matplotlib.pyplot as plt
import skimage as ski

res = (640,480)
b, a = butter(3, 0.02)

camera = PiCamera()

camera.sensor_mode = 7
camera.resolution = res
camera.framerate = 120
rawCapture = PiYUVArray(camera, size=res)
stream = camera.capture_continuous(rawCapture, format="yuv", use_video_port=True)

N = 300
k = 0
t = time.time()

for f in stream:
	I = f.array[:, :, 0]
	rawCapture.truncate(0)
	L = I[120, :]
	Lf = filtfilt(b, a, L)
	p = find_peaks(Lf, height=128)
	k += 1
	if k > N:
		break

time_elapsed = time.time() - t
print("Elapsed {:0.2f} seconds, estimated FPS {:0.2f}".format(time_elapsed, N / time_elapsed))

stream.close()
rawCapture.close()
camera.close()
