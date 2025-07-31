import webbrowser
import time

print("OPENING REAL INLINE PREVIEW TEST")
print("=" * 50)
print("This will show you the ACTUAL working inline preview!")
print("The JavaScript will automatically detect the bid card URL")
print("and create a visual preview card below it.")
print()

# Open the real test page
test_url = "http://localhost:8000/test/real-preview"
webbrowser.open(test_url)

print(f"Opened: {test_url}")
print()
print("WHAT YOU SHOULD SEE:")
print("1. Email message with bid card URL")
print("2. JavaScript automatically creates visual preview card")
print("3. Preview card shows project details INLINE")
print("4. No clicking required - preview appears automatically!")
print()
print("THIS IS THE REAL INLINE PREVIEW FUNCTIONALITY!")
print("The bid card appears as a visual card within the message!")