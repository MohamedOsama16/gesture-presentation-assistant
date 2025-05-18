# This file is for extract your camera calibration parameters

import cv2
import numpy as np
import os

def load_calibration(calibration_file):
    """
    Load camera calibration data from a file.
    
    Args:
        calibration_file: Path to the calibration file
        
    Returns:
        camera_matrix: Camera matrix
        dist_coeff: Distortion coefficients
    """
    try:
        with np.load(calibration_file) as data:
            camera_matrix = data['mtx']
            dist_coeff = data['dist']
        return camera_matrix, dist_coeff
    except Exception as e:
        print(f"Error loading calibration data: {e}")
        # Return identity matrix and zeros as default values
        return np.eye(3), np.zeros((1, 5))

def calibrate_camera(chessboard_dims=(9, 6), min_frames=10):
    """
    Calibrate camera using a chessboard pattern.
    
    Args:
        chessboard_dims: Dimensions of the chessboard (columns, rows)
        min_frames: Minimum number of frames to use for calibration
        
    Returns:
        bool: True if calibration was successful, False otherwise
    """
    # Prepare object points like (0,0,0), (1,0,0), ..., (8,5,0)
    obj_points = np.zeros((chessboard_dims[0] * chessboard_dims[1], 3), np.float32)
    obj_points[:, :2] = np.mgrid[0:chessboard_dims[0], 0:chessboard_dims[1]].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images
    obj_points_arr = []
    img_points_arr = []

    # Open the camera
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Failed to open camera.")
        return False

    print("Press 'q' to quit after collecting enough frames.")
    print("Press 'c' to capture a frame for calibration.")

    frames_collected = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Find the chessboard corners
        ret_corners, corners = cv2.findChessboardCorners(gray, chessboard_dims, None)

        # Display frame with chessboard corners if found
        display_frame = frame.copy()
        if ret_corners:
            cv2.drawChessboardCorners(display_frame, chessboard_dims, corners, ret_corners)
            status_text = "Chessboard detected! Press 'c' to capture."
        else:
            status_text = "No chessboard detected."
        
        # Show frames collected
        cv2.putText(display_frame, f"Frames: {frames_collected}/{min_frames}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_frame, status_text, 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Show the current frame
        cv2.imshow("Camera Calibration", display_frame)

        key = cv2.waitKey(1) & 0xFF
        # Capture frame on 'c' if chessboard is detected
        if key == ord('c') and ret_corners:
            obj_points_arr.append(obj_points)
            img_points_arr.append(corners)
            frames_collected += 1
            print(f"Frame {frames_collected}/{min_frames} captured.")
        
        # If enough frames collected, calibrate
        if frames_collected >= min_frames:
            print("Calibrating camera...")
            ret_calib, mtx, dist, _, _ = cv2.calibrateCamera(
                obj_points_arr, img_points_arr, gray.shape[::-1], None, None
            )

            if ret_calib:
                print("✅ Calibration successful!")
                print("🔹 Camera Matrix:\n", mtx)
                print("🔹 Distortion Coefficients:\n", dist)

                # Save to file
                np.savez("calibration/calibration_data.npz", mtx=mtx, dist=dist)
                print("📁 Calibration data saved to 'calibration/calibration_data.npz'")
                cam.release()
                cv2.destroyAllWindows()
                return True
            else:
                print("❌ Calibration failed.")
                cam.release()
                cv2.destroyAllWindows()
                return False

        # Exit on 'q'
        if key == ord("q"):
            break

    # Cleanup
    cam.release()
    cv2.destroyAllWindows()
    return False

if __name__ == "__main__":
    # Make sure calibration directory exists
    os.makedirs("calibration", exist_ok=True)
    
    # Run calibration
    calibrate_camera()