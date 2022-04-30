import os
from turtle import color
import matplotlib
from Realsense.realsense_depth import *
from Realsense.realsense import *
from Algorithm.main import *
import cv2
import time
import argparse
from UART import uart_server

matplotlib.use('TKAgg')
# Disable tensorflow output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def det_move_(obj_x_coord, obj_y_coord, xres, yres):
    centerx, centery = xres/2, yres/2

    move_x = obj_x_coord-centerx
    move_y = obj_y_coord-centery
    if(move_x != 0):
        move_x /= abs(obj_x_coord-centerx)
    if(move_y != 0):
        move_y /= abs(obj_y_coord-centery)
    return(move_x, move_y)


def main(_argv):
    parser = argparse.ArgumentParser()
    # Initialize Camera Intel Realsense
    dc = DepthCamera()
    uartServer = uart_server()

    Debug_flag = 0

    # Parse arguments
    if _argv.Debug == "1" or _argv.D == "1":
        Debug_flag = 1
        # Create window for video
        cv2.namedWindow("Video")
        cv2.namedWindow("Video_Depth")

    elif _argv.Debug == "0" or _argv.D == "0":
        Debug_flag = 0

    # Load saved CV model
    model = get_model()

    # Initialize Algorithm
    oldCords = None
    depth = None

    while True:
        # Start Video Capture
        ret, depth_frame, color_frame = dc.get_frame()

        # If frame is not empty
        if ret:

            key = cv2.waitKey(1)
            if key == 27:
                break

            # Get coordinates from color frame
            coordinates = get_coordinates(color_frame, model)

            if coordinates != None:
                # Get Median Depth from depth frame
                depth = process_frame(
                    depth_frame, coordinates[0], coordinates[1], coordinates[2], coordinates[3])

                # Debug mode
                if Debug_flag == 1:
                    print(coordinates)
                    print(coordinates)
                    print(depth)
                    show_frame(color_frame, depth_frame, depth, coordinates)

                uartServer.send_data(
                    det_move_((coordinates[0]+coordinates[2])/2,
                              (coordinates[1]+coordinates[3])/2),
                    dc.xres, dc.yres)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
