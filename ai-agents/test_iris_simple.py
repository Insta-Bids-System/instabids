from api.demo_iris import generate_smart_fallback_response, IrisChatRequest

# Test the function directly
request = IrisChatRequest(
    message="Generate a kitchen with modern cabinets",
    homeowner_id="550e8400-e29b-41d4-a716-446655440001",
    board_id="26cf972b-83e4-484c-98b6-a5d1a4affee3"
)

# Test with generation request
print("Testing image generation...")
result = generate_smart_fallback_response(request.message, True, request)
print(f"Result keys: {result.keys()}")
print(f"Image generated: {result.get('image_generated', False)}")
print(f"Image URL: {result.get('image_url', 'None')}")
print(f"Response preview: {result['response'][:200]}...")
