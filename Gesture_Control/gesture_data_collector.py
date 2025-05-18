# This file is for adding a new gesture points in the JSON file 
# YOU CAN ADD THE GESTURE ACTION BY ADDING IT`S NAME IN THE MAIN FUNCTION (SINGLE HAND GESTURE)


import cv2
import json
from cvzone.HandTrackingModule import HandDetector

# Init camera and hand detector
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.7, maxHands=1)

# Load existing gestures if available
try:
    with open("gesture_control/gestures.json", "r") as f:
        gestures_dict = json.load(f)
except FileNotFoundError:
    gestures_dict = {}

print("Press [s] to save one gesture and exit.")

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)

        # Show the finger pattern on screen
        cv2.putText(img, f"Fingers: {fingers}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Gesture Collector", img)
    key = cv2.waitKey(1)

    # Save gesture and exit
    if key == ord('s') and hands:
        gesture_name = input("Enter gesture name: ")
        gestures_dict[gesture_name] = fingers
        print(f"Saved gesture '{gesture_name}': {fingers}")

        # Show all saved gestures
        print("All saved gestures:")
        for name, pattern in gestures_dict.items():
            print(f"{name}: {pattern}")

        # Save to file and exit
        with open("gesture_control/gestures.json", "w") as f:
            json.dump(gestures_dict, f, indent=4)

        break  # Exit loop after saving one gesture

cap.release()
cv2.destroyAllWindows()
