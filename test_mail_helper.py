#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.mail_helper import MailHelper

def test_mail_helper():
    """Test the updated mail helper functionality"""
    print("Testing MailHelper with club name and document name...")
    
    # Create a mock attachment file for testing
    test_file = "test_attachment.xlsx"
    with open(test_file, "w") as f:
        f.write("This is a test attachment file")
    
    try:
        mail_helper = MailHelper()
        # Test the updated send_mail method with club name and document name
        mail_helper.send_mail("ТестовыйКлуб", "ТестоваяСлужебка_2023_12_15", [test_file])
        print("SUCCESS: Mail sent with club name and document name in subject!")
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        # Clean up the test file
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_mail_helper()
