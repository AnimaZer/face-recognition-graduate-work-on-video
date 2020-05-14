import face_recognition
import cv2
import threading
from queue import Queue
import sys

# This is a demo of running face recognition on a video file and saving the results to a new video file.
#
# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.


def main(in_queue, out_queue, input_movie, length, face_image, face_name):
    # Open the input movie file
    # input_movie = cv2.VideoCapture(argv[0])
    # length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create an output movie file (make sure resolution/frame rate matches input video!)
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # output_movie = cv2.VideoWriter('output.avi', fourcc, 30, (640, 360))

    # Load some sample pictures and learn how to recognize them.
    # face_image = face_recognition.load_image_file(argv[1])
    my_face_encoding = face_recognition.face_encodings(face_image)[0]

    known_faces = [
        my_face_encoding,
    ]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    frame_number = 0

    while True:
        item = in_queue.get()
        result = item
        # Grab a single frame of video
        ret, frame = input_movie.read()
        frame_number += 1

        # Quit when the input video file ends
        if not ret:
            break

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.50)

            # If you had more than 2 faces, you could make this logic a lot prettier
            # but I kept it simple for the demo
            name = None
            if match[0]:
                name = face_name

            face_names.append(name)

        # Label the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            if not name:
                continue

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

        # Write the resulting image to the output video file
        print("Writing frame {} / {}".format(frame_number, length))
        output_movie.write(frame)
        if frame_number >= length:
            break
    # All done!
    input_movie.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # main(sys.argv[1:])
    work = Queue()
    results = Queue()
    input_movie = cv2.VideoCapture(sys.argv[1])
    length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))
    face_image = face_recognition.load_image_file(sys.argv[2])
    face_name = sys.argv[3]

    # Create an output movie file (make sure resolution/frame rate matches input video!)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_movie = cv2.VideoWriter('output.avi', fourcc, 30, (640, 360))

    # start for workers
    for i in range(4):
        t = threading.Thread(target=main, args=(work, results, input_movie, length,  face_image, face_name))
        t.daemon = True
        t.start()

    # produce data
    for i in range(length):
        work.put(i)

    work.join()

    # get the results
    for i in range(length):
        print(results.get())

    sys.exit()
