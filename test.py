from multiprocessing import Process, Queue, Manager,Pipe
import multiprocessing
import face_recognition as fik
import cv2
import time
import sys

# 1 input video name
# 2 input image name
# 3 face name
video_input = sys.argv[1]

face_image = fik.load_image_file(sys.argv[2])
load_face_encoding = fik.face_encodings(face_image)[0]
face_name = sys.argv[3]


quality = 0.7


def f(id,fi,fl):
    import face_recognition as fok

    while True:
        small_frame = fi.get()
        print("running thread"+str(id))
        face_locations = fok.face_locations(small_frame)

        if(len(face_locations)>0):
            print(face_locations)
            for (top7, right7, bottom7, left7) in face_locations:

                small_frame_c = small_frame[top7:bottom7, left7:right7]
                fl.send(small_frame_c)

fps_var =0
if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')


    # global megaman
    with Manager() as manager:

        video_capture = cv2.VideoCapture(video_input)

        fi = Queue(maxsize=14)

        threads = 4
        proc = []

        parent_p = []
        thread_p = []
        # procids = range(0,threads)
        for t in range(0,threads):
            p_t,c_t = Pipe()
            parent_p.append(p_t)
            thread_p.append(c_t)
            print(t)
            proc.append(Process(target=f, args=(t,fi,thread_p[t])))
            proc[t].start()


        useframe = False

        frame_id = 0
        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()
            effheight, effwidth = frame.shape[:2]
            if effwidth < 20:
                break
            # Resize frame of video to 1/4 size for faster face recognition processing
            xxx = 930
            yyy = 10/16 #0.4234375
            small_frame = cv2.resize(frame, (xxx, int(xxx*yyy)))
            if frame_id%2 == 0:
                if not fi.full():


                    fi.put(small_frame)

                    print(frame_id)

                    cv2.imshow('Video', small_frame)


                    print("FPS: ", int(1.0 / (time.time() - fps_var)))
                    fps_var = time.time()


            #GET ALL DETECTIONS
            for t in range(0,threads):
                if parent_p[t].poll():
                    small_frame_c = parent_p[t].recv()
                    cv2.imshow('recc', small_frame_c)
                    height34, width34 = small_frame_c.shape[:2]
                    # print fsizeee
                    if(width34<20):
                        print("face 2 small")
                        print(width34)
                        break
                    face_encodings_cam = fik.face_encodings(small_frame_c,[(0, width34, height34, 0)])

                    match = fik.compare_faces([load_face_encoding], face_encodings_cam[0])
                    name = "Unknown"

                    if match[0]:
                        name = face_name

                    print(name)
                    break

            frame_id += 1

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
