class EngineObserver:
    """
    Observes the WFEngine and logs events to the console and a file.
    """
    def __init__(self):
        self.event_log = []

    def notify(self, event_type, data):
        """
        Receives notifications from the WFEngine.
        """
        log_entry = f"Event: {event_type}, Data: {data}"
        print(log_entry)  # Log to console
        self.event_log.append(log_entry)  # Store for file logging

    def save_log(self, filename="engine_log.txt"):
        """
        Saves the accumulated event log to a file.
        """
        with open(filename, "w") as f:
            for entry in self.event_log:
                f.write(entry + "\n")
