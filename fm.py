# 7/29/19 AHMED AISSAM
# RECORDS A COUNT OF UNIQUE FACES IN A DAY

import face_recognition
import cv2
import numpy as np
from datetime import datetime, date
import pickle
import os
import os.path

# List of known face encodings with their metadata
face_encodings = []
face_metadata = []

# Creates a daily count
dcounter = 0
# Initial date the script is ran
run_date = datetime.today().strftime('%Y-%m-%d')

try: 
    # Looks for an old dcount.txt file
    with open("dcount.txt", "r") as dcount:
        
        for line in dcount:
            pass
        # Last written date
        last_date = line.split()[0]
        # Last written day count
        last_count = int(line.split()[1])
        dcounter += last_count

except FileNotFoundError as e:
    # If one is not found, a new file is created
    print("NEW dcount.txt CREATED")
    pass


def load_faces():
    global face_encodings, face_metadata, dcounter
    now = datetime.today().strftime('%Y-%m-%d')
    try: 
        # Looks for an old faces.dat file
        with open("faces.dat", "rb") as face_data_file:
            
            if run_date != now or last_date != now:
                os.remove("faces.dat")
                pass
            # Crashed on the same day
            else:
                face_encodings, face_metadata = pickle.load(face_data_file)
                print("TODAYS FILE LOADED")
    except FileNotFoundError as e:
        # If one is not found, a new file is created
        print("NEW faces.dat CREATED")
        pass

def save_dcount():
    try: 
        # Looks for an old dcount.txt file
        with open("dcount.txt", "r") as dcount:
            
            for line in dcount:
                pass
            # Last written date
            last_date = line.split()[0]
    except FileNotFoundError as e:
        # If one is not found, a new file is created
        print("NEW dcount.txt CREATED")
        pass
    now = datetime.today().strftime('%Y-%m-%d')
    if last_date == run_date:
        with open("dcount.txt", "a") as dcount:
            for line in dcount:
                pass
            line.write("%s %d unique visits\n" % (now, dcounter))
    else:
         with open("dcount.txt", "a") as dcount:
            dcount.write("\n%s %d unique visits" % (now, dcounter))   
    print("DAY COUNT SAVED")


def save_faces():
    # Opens the faces.dat as writeable
    with open("faces.dat", "wb") as face_data_file:
        face_data = [face_encodings, face_metadata]
        # Writes the new faces to the faces.dat file
        pickle.dump(face_data, face_data_file)
    print("FACES SAVED TO FILE")

def register_face(face_encoding):
    # Adds the new face_encoding to list of faces
    face_encodings.append(face_encoding) 
    
    # Creates a dictionary entry to the metadata list for the face encoding
    # It records the time they were seen, to ensure the same person isn't counted twice
    face_metadata.append({
        "time_seen": datetime.today()
 })            


def lookup_face(face_encoding):
        # Checks whether the face is already on the face list
        metadata = None

        # If the face list is empty, return nothing as this face is the first face seen

        if len(face_encodings) == 0:
            return metadata

        # Calculate the face distance between the unknown face & every face on the face list
        # Returns a float between 0.0 - 1.0 ; a smaller value is more similar
        face_distances = face_recognition.face_distance(face_encodings, face_encoding)

        # Grabs a known face that has the lowest distance from the unknown face
        best_match_index = np.argmin(face_distances)

        # A face with a distance less than 0.6 is considered a match
        if face_distances[best_match_index] < 0.6:
            # If a match, the previous metadata is grabbed
            metadata = face_metadata[best_match_index]
            
        return metadata

def main_loop():
    global dcounter

    # Passes the linux kernel video stream number to OpenCV
    # All video streams can be found using "ls -ltrh /dev/video*"
    video_capture = cv2.VideoCapture(0)

    while 1:
        # Grabs frame from video 
        ret, frame = video_capture.read()        

        # Converts image from BGR color (OpenCV Default) to RGB
        rgb_frame = frame[:, :, ::-1]

        # Finds all the face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Checks whether each detected face is already in the face list
        # The face_label indicates whether the face has been seen now or not
        face_labels = []
        
        for face_location, face_encoding in zip(face_locations, face_encodings):
         
            # Checks if face is in list of known faces
            metadata = lookup_face(face_encoding)

            # If this face has already been seen now, label it as such
            if metadata is not None:
                face_label = f"{datetime.today().strftime('%H:%M:%S')}"

            # If this face hasn't been seen now, add it to the list of faces
            else:
                face_label = f"{datetime.today().strftime('%H:%M:%S')}"

                # Adds to the day count for a new face
                dcounter += 1

                # Adds the new face's data
                register_face(face_encoding, )

                # Saving the known faces and daily count every time a new face is detected
                save_faces()
                save_dcount()
            
            face_labels.append(face_label)
        
        # Draws a bounding box around each face with a label
        for (top, right, bottom, left), face_label in zip(face_locations, face_labels):
            
            # Location & color of frame that surrounds face
            cv2.rectangle(frame, (left,top), (right, bottom), (0, 0, 255), 2)

            # Location & color of face label frame
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            # Location, color, and font of face label
            cv2.putText(frame, face_label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        # Outputs the frame with boxes drawn around the faces
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            save_faces()
            save_dcount()
            break

    # Releases handle to webcam
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    load_faces()
    main_loop()
