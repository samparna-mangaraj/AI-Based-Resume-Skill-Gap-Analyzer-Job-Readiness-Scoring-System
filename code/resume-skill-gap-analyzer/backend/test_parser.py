import os
import sys
from app.parser import ResumeParser

def test_parser():
    print("--- RESUME PARSER TEST ---")
    
    # Test Case 1: HTML with "Dirty" content
    html_content = b"""
    <html>
        <head><style>.bad { color: red; }</style></head>
        <body>
            <h1>John Doe</h1>
            <p>Email: john@example.com | Phone: 555-0199</p>
            <script>console.log('Ignore me');</script>
            <div>Skillset: <b>Python</b>, <b>Java</b>, and <b>React!</b></div>
            <p>Experience: 4 years (2020-2024)</p>
        </body>
    </html>
    """
    
    print("\n1. Testing HTML Parsing...")
    result_html = ResumeParser.parse(html_content, "resume.html")
    print(f"Format: {result_html['format']}")
    print(f"Raw (Sample): {result_html['raw_content'][:100]}...")
    print(f"Cleaned: {result_html['cleaned_content']}")
    print(f"Word Count: {result_html['word_count']}")
    
    # Test Case 2: TXT with special characters
    txt_content = "Software Engineer\nExpertise: ML/AI & Cloud Computing!!\n\n- Python @ 100%\n- SQL & NoSQL".encode('utf-8')
    
    print("\n2. Testing TXT Parsing (Level 2 Cleaning)...")
    result_txt = ResumeParser.parse(txt_content, "resume.txt")
    print(f"Cleaned: {result_txt['cleaned_content']}")
    
    # Verify success
    if result_html['success'] and result_txt['success']:
        print("\n[SUCCESS] PARSER TESTS PASSED!")
    else:
        print("\n[FAILED] PARSER TESTS FAILED!")

if __name__ == "__main__":
    test_parser()
