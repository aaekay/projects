import yagmail as ym
import requests
import hashlib
import time
import logging 

logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.FileHandler("tracker.log"),  # Log to a file #
    ]
)

# Create logger
log = logging.getLogger(__name__)



# yag.send(subject="Great!", contents = "")

def get_website_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def compute_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def main(url):
    # Replace with the website URL you want to track
    
    previous_hash = ""

    while True:
        try:
            yag = ym.SMTP("abnormaldocs@gmail.com", oauth2_file="token.json")
            log.info("the authentication is good")
            try:
                current_content = get_website_content(url)
            except requests.RequestException as e:
                log.info(f"Error fetching the website: {e}")
                yag.send(subject="Error checking AIIMS Phd!", contents = "Error in website Click here")
            # current_hash = compute_hash(current_content)
            if "July" not in current_content:
                log.info("False, there is no change in website")
                yag.send(to="mitugarg75@gmail.com", subject="No Changes in AIIMS Phd", contents = "There has been no changes in website")
                log.info("mail sent")
            else:
                log.info(f"There is a change in website. Please review. Click here {url}")
                yag.send(to="mitugarg75@gmail.com", subject="Changes in AIIMS Phd!", contents = "There has been changes in website Click here")
                log.info("mail send")
        except:
            log.info(f"Error sending the mail: {e}")
        time.sleep(12*60*60)  # Wait for 24 hours

main("https://phd.aiimsexams.ac.in/Welcome_DM.aspx")