import asyncio

class StateFunctions:
    """
    This class houses asynchronous state function logic.
    """

    async def request_input(self, context, executor):
        """Requests user input for name and email."""
        name = await executor._request_input("Please enter your name:")
        context["name"] = name
        email = await executor._request_input("Please enter your email:")
        context["email"] = email
        return "data_collected"

    async def extract_data(self, context, executor):
        """Extracts data from the context (no-op in this example)."""
        print(f"Extracting  {context}")
        return "data_extracted"

    async def check_all_data_collected(self, context, executor):
        """Checks if all required data is collected."""
        if "name" in context and "email" in context:
            return "all_data_collected"
        else:
            return "override_state"

    async def ask_confirmation(self, context, executor):
        """Asks for confirmation from the user."""
        confirmation = await executor._request_input("Do you confirm the data is correct? (yes/no)")
        if confirmation.lower() == "yes":
            return "confirmed"
        elif confirmation.lower() == "no":
            return "not_confirmed"
        else:
            return "invalid_confirmation"


    async def process_data(self, context, executor):
        """Processes the collected data (prints it in this example)."""
        print("Processing ")
        print(f"  Name: {context['name']}")
        print(f"  Email: {context['email']}")
        return "data_processed"

    async def __start__(self, context, executor):
        """Start state"""
        return None
