import PySimpleGUI as sg
import face_recognition as fc
import cv2
from multiprocessing import Process, cpu_count
import time, os, datetime


def image_output(folder):
    images_list = os.listdir(folder)
    # print(images_list)
    # print(os.getcwd())
    if not images_list:
        sg.popup_error('no files', 'Failed to find frames.')
        exit(0)

    layout = [
        [sg.Listbox(values=images_list, size=(20, 30), change_submits=True, key='_LISTBOX_', select_mode='single'),
         sg.Image(filename=r''+str(folder)+'/'+str(images_list[0]), key='show_img')],
    ]

    window = sg.Window('Face Finder', layout, size=(850, 400))
    while True:  # The Event Loop
        event, values = window.read()
        # print(event, values) #debug
        if event in (None, 'Exit', 'Cancel'):
            break
        elif event == '_LISTBOX_':
            image_id = str(list(values.items())[0][1]).replace("']", "").replace("['", "")
            print(image_id)
            window.FindElement('show_img').Update(filename=r''+str(folder)+'/'+str(image_id))


def processes_starting():
    # Load some sample pictures and learn how to recognize them.
    input_image = fc.load_image_file(INPUT_IMAGE)
    input_face_encoding = fc.face_encodings(input_image)[0]

    known_faces = [input_face_encoding]
    # Open the input movie file
    input_movie = cv2.VideoCapture(INPUT_VIDEO)
    length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

    if not os.path.exists(INPUT_NAME):
        os.mkdir(INPUT_NAME)

    process_list = []
    part = int(length / (cpu_count() - 1))
    begin_run = 0
    end_run = int(length / (cpu_count() - 1))
    for i in range(1, cpu_count()):
        p = Process(target=main, args=(begin_run, end_run))
        process_list.append(p)
        p.start()
        print(str(i)+';'+str(end_run)+';'+str(begin_run))
        print(str(datetime.datetime.now()))
        end_run = int(part * int(i+1))
        begin_run = int(part * i)

    for p in process_list:
        p.join()


# def progress_bar(length):
#     for i in range(length):
#         sg.PopupAnimated(sg.DEFAULT_BASE64_LOADING_GIF, time_between_frames=100, background_color='white')
#     sg.popup_animated(None)


def main(frame_start, frame_end):
    # Open the input movie file
    input_movie = cv2.VideoCapture(INPUT_VIDEO)
    length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

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
    path_min = 0
    path_hour = 0
    path_sec_str = ''
    path_min_str = ''
    path_hour_str = ''
    name = None

    while True:
        # Grab a single frame of video
        ret, frame = input_movie.read()
        frame_number += 5
        # path = input_movie.get(7)
        if frame_number >= frame_start:

            # Quit when the input video file ends
            if frame_number >= frame_end:
                print(str(datetime.datetime.now()))
                break

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_frame = frame[:, :, ::-1]

            # Find all the faces and face encodings in the current frame of video
            face_locations = fc.face_locations(rgb_frame)
            face_encodings = fc.face_encodings(rgb_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                match = fc.compare_faces(known_faces, face_encoding, tolerance=0.49)

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
            path_sec = int(frame_number / 30)

            if path_sec >= 60:
                while path_sec >= 60:
                    path_min += 1
                    path_sec -= 60
            if path_min >= 60:
                while path_min >= 60:
                    path_hour += 1
                    path_min -= 60

            if path_sec < 10:
                path_sec_str = '0' + str(path_sec)
            else:
                path_sec_str = str(path_sec)

            if path_min < 10:
                path_min_str = '0' + str(path_min)
            else:
                path_min_str = str(path_min)

            if path_hour < 10:
                path_hour_str = '0' + str(path_hour)
            else:
                path_hour_str = str(path_hour)

            path = str(path_hour_str) + ':' + str(path_min_str) + ':' + str(path_sec_str) + '.png'
            path_min = 0
            path_hour = 0
            if name:
                cv2.imwrite(os.path.join(INPUT_NAME, path), frame)
                frame_number += 30
                input_movie.set(1, frame_number)

    # All done!
    input_movie.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    layout = [
        [sg.Text('Name'), sg.InputText()],
        [sg.Text('Image'), sg.InputText(disabled=True), sg.FileBrowse(file_types=(('Image Files', '*.jpg *.png *.jpeg *.raw *.bmp'),))],
        [sg.Text('Video'), sg.InputText(disabled=True), sg.FileBrowse(file_types=(('Video Files', '*.mp4 *.avi *.mkv'),))],
        [sg.Submit(), sg.Cancel()]
    ]
    window = sg.Window('Face Finder', layout)
    while True:  # The Event Loop
        event, values = window.read()
        # print(event, values) #debug
        if event in (None, 'Exit', 'Cancel'):
            break
        if event == 'Submit' and values[0] and values[1] and values[2]:
            # file1 = file2 = isitago = None

            INPUT_NAME = ("_".join(values[0].split()))
            INPUT_IMAGE = values[1]
            INPUT_VIDEO = values[2]
            sg.popup('Please wait, video processing has begun', str(datetime.datetime.now()))

            processes_starting()

            sg.popup('Processing completed', str(datetime.datetime.now()))
            window.Close()
            image_output(INPUT_NAME)




