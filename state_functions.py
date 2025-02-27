import asyncio

class StateFunctions:
    """
    This class houses asynchronous state function logic.
    """

    async def request_input(self, context, executor):
        """Requests user input for name and email."""
        print("Please enter your name:")
        # In a real application, you'd get input here.  For testing,
        # we'll use pre-set values or values from the context.
        context["name"] = input()
        print("Please enter your email:")
        context["email"] = input()
        return "data_collected", None

    async def extract_data(self, context, executor):
        """Extracts data from the context (no-op in this example)."""
        print(f"Extracting  {context}")
        return "data_extracted", None

    async def check_all_data_collected(self, context, executor):
        """Checks if all required data is collected."""
        if "name" in context and "email" in context:
            return "all_data_collected", None
        else:
            return None, "override_state" # Example of using override

    async def ask_confirmation(self, context, executor):
        """Asks for confirmation from the user."""
        print("Do you confirm the data is correct? (yes/no)")
        confirmation = input()
        if confirmation.lower() == "yes":
            return "confirmed", None
        elif confirmation.lower() == "no":
            return "not_confirmed", None
        else:
            return "invalid_confirmation", None


    async def process_data(self, context, executor):
        """Processes the collected data (prints it in this example)."""
        print("Processing ")
        print(f"  Name: {context['name']}")
        print(f"  Email: {context['email']}")
        return "data_processed", None

    async def __start__(self, context, executor):
        """Start state"""
        return None, None
