import face_recognition as fc
import cv2
from multiprocessing import Process, Pool
import sys

INPUT_VIDEO = sys.argv[1] # input video
INPUT_IMAGE = sys.argv[2] # input image
INPUT_NAME = sys.argv[3] # input name

# Create an output movie file (make sure resolution/frame rate matches input video!)
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# output_movie = cv2.VideoWriter('output.avi', fourcc, 29.97, (640, 360))

# Load some sample pictures and learn how to recognize them.
input_image = fc.load_image_file(INPUT_IMAGE)
input_face_encoding = fc.face_encodings(input_image)[0]

known_faces = [input_face_encoding]


def main(output_name, frame_start, frame_end):
    # Open the input movie file
    input_movie = cv2.VideoCapture(INPUT_VIDEO)
    length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

    # # Create an output movie file (make sure resolution/frame rate matches input video!)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_movie = cv2.VideoWriter(output_name, fourcc, 29.97, (640, 360))

    # Load some sample pictures and learn how to recognize them.
    input_image = fc.load_image_file(INPUT_IMAGE)
    input_face_encoding = fc.face_encodings(input_image)[0]

    known_faces = [input_face_encoding]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    frame_number = frame_start  # подать в аргумент начало а также конец
    input_movie.set(1, frame_start)
    while True:
        # Grab a single frame of video
        ret, frame = input_movie.read()
        frame_number += 1
        if frame_number >= frame_start:
            
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
            
            print("Writing frame  {} / {}".format(frame_number, frame_end))
            output_movie.write(frame)
    # All done!
    input_movie.release()
    cv2.destroyAllWindows()
        # # Write the resulting image to the output video file
        # print("Writing frame {} / {}".format(frame_number, length))
        # output_movie.write(frame)


# def video_writer():
#     print("Writing frame {} / {}".format(frame_number, length))
#     output_movie.write(frame)


if __name__ == "__main__":

    # Open the input movie file
    input_movie = cv2.VideoCapture(INPUT_VIDEO)
    length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

    video_part = int(length / 3)

    p1 = Process(target=main, args=('output1.avi', 0, video_part))
    p2 = Process(target=main, args=('output2.avi', video_part, video_part*2))
    p3 = Process(target=main, args=('output3.avi', video_part*2, video_part*3))
    # p4 = Process(target=main, args=('output4.avi', video_part*3, video_part*4))

    p1.start()
    p2.start()
    p3.start()
    # p4.start()

    p1.join()
    p2.join()
    p3.join()
    # p4.join()
    # # Write the resulting image to the output video file
    # for i in range(0, int(length/2)):
    #     print("Writing frame {} / {}".format(i, int(length/2)))
    #     output_movie.write(begin_arr[i])
    #
    # for i in range(0, int(length/2)):
    #     print("Writing frame {} / {}".format(int(length/2), length))
    #     output_movie.write(end_arr[i])




