from tools.tools import eye_processor

import argparse
import time


def parser():
    """Argument parser function."""

    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--shape-predictor', type=str,
        default='./data/shape_predictor_68_face_landmarks.dat',
        help='Path to facial landmark predictor')
    ap.add_argument('-a', '--activity', type=int, default=1,
        help='Set activity: \n (1) Count blinks \n (2) Track person asleep')
    ap.add_argument('-v', '--verbose', type=bool, default=False,
        help='Display action messages in console')
    args = vars(ap.parse_args())

    return args


if __name__ == '__main__':
    args = parser()
    eye_processor(args)