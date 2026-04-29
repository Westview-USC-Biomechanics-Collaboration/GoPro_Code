# -*- coding: utf-8 -*-
"""

"""
import asyncio
import serial
import serial.tools.list_ports
import threading
import numpy as np
import pandas as pd
import json
import time
from datetime import datetime
import os
from open_gopro import WiredGoPro
from open_gopro.models import constants



# Create local path for saving video
local_folder = r"C:\GoPro_Downloads"
#local_folder = r"C:\VEnv312\GoPro_Testing\DownloadVideos"


# Create dictionary listing the cameras available
# Key = the Camera View
# Value = serial number of the camera to use for the view
dict_cameras = {'Top': 'C3534250578396',
                'SideA': 'C3534250766732',
                'SideB': 'C3534250766732',
                'Front': 'C3535424535389'}

# dict_cameras_wv = {'Top': 'C3534250578396',
#                 'SideA': 'C3534250766732',
#                 'SideB': 'C3534250766732'}

# dict_cameras_rongey = {'Top': 'C3534250728378',
#                 'SideA': 'C3534250759526',
#                 'SideB': 'C3534250759526'}

#------------------------------------------------------------------------------
def get_file_prefix(local_folder):
    # Get current timestamp to use for prefix of filename
    current_time = datetime.now()
    # Convert to: YYYYMMDD_ HHMMSS format
    file_prefix = current_time.strftime("%Y%m%d_%H%M%S")
    return file_prefix
#------------------------------------------------------------------------------

async def top_view_camera(sn):
    print('Top view connceting to: ' + str(sn))
    gopro_top = WiredGoPro(sn)
    await gopro_top.open()
    return gopro_top
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
async def sideB_view_camera(sn):
    print('SideB view connceting to: ' + str(sn))
    gopro_sideB = WiredGoPro(sn)
    await gopro_sideB.open()
    return gopro_sideB
#------------------------------------------------------------------------------
async def front_view_camera(sn):
    print('Front view connceting to: ' + str(sn))
    gopro_front = WiredGoPro(sn)
    await gopro_front.open()
    return gopro_front
#------------------------------------------------------------------------------
async def get_camera_info(gopro):
    # Get info
    camera_info = await gopro.http_command.get_camera_info()
    print("Camera Info:")
    print(camera_info)
    return camera_info
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
async def get_camera_config(gopro):
    # Get all info related to camera state
    camera_state = await gopro.http_command.get_camera_state()
    print(camera_state.data[constants.settings.SettingId.FRAMES_PER_SECOND].name)
    print(camera_state.data[constants.settings.SettingId.VIDEO_RESOLUTION].name)
    print(camera_state.data[constants.settings.SettingId.VIDEO_LENS].name)
    print(camera_state.data[constants.settings.SettingId.VIDEO_FRAMING].name)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
async def record_video(gopro_list, local_folder, current_experiment):
    try:
        #-- gopro_list is list of tuples: (gopro object, view as a string) --#

        ### Get timestamp for annotating files
        file_prefix = get_file_prefix(local_folder)

        ### Start Recording
        for case in gopro_list:
            gopro = case[0]
            view = case[1]
            await gopro.http_command.set_shutter(shutter=constants.Toggle.ENABLE)
            print('Recording started for ' + view)

        ### Prompt user to stop recording
        input('----- Press Enter to stop recording-----')

        ### Stop Recording
        for case in gopro_list:
            gopro = case[0]
            view = case[1]
            await gopro.http_command.set_shutter(shutter=constants.Toggle.DISABLE)
            print('Recording stopped for ' + view)

        ### Save files
        for case in gopro_list:
            gopro = case[0]
            view = case[1]

            # Find the video on the GoPro that was just captured
            video = await gopro.http_command.get_last_captured_media()
            gopro_file = video.data.folder + '/' + video.data.file
            print(gopro_file)

            # Download video from GoPro to the local computer
            # Save it using the timestamped filename created when recording started
            # Print the path where the file was saved
            new_file_path = os.path.join(local_folder, file_prefix + '_{' + current_experiment + '}_' + view + '.MP4')
            path_used = await gopro.http_command.download_file(camera_file=gopro_file, local_file=new_file_path)
            print(path_used)

    except Exception as e:
        print(f"An error occurred: {e}")
#------------------------------------------------------------------------------


#------------------ Main Control for Recording Videos -------------------------
async def main_control(local_folder):
    #-- Allow user to update the local folder path and camera serian numbers --
    print('')
    print('--------- STARTING GOPRO CONTROL SCRIPT -----------------')
    print('')
    print('Current local folder path is: ' + local_folder)
    new_local_folder = input('Provide new local folder path, or hit ENTER to use current path: ')
    print(new_local_folder)
    if new_local_folder != '':
        local_folder = new_local_folder
    print('')
    print('Current Front View SN is: ' + dict_cameras['Front'])
    new_front_sn = input('Provide Front View SN, or hit ENTER to use current SN: ')
    print(new_front_sn)
    if new_front_sn != '':
        dict_cameras['Front'] = new_front_sn
    print('Current Top View SN is: ' + dict_cameras['Top'])
    new_top_sn = input('Provide Top View SN, or hit ENTER to use current SN: ')
    print(new_top_sn)
    if new_top_sn != '':
        dict_cameras['Top'] = new_top_sn
    print('Current Side View SN is: ' + dict_cameras['SideB'])
    new_side_sn = input('Provide Side View SN, or hit ENTER to use current SN: ')
    print(new_side_sn)
    if new_side_sn != '':
        dict_cameras['SideA'] = new_side_sn
        dict_cameras['SideB'] = new_side_sn

    #------- Connect to the cameras and show the info and config settings -----
    gopro_front = await front_view_camera(dict_cameras['Front'])
    gopro_top = await top_view_camera(dict_cameras['Top'])
    gopro_sideB = await sideB_view_camera(dict_cameras['SideB'])

    await get_camera_info(gopro_top)
    await get_camera_info(gopro_sideB)
    await get_camera_info(gopro_front)

    print('----- Configutation of Top View Camera -----')
    await get_camera_config(gopro_top)

    print('----- Configutation of SideB View Camera -----')
    await get_camera_config(gopro_sideB)

    print('----- Configutation of Front View Camera -----')
    await get_camera_config(gopro_front)
    #--------------------------------------------------------------------------


    #------------- Loop for recording videos for multiple experiments ---------
    current_experiment = ''
    while True:
        # Determine if quitting or experiment name needs updating
        print('Current Experiment = ' + current_experiment)
        new_experiment = input('Provide experiment name (Enter to keep current name), or q to quit: ')
        print(new_experiment)
        if new_experiment == 'q':
            break
        if new_experiment != '':
            current_experiment = new_experiment



        ### Record videos on both cameras
        # Run the function to record a video
        print('')
        input('Press Enter To Start Recording')
        list_gopro_view = [(gopro_top, 'Top'),
                            (gopro_sideB, 'SideB'),
                             (gopro_front, 'Front')]
        await record_video(list_gopro_view, local_folder, current_experiment)
    #--------------------------------------------------------------------------
#------------------------------------------------------------------------------


# Needed to run as stand-alone (i.e., not from IDE)
def entrypoint() -> None:
    asyncio.run(main_control(local_folder))

if __name__ == "__main__":
