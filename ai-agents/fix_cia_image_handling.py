#!/usr/bin/env python3
"""
Fix to add image handling to CIA agent
This shows what needs to be added to the CIA agent to properly handle images
"""

# The fix needs to be added in the handle_conversation method after the message is added

# CURRENT CODE (around line 230):
# state["messages"].append({
#     "role": "user",
#     "content": message,
#     "images": images,
#     "metadata": {"timestamp": datetime.now().isoformat()}
# })

# ADD THIS CODE RIGHT AFTER:
def add_images_to_collected_info(state, images):
    """Add uploaded images to collected_info"""
    if images and len(images) > 0:
        # Add images to the uploaded_photos field
        if 'collected_info' in state:
            state['collected_info']['uploaded_photos'] = images
            print(f"[CIA] Added {len(images)} photos to collected_info")
            
            # Could also add placeholder photo analyses
            state['collected_info']['photo_analyses'] = []
            for img_url in images:
                state['collected_info']['photo_analyses'].append({
                    'url': img_url,
                    'description': 'Photo uploaded by user',
                    'identified_issues': [],
                    'estimated_scope': 'To be analyzed',
                    'areas_of_concern': [],
                    'confidence': 0.0
                })


# The fix location in agents/cia/agent.py would be around line 235:
# After:
#     state["messages"].append({
#         "role": "user",
#         "content": message,
#         "images": images,
#         "metadata": {"timestamp": datetime.now().isoformat()}
#     })
#
# Add:
#     # Store images in collected_info
#     if images and len(images) > 0:
#         state['collected_info']['uploaded_photos'] = images
#         print(f"[CIA] Added {len(images)} photos to collected_info")


print("FIX FOR CIA IMAGE HANDLING")
print("="*50)
print("\nThe CIA agent needs to be updated to store images in collected_info.")
print("\nIn agents/cia/agent.py, after adding the message (around line 234):")
print("\nADD THIS CODE:")
print("""
    # Store images in collected_info
    if images and len(images) > 0:
        state['collected_info']['uploaded_photos'] = images
        print(f"[CIA] Added {len(images)} photos to collected_info")
""")
print("\nThis will ensure images flow through to JAA and bid cards.")