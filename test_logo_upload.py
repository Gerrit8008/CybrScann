#!/usr/bin/env python3

import os
import requests
import tempfile
from PIL import Image

def test_logo_upload():
    """Test logo upload functionality"""
    
    # Create a simple test logo image
    img = Image.new('RGB', (200, 50), color='blue')
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        img.save(tmp.name, 'PNG')
        test_image_path = tmp.name
    
    try:
        print(f"Created test image: {test_image_path}")
        print(f"File exists: {os.path.exists(test_image_path)}")
        print(f"File size: {os.path.getsize(test_image_path)} bytes")
        
        # Check if uploads directory exists
        uploads_dir = 'static/uploads'
        print(f"Uploads directory exists: {os.path.exists(uploads_dir)}")
        
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            print(f"Created uploads directory: {uploads_dir}")
        
        # Test file handling without Flask
        from werkzeug.utils import secure_filename
        import time
        
        filename = secure_filename('test_logo.png')
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        unique_filename = f"logo_{timestamp}_{name}{ext}"
        
        print(f"Generated filename: {unique_filename}")
        
        # Copy test file to uploads directory
        import shutil
        destination = os.path.join(uploads_dir, unique_filename)
        shutil.copy2(test_image_path, destination)
        
        print(f"Test logo saved to: {destination}")
        print(f"Destination exists: {os.path.exists(destination)}")
        
        # Clean up
        os.unlink(test_image_path)
        
        return destination
        
    except Exception as e:
        print(f"Error testing logo upload: {e}")
        # Clean up on error
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)
        return None

if __name__ == "__main__":
    result = test_logo_upload()
    if result:
        print(f"✅ Logo upload test successful: {result}")
    else:
        print("❌ Logo upload test failed")