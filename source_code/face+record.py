import cv2
import os
import face_recognition
import threading
import time

os.chdir("source_code")
x_c = 0 
y_c = 0
class WebcamRecorder:
    def __init__(self, filename):
        self.filename = filename
        self.frame = None
        self.centerFace = (-1, -1)
        self.isRecording = False
        self.frames = []
        self.prevFaces = []
        self.fps = 60
        self.stop_event = threading.Event()
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)  # Set to 30 frames per second
        t = threading.Thread(target=self.updateFrameLoop, args=(self))
        t.start()


    def getCoords(self, frame):
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        if len(face_locations) == 0:
            print("nofacedetected")
            return (-1, -1)
        middle_point = (frame.shape[1] // 2, frame.shape[0] // 2)
        closest_face_location = min(face_locations, key=lambda loc: (loc[0]+loc[2] - middle_point[0])**2 + (loc[1]+loc[3] - middle_point[1])**2)
        top, right, bottom, left = closest_face_location
        the_center = ((left+right)//2, (top+bottom)//2)
        return the_center
    
    def updateFrame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.frame = frame
            if self.isRecording():
                self.frames.append(frame)
            self.centerFace = self.getCoords(frame)
            print("Center of face", self.centerFace)
            #diy fifo queue
            self.prevFaces.append(self.centerFace)
            if len(self.prevFaces>30):
                self.prevFaces.pop(0)

    def updateFrameLoop(self):
        while True:
            self.updateFrame()
    
    def _save(self):
        if len(self.frames) == 0:
            return
        height, width, channels = self.frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.filename, fourcc, self.fps/6, (width, height))  # reduce fps
        for frame in self.frames:
            out.write(frame)
            time.sleep(1/self.fps)  # wait between frames
        out.release()
        self.frames = []

if __name__ == "__main__":
    recorder = WebcamRecorder("output.mp4")
    recorder.start()
    recorder.isRecording = True
    time.sleep(5)
    recorder.isRecording = False
    recorder.save()

