from scipy.spatial import distance as dist
from imutils import face_utils
import numpy as np
import imutils
import dlib
import cv2

from tools.config import *

import time


def eye_aspect_ratio(eye):
    """Computes the euclidean distances between eye landmarks.
    
    Parameters
    ----------
    eye : list
        A list containing eyes landmarks.

    Returns
    -------
    ear : float
        The eye aspect ratio (EAR). 
    """

    # Euclidean distance between vertical eye landmarks
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # Euclidean distance between horizontal eye landmarks
    C = dist.euclidean(eye[0], eye[3])

    # Compute EAR
    ear = (A + B) / (2.0 * C)

    return ear


def eye_processor(args):
    """Main function.
    
    Parameters
    ----------
    args : dict
        A dictionary containing the arguments from the parser.
    """

    if args['verbose']:
        print('[INFO] Loading facial landmark predictor...')

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args['shape_predictor'])

    (l_start, l_end) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
    (r_start, r_end) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

    if args['verbose']:
        print('[INFO] Opening camera...')

    cap = cv2.VideoCapture(0)

    while True:
        global COUNTER, TOTAL, ASLEEP

        _, frame = cap.read()
        frame = cv2.resize(frame, (640, 360))
        original = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        start = time.time()
        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            for _, (i, j) in face_utils.FACIAL_LANDMARKS_IDXS.items():
                for (x, y) in shape[i:j]:
                    cv2.circle(frame, (x, y), 1, POINT_COLOR, -1)

            left_eye = shape[l_start:l_end]
            right_eye = shape[r_start:r_end]

            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)

            ear = (left_ear + right_ear) / 2.0

            left_eye_hull = cv2.convexHull(left_eye)
            right_eye_hull = cv2.convexHull(right_eye)
            cv2.drawContours(frame, [left_eye_hull], -1, EYES_COLOR, 1)
            cv2.drawContours(frame, [right_eye_hull], -1, EYES_COLOR, 1)

            if ear < EYE_AR_THRESH:
                COUNTER += 1
                if args['activity'] == 2:
                    ASLEEP = True
            else:
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    if args['activity'] == 1:
                        TOTAL += 1
                COUNTER = 0
                ASLEEP = False
            
            if args['activity'] == 1:
                cv2.putText(
                    frame, 
                    f'Blinks: {TOTAL}',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, TEXT_COLOR, 2
                )
            
            if args['activity'] == 2:
                if ASLEEP:
                    cv2.putText(
                        frame, 
                        f'The person is sleeping!',
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, RED, 2
                    )
                else:
                    cv2.putText(
                        frame, 
                        f'The person is paying attention.',
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, GREEN, 2
                    )
        
        end = time.time()
        print(f' * Time for estimation: {end - start} ')

        
        # Display the resulting frame
        cv2.imshow('Sleeping detection...', frame)
        cv2.imshow('Original image', original)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()