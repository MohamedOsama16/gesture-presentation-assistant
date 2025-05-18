from deepface import DeepFace

def authenticate_user(frame, auth_face_img_path):
    try:
        result = DeepFace.verify(frame, auth_face_img_path, enforce_detection=False)
        return result['verified']
    except Exception as e:
        print(f"Authentication error: {e}")
        return False