
# Clone the repository:

      git clone https://github.com/mrfelpa/script-download-proxy.git
      
# Access the script directory:

      cd script-download-proxy

# Install the required libraries:

      pip install -r requirements.txt


- Fill in the variables at the beginning of the script with your information:
  
- ***url:*** URL of the file for download.
- ***delay:*** Waiting time between requests (in seconds).
- ***max_retries:*** Maximum number of download attempts.
- ***proxy_providers:*** List of proxy providers that you consider safe and reliable.

# Run the script:

    python download.py

# Disclaimer

- The author of this code is not responsible for the misuse of this script

# Implementações futuras:

- [X] Detection and blocking of CAPTCHA proxies.
- [ ] Integration with cloud services for file storage.
