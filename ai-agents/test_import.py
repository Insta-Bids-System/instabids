try:
    from api.image_generation import generate_dream_space, GenerateDreamSpaceRequest
    print("Import successful")
    
    # Test creating a request
    req = GenerateDreamSpaceRequest(
        board_id="test",
        ideal_image_id="test1",
        current_image_id="test2",
        user_preferences="test"
    )
    print(f"Request created: {req}")
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()