import datetime
import random
import string

def generate_unique_tag(folder_name):
    # Get current timestamp: YYYYMMDDHHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # Generate 5 random alphanumeric characters
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    # Construct the tag: "manual_<folder_name>_<timestamp>_<random_chars>"
    tag = f"manual_{folder_name}_{timestamp}_{random_chars}"
    return tag
