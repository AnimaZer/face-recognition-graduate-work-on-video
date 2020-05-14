import face_recognition as fc
import cv2
import numpy as np
from time import time
from threading import Thread
from multiprocessing import Process, Pool
import sys

INPUT_VIDEO = sys.argv[1] # input video
INPUT_IMAGE = sys.argv[2] # input image
INPUT_NAME = sys.argv[3] # input name
# CHOICE = sys.argv[4] # type work

# Open the input movie file
input_movie = cv2.VideoCapture(INPUT_VIDEO)
length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

# Create an output movie file (make sure resolution/frame rate matches input video!)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_movie = cv2.VideoWriter('output.avi', fourcc, 29.97, (640, 360))

# Load some sample pictures and learn how to recognize them.
input_image = fc.load_image_file(INPUT_IMAGE)
input_face_encoding = fc.face_encodings(input_image)[0]

known_faces = [input_face_encoding]

# Array declaration
begin_arr = []
end_arr = []


def main(process_name, frame_start, frame_end):
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    frame_number = frame_start  # подать в аргумент начало а также конец

    while True:
        # Grab a single frame of video
        ret, frame = input_movie.read()
        frame_number += 1

        # Quit when the input video file ends
        if frame_number >= frame_end:
            break

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = fc.face_locations(rgb_frame)
        face_encodings = fc.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = fc.compare_faces(known_faces, face_encoding, tolerance=0.50)

            # If you had more than 2 faces, you could make this logic a lot prettier
            # but I kept it simple for the demo
            name = None
            if match[0]:
                name = INPUT_NAME

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

        if process_name == 'process1':
            begin_arr.append(frame)

        elif process_name == 'process2':
            end_arr.append(frame)
        # # Write the resulting image to the output video file
        # print("Writing frame {} / {}".format(frame_number, length))
        # output_movie.write(frame)


# def video_writer():
#     print("Writing frame {} / {}".format(frame_number, length))
#     output_movie.write(frame)


if __name__ == "__main__":
    process_list = []

    # for i in range(3):
    #     p = Process(target=main, args=(Process.name, frame_start, frame_end), name='process'+i)
    #     process_list.append(p)
    #     if Process.name == 'process1':
    #         frame_start = 0
    #         frame_end = int(length / 2)
    #
    #     elif Process.name == 'process2':
    #         frame_start = int(length / 2)
    #         frame_end = length
    #     p.start()
    #     print('process ', i, ' is started')
    #
    # for p in process_list:
    #     p.join()
    #     print('process ', p, ' is joined')
    if Process.name == 'process1':
        frame_start = 0
        frame_end = int(length / 2)

    elif Process.name == 'process2':
        frame_start = int(length / 2)
        frame_end = length
    frame_start = 0
    frame_end = int(length / 2)
    p1 = Process(target=main, args=('process1', frame_start, frame_end))
    p1.start()
    frame_start = int(length / 2)
    frame_end = length
    p2 = Process(target=main, args=('process2', frame_start, frame_end))
    p2.start()

    p1.join()
    p2.join()
    # Write the resulting image to the output video file
    for i in range(0, int(length/2)):
        print("Writing frame {} / {}".format(i, int(length/2)))
        output_movie.write(begin_arr[i])

    for i in range(0, int(length/2)):
        print("Writing frame {} / {}".format(int(length/2), length))
        output_movie.write(end_arr[i])

    # All done!
    input_movie.release()
    cv2.destroyAllWindows()