# CELL 2: State Functions and Sub-Engine Definition Function

import time

def state_start(input_data=None):
    yield {"instruction": "debug", "level": "state_enter", "message": "Entering __start__ state: Initializing workflow"}
    yield {"instruction": "notify", "message": "Welcome to the Interchangeable State Machine Demo!", "level": "info"} # Updated message
    yield {"instruction": "request_input", "query": "Please enter your name:"}
    name = yield
    if name:
        yield {"instruction": "notify", "message": f"Hello, {name}! Workflow initialized.", "level": "info"}
        yield {"instruction": "transition", "next_state": "state_process_input", "payload": {"user_name": name}}
    else:
        yield {"instruction": "warning", "message": "No name entered. Please try again."}
        yield {"instruction": "transition", "next_state": "__start__"}
    yield {"instruction": "debug", "level": "state_exit", "message": "Exiting __start__ state"}
    return

def state_process_input(input_data=None):
    user_name = input_data.get("payload", {}).get("user_name", "Unknown User")
    yield {"instruction": "debug", "level": "state_enter", "message": "Entering state_process_input state", "payload": {"current_user": user_name}}
    yield {"instruction": "notify", "message": f"Awaiting command from {user_name}. Options: (options_menu/process/report/quit)", "level": "info"} # Updated options
    yield {"instruction": "request_input", "query": f"Enter command for {user_name}:"}
    command = yield
    if command.lower() == "options_menu": # Command to trigger sub-machine - now transition to definition directly!
        yield {"instruction": "debug", "level": "action", "message": f"User '{user_name}' chose 'options_menu' command - invoking sub-machine"}
        yield {"instruction": "transition", "next_state": "option_actions", "payload": {"user_name": user_name}} # Transition to sub-machine DEFINITION FUNCTION
    elif command.lower() == "process":
        yield {"instruction": "debug", "level": "action", "message": f"User '{user_name}' chose 'process' command"}
        yield {"instruction": "transition", "next_state": "state_complex_process", "payload": {"user_name": user_name}}
    elif command.lower() == "report":
        yield {"instruction": "debug", "level": "action", "message": f"User '{user_name}' chose 'report' command"}
        yield {"instruction": "transition", "next_state": "state_generate_report", "payload": {"user_name": user_name}}
    elif command.lower() == "quit":
        yield {"instruction": "debug", "level": "action", "message": f"User '{user_name}' chose 'quit' command"}
        yield {"instruction": "notify", "message": f"Goodbye, {user_name}! Ending workflow.", "level": "info"}
        yield {"instruction": "transition", "next_state": "__end__"}
    else:
        yield {"instruction": "warning", "message": f"Invalid command: '{command}'. Please choose from options.", "payload": {"command_entered": command}}
        yield {"instruction": "transition", "next_state": "state_process_input", "payload": {"user_name": user_name}} # Loop back
    yield {"instruction": "debug", "level": "state_exit", "message": "Exiting state_process_input state"}
    return

def state_complex_process(input_data=None):
    user_name = input_data.get("payload", {}).get("user_name", "Unknown User")
    yield {"instruction": "debug", "level": "state_enter", "message": "Entering state_complex_process state", "payload": {"current_user": user_name}}
    yield {"instruction": "notify", "message": f"Starting complex data processing for {user_name}...", "level": "info"}
    yield {"instruction": "request_input", "query": f"Enter data file name for processing for {user_name}:"}
    file_name = yield
    if not file_name:
        yield {"instruction": "notify", "message": "No file name provided. Aborting complex process.", "level": "warning"}
        yield {"instruction": "transition", "next_state": "state_process_input", "payload": {"user_name": user_name}}
        return

    yield {"instruction": "notify", "message": f"Initiating file processing for '{file_name}'.", "level": "info", "payload": {"file": file_name}}
    total_steps = 10
    for step in range(total_steps):
        time.sleep(0.3) # Reduced time for faster demo
        progress_percent = int(((step + 1) / total_steps) * 100)
        yield {"instruction": "notify", "message": f"Processing '{file_name}': {progress_percent}% complete...", "level": "progress", "payload": {"file": file_name, "progress": progress_percent}}
        yield {"instruction": "debug", "level": "progress", "message": f"File processing step {step+1}/{total_steps} ({progress_percent}%)", "payload": {"file": file_name, "step": step+1, "progress": progress_percent}}

    processing_result = {"status": "success", "file": file_name, "processed_records": 150} # Example result
    yield {"instruction": "notify", "message": f"File '{file_name}' processing completed successfully!", "level": "success", "payload": {"file": file_name, "result": processing_result}}
    yield {"instruction": "debug", "level": "action_complete", "message": f"File processing finished", "payload": {"result": processing_result}}

    yield {"instruction": "request_input", "query": f"Review processing result for '{file_name}' (ok/retry):", "payload": {"result_summary": processing_result}}
    confirmation = yield
    if confirmation.lower() == "ok":
        yield {"instruction": "notify", "message": "Processing confirmed. Proceeding to next steps.", "level": "info"}
        yield {"instruction": "transition", "next_state": "state_option_one_action", "payload": {"last_process_result": processing_result, "user_name": user_name}} # Passing processing result
    else:
        yield {"instruction": "notify", "message": "Processing result not accepted. Returning to input.", "level": "warning"}
        yield {"instruction": "transition", "next_state": "state_process_input", "payload": {"user_name": user_name}}
    yield {"instruction": "debug", "level": "state_exit", "message": "Exiting state_complex_process state"}
    return

