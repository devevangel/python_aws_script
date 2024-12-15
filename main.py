import time
import logging

# Set up logging to file
logging.basicConfig(
    filename='/var/log/main.log',  # Log file location
    level=logging.INFO,  # Log level (INFO means it logs general information)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format with timestamp
)

def main():
    logging.info("Python script started.")  # Log when the script starts
    while True:
        logging.info("Script is running...")  # Log every minute
        time.sleep(60)  # Keep the script running

if __name__ == "__main__":
    main()
