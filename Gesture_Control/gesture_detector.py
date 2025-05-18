import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector as CVZoneHandDetector
import json

class GestureDetector:
    def __init__(self, detection_confidence=0.7, max_hands=2):
        """
        Initialize the hand gesture detector.
        
        Args:
            detection_confidence: Confidence threshold for hand detection
            max_hands: Maximum number of hands to detect
        """
        self.detector = CVZoneHandDetector(detectionCon=detection_confidence, maxHands=max_hands)
        
        # Define gesture patterns
        with open("gesture_control/gestures.json", "r") as f:
            self.gestures_dict = json.load(f)

    
    def find_hands(self, img, draw=True):
        """
        Find hands in the image.
        
        Args:
            img: Input image
            draw: Whether to draw landmarks on the image
            
        Returns:
            hands: List of detected hands with landmarks
            img: Image with landmarks drawn if draw=True
        """
        return self.detector.findHands(img, flipType=True, draw=draw)
    
    def process_gesture(self, hand):
        """
        Process hand gesture to determine the intended action.
        
        Args:
            hand: Hand object with landmarks from the detector
            
        Returns:
            action: Detected action name or None if no match
        """
        gesture = self.detector.fingersUp(hand)
        
        for action, pattern in self.gestures_dict.items():
            if gesture == pattern:
                return action
        
        return None
    
    def process_zoom_gesture(self, hands, img, cam_dims, pres_dims):
        """
        Process zoom gesture when two hands are detected.
        
        Args:
            hands: List of detected hands with landmarks
            img: Input image
            cam_dims: Camera dimensions (width, height)
            pres_dims: Presentation dimensions (width, height)
            
        Returns:
            pt1, pt2: Points between hands
            mid_pt: Middle point between hands
            zoom_factor: Calculated zoom factor or -1 if not a zoom gesture
        """
        if len(hands) != 2:
            return None, None, None, -1
            
        gesture1 = self.detector.fingersUp(hands[0])
        gesture2 = self.detector.fingersUp(hands[1])
        
        # Check if both hands show three fingers up (thumb, index, middle)
        if gesture1 == [1, 1, 1, 0, 0] and gesture2 == [1, 1, 1, 0, 0]:
            pt1 = hands[0]['lmList'][5][:2]  # Base of index finger
            pt2 = hands[1]['lmList'][5][:2]  # Base of index finger
            
            mid_pt = (int((pt1[0] + pt2[0]) / 2), int((pt1[1] + pt2[1]) / 2))
            
            cv2.line(img, pt1, pt2, (0, 255, 0), 2)
            
            # Calculate distance between hands for zoom factor
            dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
            zoom_factor = min(max(dist / 100, 1), 2)  # Limit zoom between 1x and 2x
            
            return pt1, pt2, mid_pt, zoom_factor
            
        return None, None, None, -1