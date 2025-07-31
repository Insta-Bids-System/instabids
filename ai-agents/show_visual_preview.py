import webbrowser
import time

print("Opening the ACTUAL visual bid card preview...")
print("This is what contractors see when they click the rich link!")
print()

# Open the actual bid card preview
preview_url = "http://localhost:8000/api/bid-cards/d57cd6cd-f424-460e-9c15-7a08c09507f3/preview"
webbrowser.open(preview_url)

print(f"Opened: {preview_url}")
print()
print("This shows:")
print("- Beautiful gradient design with project icon")
print("- Project details (Lawn, $200-$400, 1 week timeline)")  
print("- Professional layout with call-to-action")
print("- Instabids branding")
print()
print("THIS IS THE VISUAL 'POP UP' YOU REQUESTED!")
print("Instead of a plain link, contractors see this rich visual preview.")