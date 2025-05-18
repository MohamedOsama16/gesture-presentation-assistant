import cv2
import numpy as np
import os
from spire.presentation.common import *
from spire.presentation import *

def load_slides(ppt_path, dims=None):
    """
    Convert PowerPoint presentation to a list of images.

    Args:
        ppt_path: Path to the PowerPoint presentation file
        dims: Dimensions to resize slides to (width, height)

    Returns:
        List of slide images
    """
    slides_list = []

    presentation = Presentation()

    try:
        # Load PowerPoint presentation
        presentation.LoadFromFile(ppt_path)

        # Loop through the slides in the presentation
        for i, slide in enumerate(presentation.Slides):
            # Save each slide as an image
            image = slide.SaveAsImage()

            # Convert to numpy array
            image_bytes = image.ToArray()
            image_np = np.frombuffer(image_bytes, dtype=np.uint8)
            image_np = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            # Resize if dimensions are provided
            if dims:
                image_np = cv2.resize(image_np, dims)

            # ✅ Append to slide list
            slides_list.append(image_np)

            # Clean up resources
            image.Dispose()

    except Exception as e:
        print(f"Error loading presentation: {e}")

    # Dispose the presentation object
    presentation.Dispose()

    return slides_list


def map_pointer_to_slide(point, mpad_upperleft, mpad_width, mpad_height, pres_dims):
    """
    Map a point from mousepad coordinates to slide coordinates.
    
    Args:
        point: Point in mousepad coordinates (x, y)
        mpad_upperleft: Upper left corner of mousepad (x, y)
        mpad_width: Width of mousepad
        mpad_height: Height of mousepad
        pres_dims: Presentation dimensions (width, height)
        
    Returns:
        Point in slide coordinates (x, y)
    """
    mapped_pt = (
        int((point[0] - mpad_upperleft[0]) * (pres_dims[0] / mpad_width)),
        int((point[1]) * (pres_dims[1] / mpad_height))
    )
    return mapped_pt