from booking_bot import BookingBotMyFitness
import os

# Example usage
if __name__ == "__main__":
    # Get credentials from a file
    credentials_file = os.path.join(os.path.expanduser("~"), "myfitnesskey.txt")
    with open(credentials_file, "r") as file:
        email = file.readline().strip()
        password = file.readline().strip()
    
    # Initialize and run the bot
    bot = BookingBotMyFitness(email, password, target_class="Hot Pilates Sculpt", headless=True)
    bot.run()