import cv2


class CameraDetector:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.capture = None
        self.hog = None

        if hasattr(cv2, "HOGDescriptor") and hasattr(cv2, "HOGDescriptor_getDefaultPeopleDetector"):
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def start(self):
        if self.capture is None or not self.capture.isOpened():
            self.capture = cv2.VideoCapture(self.camera_index)

        return self.capture.isOpened()

    def read_frame(self):
        if self.capture is None or not self.capture.isOpened():
            return False, None

        return self.capture.read()

    def detect_person(self, frame):
        resized = cv2.resize(frame, (320, 240))
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40),
        )

        boxes = []
        weights = []

        if self.hog is not None:
            boxes, weights = self.hog.detectMultiScale(
                resized,
                winStride=(8, 8),
                padding=(8, 8),
                scale=1.05,
            )

        person_detected = len(faces) > 0 or len(boxes) > 0

        for face in faces:
            x, y, width, height = face
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)
            cv2.putText(
                frame,
                "WAJAH TERDETEKSI",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        return person_detected, frame

    def stop(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None
