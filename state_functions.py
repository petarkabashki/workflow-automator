class StateFunctions:
    """
    This class houses state function logic. State functions can now:
    - Request input
    - Provide progress updates
    - Issue state change instructions
    - Accept arguments from the engine's caller
    """

    def __init__(self):
        self.context = {}

    def start(self, arg=None):
        """Initial state function."""
        print("Starting workflow...")
        return ('state_change', 'request_name')

    def request_name(self, arg=None):
        """Requests the user's name."""
        return ('input', 'Please enter your name:')

    def process_name(self, name=None):
        """Processes the received name and requests age."""
        if name:
            self.context['name'] = name
            print(f"Hello, {name}!")
            return ('input', 'Please enter your age:')
        else:
            return ('input', 'Name is required. Please enter your name:')
        
    def process_age(self, age=None):
        """Processes the received age and transitions to the end."""
        if age:
            try:
                age = int(age)
                self.context['age'] = age
                print(f"You are {age} years old.")
                return ('progress', 100)  # Indicate completion
            except ValueError:
                return ('input', 'Invalid age. Please enter a number:')
        else:
            return ('input', 'Age is required. Please enter your age:')

    def end(self, arg=None):
        """Final state function."""
        print("Workflow completed.")
        print(f"Collected data: {self.context}")
        return ('end',)
