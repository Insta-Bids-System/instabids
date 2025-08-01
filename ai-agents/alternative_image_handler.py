#!/usr/bin/env python3
"""
Alternative image handling approach - save to local file system
and serve via FastAPI
"""

import os
import base64
import uuid
from datetime import datetime
from pathlib import Path

class LocalImageHandler:
    """Handle images locally when Supabase Storage is not available"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Use project's static directory
            base_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def save_image(self, base64_image: str, user_id: str) -> str:
        """Save base64 image to local file system and return URL"""
        try:
            # Decode base64
            image_data = base64.b64decode(base64_image)
            
            # Create user directory
            user_dir = self.base_path / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            filename = f"{timestamp}_{unique_id}.jpg"
            
            # Save file
            file_path = user_dir / filename
            with open(file_path, 'wb') as f:
                f.write(image_data)
                
            # Return URL path (will be served by FastAPI)
            url = f"/static/uploads/{user_id}/{filename}"
            
            print(f"[LocalStorage] Saved image to: {file_path}")
            print(f"[LocalStorage] URL: {url}")
            
            return url
            
        except Exception as e:
            print(f"[LocalStorage] Error saving image: {e}")
            raise
            
    def delete_image(self, url: str) -> bool:
        """Delete image from local storage"""
        try:
            # Extract path from URL
            path_parts = url.split('/static/uploads/')[-1]
            file_path = self.base_path / path_parts
            
            if file_path.exists():
                file_path.unlink()
                print(f"[LocalStorage] Deleted: {file_path}")
                return True
            return False
            
        except Exception as e:
            print(f"[LocalStorage] Error deleting image: {e}")
            return False


# Usage in CIA agent:
"""
# In CIA agent's handle_conversation method:

# If Supabase storage fails, use local storage
if "row-level security" in str(e):
    print(f"[CIA] Using local storage fallback")
    
    # Initialize local handler
    local_handler = LocalImageHandler()
    
    # Save images locally
    for idx, base64_image in enumerate(images):
        try:
            url = local_handler.save_image(base64_image, user_id)
            image_urls.append(f"http://localhost:8008{url}")
        except Exception as local_e:
            print(f"[CIA] Local storage also failed: {local_e}")
            continue
"""

# Add to main.py to serve static files:
"""
# In main.py after app initialization:

# Serve uploaded images
static_path = os.path.join(os.path.dirname(__file__), '..', 'static')
if not os.path.exists(static_path):
    os.makedirs(static_path, exist_ok=True)
    
app.mount("/static", StaticFiles(directory=static_path), name="static")
print(f"[OK] Static files mounted from: {static_path}")
"""