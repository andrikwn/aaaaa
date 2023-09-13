import cv2
import os
import time
import psutil
import subprocess
import json
from datetime import datetime, timedelta

desired_cores = [0]

psutil.Process(os.getpid()).cpu_affinity(desired_cores)

# Create the initial JSON file if it doesn't exist with default value "alert : kosong"
json_file_path = 'notif.json'
if not os.path.exists(json_file_path):
    with open(json_file_path, 'w+') as json_file:
        default_data = {'alert': 'kosong'}
        json.dump(default_data, json_file)

subprocess.Popen(["python3", "sensordatabase.py"])

def record():
    cap = cv2.VideoCapture(1)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    folder = "video"
    snap_folder = "snapshot"

    while True:
        waktu_sekarang = datetime.now()
        dayfolder = waktu_sekarang.strftime("%Y%m%dT000000Z")
        subfolder = waktu_sekarang.strftime("%Y%m%dT%H0000Z")
        targetfolder = os.path.join(folder, dayfolder, subfolder)
        snap_subfolder = waktu_sekarang.strftime("%Y%m%dT%H0000Z")
        snap_targetfolder = os.path.join(snap_folder, dayfolder, snap_subfolder)

        if not os.path.exists(targetfolder):
            os.makedirs(targetfolder)
        if not os.path.exists(snap_targetfolder):
            os.makedirs(snap_targetfolder)

        a = waktu_sekarang.replace(second=1, microsecond=0)
        b = waktu_sekarang.replace(second=59, microsecond=999999)

        timefilename = a.strftime("%Y%m%dT%H%M00Z")
        filename = os.path.join(targetfolder, f"{timefilename}.avi")

        out = cv2.VideoWriter(filename, fourcc, 10, (480, 320))

        while datetime.now() <= b:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)

            # Read and update the JSON file
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)
                if 'snap now' in data and data['snap now'] == 'yes':
                    # Take a snapshot
                    snap_sec = datetime.now().strftime("%Y%m%dT%H%M%SZ")
                    snap_filename = os.path.join(snap_targetfolder, f"{snap_sec}.jpg")
                    cv2.imwrite(snap_filename, frame)
                    
                    # Change the JSON value to "alert : kosong"
                    data['snap now'] = 'no'
                    data['snap'] = snap_sec + '.jpg'
                    data['video'] = timefilename + '.mp4'
                    
                    # Write the updated JSON back to the file
                    with open(json_file_path, 'w+') as updated_json_file:
                        json.dump(data, updated_json_file, indent=4)
            out.write(frame)
            time.sleep(0.06)

        out.release()
        subprocess.Popen(["python3", "compress.py"])

if __name__ == "__main__":
    if not os.path.exists("video"):
        os.makedirs("video")
    if not os.path.exists("snapshot"):
        os.makedirs("snapshot")

    record()
