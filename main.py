import os
import datetime
import time
from booking_bot import BookingBotMyFitness

def job():
    # Get credentials from a file
    credentials_file = os.path.join(os.path.expanduser("~"), "myfitnesskey.txt")
    with open(credentials_file, "r") as file:
        email = file.readline().strip()
        password = file.readline().strip()
    
    # Initialize and run the bot
    bot = BookingBotMyFitness(email, password, target_class="Hot Pilates Sculpt", headless=False)
    bot.run()

# Example usage
if __name__ == "__main__":
    print("Booking bot scheduler is running...")

    while True:
        now = datetime.datetime.now()
        
        # Schedule the job
        if now.weekday() == 6 and now.hour == 20 and now.minute == 00:
            job()
            break

        time.sleep(60)  # Check every minute
        