def state_option_one_action(input_data=None):
    user_name = input_data.get("payload", {}).get("user_name", "Unknown User")
    last_result = input_data.get("payload", {}).get("last_process_result", {})
    yield {"instruction": "debug", "level": "state_enter", "message": "Entering state_option_one_action", "payload": {"current_user": user_name, "last_result_file": last_result.get("file")}}
    yield {"instruction": "notify", "message": f"Performing Option 1 action for {user_name}...", "level": "info"}
    yield {"instruction": "perform_custom_action", "name": "option_one_task_started", "payload": {"task_id": 123, "user": user_name, "last_file": last_result.get("file")}}
    yield {"instruction": "notify", "message": "Option 1 action completed successfully.", "level": "success"}
    yield {"instruction": "transition", "next_state": "state_process_input", "payload": {"user_name": user_name}} # Back to input
    yield {"instruction": "debug", "level": "state_exit", "message": "Exiting state_option_one_action"}
    return

def state_option_two_action(input_data=None):
    user_name = input_data.get("payload", {}).get("user_name", "Unknown User")
    yield {"instruction": "debug", "level": "state_enter", "message": "Entering state_option_two_action", "payload": {"current_user": user_name}}
    yield {"instruction": "notify", "message": f"Initiating Option 2 action for {user_name}... (simulating potential issue)", "level": "warning"}
    yield {"instruction": "debug", "level": "action", "message": "Simulating an error within Option 2 logic"}
    yield {"instruction": "error", "message": f"Error encountered during Option 2 action for {user_name}!", "payload": {"user": user_name, "error_code": "OPT2-ERR-500"}}
    yield {"instruction": "transition", "next_state": "state_process_input", "payload": {"user_name": user_name}} # Back to input after error
    yield {"instruction": "debug", "level": "state_exit", "message": "Exiting state_option_two_action"}
    return

def state_generate_report(input_data=None): # New state: generate report
    user_name = input_data.get("payload", {}).get("user_name", "Unknown User")
    yield {"instruction": "debug", "level": "state_enter", "message": "Entering state_generate_report", "payload": {"current_user": user_name}}
    yield {"instruction": "notify", "message": f"Generating report for {user_name}...", "level": "info"}
    time.sleep(1.5) # Simulate report generation time
    report_data = {"user": user_name, "report_type": "Summary", "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    yield {"instruction": "notify", "message": f"Report generated successfully for {user_name}.", "level": "success", "payload": {"report_details": report_data}}
    yield {"instruction": "debug", "level": "action_complete", "message": "Report generation complete", "payload": {"report_details": report_data}}
    yield {"instruction": "transition", "next_state": "state_process_input", "payload": {"user_name": user_name}} # Back to input after report
    yield {"instruction": "debug", "level": "state_exit", "message": "Exiting state_generate_report"}
    return


def state_end(input_data=None):
    yield {"instruction": "debug", "level": "state_enter", "message": "Entering __end__ state: Workflow termination"}
    yield {"instruction": "notify", "message": "State Machine Execution Finished. Thank you!", "level": "info"}
    yield {"instruction": "debug", "level": "state_exit", "message": "Exiting __end__ state"}
    yield {"instruction": "transition", "next_state": "__end__"} # Self-loop or remove transition for final halt
    return

def create_option_actions_sub_machine():
    """Function to create and return the 'option_actions' sub-machine definition."""
    option_actions_sub_machine_definition = {
        "__start__": state_process_input,  # Reusing state_process_input - could have dedicated sub-machine start state
        "state_option_one_action": state_option_one_action,
        "state_option_two_action": state_option_two_action,
        "__end__": state_end,  # Reusing state_end
        "parent_process_input": state_process_input  # Example parent transition if needed from within sub-machine states
    }
    return option_actions_sub_machine_definition