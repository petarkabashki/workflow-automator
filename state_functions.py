import asyncio

class StateFunctions:
    """
    This class houses asynchronous state function logic.
    """

    def __init__(self):
        self.context = {}  # Initialize context here
        self.interaction_history = []  # Initialize history here

    async def request_input(self):
        """Requests user input for name and email."""
        print("Please enter your name:")
        self.context["name"] = input()
        print("Please enter your email:")
        self.context["email"] = input()
        return "data_collected", None

    async def extract_data(self):
        """Extracts data from the context (no-op in this example)."""
        print(f"Extracting  {self.context}")
        return "data_extracted", None

    async def check_all_data_collected(self):
        """Checks if all required data is collected."""
        if "name" in self.context and "email" in self.context:
            return "all_data_collected", None
        else:
            return None, "override_state" # Example of using override

    async def ask_confirmation(self):
        """Asks for confirmation from the user."""
        print("Do you confirm the data is correct? (yes/no)")
        confirmation = input()
        if confirmation.lower() == "yes":
            return "confirmed", None
        elif confirmation.lower() == "no":
            return "not_confirmed", None
        else:
            return "invalid_confirmation", None


    async def process_data(self):
        """Processes the collected data (prints it in this example)."""
        print("Processing ")
        print(f"  Name: {self.context['name']}")
        print(f"  Email: {self.context['email']}")
        return "data_processed", None

    async def __start__(self):
        """Start state"""
        return None, None
