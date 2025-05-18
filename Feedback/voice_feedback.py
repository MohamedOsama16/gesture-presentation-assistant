import pyttsx3

class VoiceFeedback:
    def __init__(self, rate_adjust=-50, volume=1.0, voice_index=1):
        """
        Initialize voice feedback system.
        
        Args:
            rate_adjust: Adjustment to speech rate (-50 means slower)
            volume: Volume of speech (0.0 to 1.0)
            voice_index: Voice index (0 for male, 1 for female typically)
        """
        self.engine = pyttsx3.init()
        
        # Set speech parameters
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate + rate_adjust)  # Adjust speed
        self.engine.setProperty('volume', volume)  # Set volume
        
        # Set voice (female by default)
        voices = self.engine.getProperty('voices')
        if len(voices) > voice_index:
            self.engine.setProperty('voice', voices[voice_index].id)
    
    def speak(self, text):
        """
        Speak the given text.
        
        Args:
            text: Text to speak
        """
        self.engine.say(text)
        self.engine.runAndWait()

    def announce_gesture(self, gesture_name):
        """
        Announce the detected gesture.
        
        Args:
            gesture_name: Name of the detected gesture
        """
        self.speak(f"{gesture_name} gesture detected")
    
    def announce_slide_change(self, direction):
        """
        Announce slide change.
        
        Args:
            direction: Direction of slide change ("next" or "prev")
        """
        if direction == "next":
            self.speak("Next slide")
        elif direction == "prev":
            self.speak("Previous slide")
    
