import cv2
import numpy as np
import os
from Gesture_Control.gesture_detector import GestureDetector
from Calibration.camera_calibration import load_calibration
from Feedback.visual_feedback import draw_on_display, display_mouse_pad
from Feedback.voice_feedback import VoiceFeedback
from Integration.slides_integration import load_slides, map_pointer_to_slide
from Authentication.authenticator import authenticate_user
import time


auth_face_img_path = 'D:\\Mohamed\\Mohamed Osama\\Gesture Presentation Assistant\\Authentication\\Mohamed_Osama.jpg'  # غيّر المسار لو الصورة في مكان تاني


# ------------------- Presentation and Camera Settings -------------------
PRES_DIMS = (1200, 600)  # Presentation slide size
CAM_DIMS = (250, 250)     # Webcam feed size


def main():
    # ------------------- Load Camera Calibration -------------------
    camera_matrix, dist_coeff = load_calibration('Calibration/calibration_data.npz')

    # Load Slides
    ppt_path = r"D:\\Mohamed\\Mohamed Osama\\Gesture Presentation Assistant\\Gesture Presentation Test.pptx"
    try:
        slides_list = load_slides(ppt_path, PRES_DIMS)
        print(f"Loaded {len(slides_list)} slides")
        if len(slides_list) == 0:
            raise ValueError("No slides loaded. Please check the PPTX file path and contents.")
    except Exception as e:
        print(f"Failed to load slides: {e}")
        return

    # ------------------- Initialize Variables -------------------
    slide_num = 0
    change_slide = False
    drawings_log = []
    show_landmarks = True
    pointer_color = (0, 0, 255)
    annotation_color = (0, 0, 255)
    mpad_color = (128, 128, 128)
    allow_gestures = False

    # ------------------- Initialize Detectors and Feedback -------------------
    gesture_detector = GestureDetector(detection_confidence=0.7, max_hands=2)
    voice_feedback = VoiceFeedback()

    # ------------------- Open Webcam -------------------
    cap = cv2.VideoCapture(0)
    assert cap.isOpened(), "Can't access Camera device"

    print("Authenticating... Please look at the camera.")
    auth_success = False
    for _ in range(50):
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        cv2.imshow("Authentication", frame)
        cv2.waitKey(3)

        if authenticate_user(frame, auth_face_img_path):
            auth_success = True
            time.sleep(6)
            voice_feedback.speak("Authentication successful")
            print("Authentication successful.")
            break

    cv2.destroyWindow("Authentication")

    if not auth_success:
        voice_feedback.speak("Authentication failed")
        print("Authentication failed. Exiting.")
        cap.release()
        return

    voice_cooldown = False
    last_voice_time = 0

    running = True
    while running:
        ret, cam = cap.read()
        if not ret or cv2.waitKey(10) == ord("q"):
            break

        cam = cv2.undistort(cam, camera_matrix, dist_coeff)
        cam = cv2.resize(cam, CAM_DIMS)
        cam = cv2.flip(cam, 1)

        slide = slides_list[slide_num]
        display = slide.copy()

        hands, cam = gesture_detector.find_hands(cam, draw=show_landmarks)

        if hands:
            # ------------------- Zooming with Two Hands -------------------
            if len(hands) == 2:
                pt1, pt2, mid_pt, zoom_factor = gesture_detector.process_zoom_gesture(hands, cam, CAM_DIMS, PRES_DIMS)
                if zoom_factor > 0:
                    mapped_pt = (
                        int(mid_pt[0] * (PRES_DIMS[0] / CAM_DIMS[0])),
                        int(mid_pt[1] * (PRES_DIMS[1] / CAM_DIMS[1]))
                    )
                    zoom_w = int(PRES_DIMS[0] / zoom_factor)
                    zoom_h = int(PRES_DIMS[1] / zoom_factor)
                    x1 = max(mapped_pt[0] - zoom_w // 2, 0)
                    y1 = max(mapped_pt[1] - zoom_h // 2, 0)
                    x2 = min(mapped_pt[0] + zoom_w // 2, PRES_DIMS[0])
                    y2 = min(mapped_pt[1] + zoom_h // 2, PRES_DIMS[1])
                    zoomed_region = display[y1:y2, x1:x2]
                    display = cv2.resize(zoomed_region, PRES_DIMS)
                    cv2.putText(cam, f"x{zoom_factor:.2f}", mid_pt, cv2.FONT_HERSHEY_PLAIN, 2, (50, 50, 50), 2)
                    current_time = time.time()
                    if not voice_cooldown:
                        voice_feedback.speak("Zoom mode")
                        voice_cooldown = True
                        last_voice_time = current_time

            # ------------------- Single Hand Gestures -------------------
            if len(hands) > 0:
                _, cy = hands[0]['center']
                face_centerY = CAM_DIMS[1] // 2  # You can use fixed center if emotion logic removed
                allow_gestures = cy < face_centerY

                action = gesture_detector.process_gesture(hands[0])

                if action:
                    # --- Slide Change Actions ---
                    if action == "next" and not change_slide and slide_num < len(slides_list) - 1 and allow_gestures:
                        slide_num += 1
                        change_slide = True
                        voice_feedback.speak("Next slide")
                        print("Slide changed to next")

                    elif action == "prev" and not change_slide and slide_num > 0 and allow_gestures:
                        slide_num -= 1
                        change_slide = True
                        voice_feedback.speak("Previous slide")
                        print("Slide changed to previous")

                    else:
                        # Reset change_slide if current action is NOT next/prev so next gesture can trigger again
                        if action not in ["next", "prev"]:
                            change_slide = False

                    # --- Other gesture actions ---
                    if action == "pointer":
                        change_slide = False
                        landmarks = hands[0]['lmList']
                        index_tip = landmarks[8][:2]
                        p1, p2 = display_mouse_pad(cam, "Mouse Pad", 0.3, mpad_color, (cam.shape[1]-200, 0), (200, 150))
                        if p1[0] < index_tip[0] < p2[0] and p1[1] < index_tip[1] < p2[1]:
                            index_tip_on_slide = map_pointer_to_slide(index_tip, p1, p2[0] - p1[0], p2[1] - p1[1], PRES_DIMS)
                            cv2.circle(cam, index_tip, 4, (255, 255, 255), 2)
                            cv2.circle(display, index_tip_on_slide, 5, pointer_color, -1)
                            current_time = time.time()
                            if not voice_cooldown:
                                voice_feedback.speak("pointer mode")
                                voice_cooldown = True
                                last_voice_time = current_time

                    elif action == "draw":
                        change_slide = False
                        landmarks = hands[0]['lmList']
                        index_tip = landmarks[8][:2]
                        p1, p2 = display_mouse_pad(cam, "Draw Pad", 0.3, mpad_color, (cam.shape[1]-200, 0), (200, 150))
                        if p1[0] < index_tip[0] < p2[0] and p1[1] < index_tip[1] < p2[1]:
                            index_tip_on_slide = map_pointer_to_slide(index_tip, p1, p2[0]-p1[0], p2[1]-p1[1], PRES_DIMS)
                            cv2.circle(cam, index_tip, 4, annotation_color, 2)
                            drawings_log.append(index_tip_on_slide)
                            current_time = time.time()
                            if not voice_cooldown:
                                voice_feedback.speak("Draw mode")
                                voice_cooldown = True
                                last_voice_time = current_time

                    elif action == "erase" and allow_gestures:
                        change_slide = False
                        drawings_log.clear()

                    elif action == "end" and allow_gestures:
                        voice_feedback.speak("Ending presentation")
                        time.sleep(2)  # Wait 4 seconds before proceeding
                        print("Presentation ended by gesture")
                        running = False  # Control main loop exit
                        break

               
                    # For adding new gestures write here 

                    # elif action == "action_name":
                    #     pass
                    cv2.putText(cam, f"Gesture: {action}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        else:
            # No hands detected - reset change_slide so next/prev can be triggered again
            change_slide = False

        draw_on_display(display, drawings_log, annotation_color)

        cv2.imshow("Camera", cam)
        cv2.imshow("Slide", display)

        if voice_cooldown and (time.time() - last_voice_time >= 10):
            voice_cooldown = False

    cv2.destroyAllWindows()
    cap.release()


if __name__ == "__main__":
    main()
