import cv2
import numpy as np

def draw_on_display(display, drawings_log, color):
    """
    Draw annotations on the display from the drawing log.
    
    Args:
        display: Display image to draw on
        drawings_log: List of drawing points
        color: Color to use for drawing
    """
    for drawing in drawings_log:
        cv2.circle(display, drawing, 5, color, -1)

def display_mouse_pad(img, header_text, transparency_factor=0.8, mpad_color=(128, 128, 128), top_left=(0, 0), size=None):
    """
    Display a mouse pad area on the image.
    
    Args:
        img: Image to display mouse pad on
        header_text: Text to display on the mouse pad
        transparency_factor: Transparency of the mouse pad
        mpad_color: Color of the mouse pad
        top_left: Top left corner of the mouse pad
        size: Size of the mouse pad (width, height)
        
    Returns:
        Tuple of top left and bottom right coordinates of the mouse pad
    """
    overlay = img.copy()

    x, y = top_left

    # Default size: half the frame width and height if not provided
    if size is None:
        width = img.shape[1] // 2
        height = img.shape[0] // 2
    else:
        width, height = size

    # Bottom-right corner
    x2 = x + width
    y2 = y + height

    # Draw rectangle
    cv2.rectangle(overlay, (x, y), (x2, y2), mpad_color, -1)

    # Blend with original image
    cv2.addWeighted(overlay, transparency_factor, img, 1 - transparency_factor, 0, img)

    # Draw label
    cv2.putText(img, header_text, (x + 5, y + 20), cv2.FONT_HERSHEY_PLAIN, 1, (50, 50, 50), 2)

    return (x, y), (x2, y2)

def map_cam_to_slide(point, cam_dims, pres_dims):
    """
    Map a point from camera coordinates to slide coordinates.
    
    Args:
        point: Point in camera coordinates (x, y)
        cam_dims: Camera dimensions (width, height)
        pres_dims: Presentation dimensions (width, height)
        
    Returns:
        Point in slide coordinates (x, y)
    """
    mapped_pt = (
        int(point[0] * (pres_dims[0] / cam_dims[0])),
        int(point[1] * (pres_dims[1] / cam_dims[1]))
    )
    return mapped_pt

def display_status(img, text, position=(10, 30), color=(0, 255, 0), font_scale=2, thickness=2):
    """
    Display status text on the image.
    
    Args:
        img: Image to display text on
        text: Text to display
        position: Position of the text
        color: Color of the text
        font_scale: Font scale
        thickness: Text thickness
    """
    cv2.putText(img, text, position, cv2.FONT_HERSHEY_PLAIN, font_scale, color, thickness)