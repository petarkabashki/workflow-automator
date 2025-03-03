from state_functions import *
from recursive_engine import *


def runner(engine_generator, debug_mode=False):
    print("-" * 50 + " State Machine Execution Started " + "-" * 50) # Start delimiter
    state_transition_count = 0 # Counter for state transitions

    while True:
        try:
            instruction_for_runner = next(engine_generator)
            instruction_type = instruction_for_runner["instruction"]

            if instruction_type == "runner_notify":
                level = instruction_for_runner.get('level', 'info').upper()
                message = instruction_for_runner['message']
                payload = instruction_for_runner.get('payload', {})
                print(f"[{level}] Notification: {message}  {'Payload:' + str(payload) if payload else ''}")
            elif instruction_type == "runner_warning":
                message = instruction_for_runner['message']
                payload = instruction_for_runner.get('payload', {})
                print(f"[WARNING] {message}  {'Payload:' + str(payload) if payload else ''}")
            elif instruction_type == "runner_error":
                message = instruction_for_runner['message']
                payload = instruction_for_runner.get('payload', {})
                exception_info = instruction_for_runner.get('exception', '') # Retrieve exception info if available
                print(f"[ERROR] {message}  {'Payload:' + str(payload) if payload else ''}  {'Exception:' + exception_info if exception_info else ''}")
            elif instruction_type == "runner_debug" and debug_mode:
                level = instruction_for_runner.get('level', 'debug').upper()
                message = instruction_for_runner['message']
                payload = instruction_for_runner.get('payload', {})
                print(f"[DEBUG - {level}] {message}  {'Payload:' + str(payload) if payload else ''}")
            elif instruction_type == "runner_request_input":
                query = instruction_for_runner.get("query", "Enter input:")
                user_input = input(f"[INPUT REQUEST] {query} ") # Indicate input request clearly
                engine_generator.send(user_input)
            elif instruction_type == "runner_custom":
                name = instruction_for_runner['name']
                payload = instruction_for_runner.get('payload', {})
                print(f"[CUSTOM ACTION] Performing '{name}'  {'Payload:' + str(payload) if payload else ''}")
            elif instruction_type == "runner_warning": # Handling runner_warning from engine for unexpected yields
                message = instruction_for_runner['message']
                payload = instruction_for_runner.get('payload', {})
                print(f"[ENGINE WARNING] {message}  {'Payload:' + str(payload) if payload else ''}")
            else: # Fallback for unexpected instructions
                print(f"[RUNNER] Received Instruction: {instruction_for_runner}  {'Payload:' + str(instruction_for_runner.get('payload', {})) if instruction_for_runner.get('payload') else ''}")

            if instruction_type == "transition": # Visual separator for state transitions
                state_transition_count += 1
                print(f"\n{'=' * 30}  State Transition #{state_transition_count}  {'=' * 30}\n")


        except StopIteration:
            print("-" * 50 + " State Machine Execution Finished " + "-" * 50) # End delimiter
            break
        except Exception as runner_exception: # Catch runner-level exceptions if needed.
            print(f"[RUNNER ERROR] An error occurred in the runner loop: {runner_exception}")
            print("-" * 50 + " State Machine Execution Aborted due to Runner Error " + "-" * 50)
            break

# 4. Example Usage (No Changes needed to state machine definitions from previous response, just using fleshed out state functions and runner)

# Example State Machine Definitions (using the fleshed out state functions):
option_actions_sub_machine_fleshed_out = {
    "__start__": state_process_input, # Reusing state_process_input for sub-machine start
    "state_option_one_action": state_option_one_action,
    "state_option_two_action": state_option_two_action,
    "__end__": state_end,
    "parent_process_input": state_process_input # Example parent transition (though __end__ payload is preferred now)
}

state_functions_recursive_nested_fleshed_out = {
    "__start__": state_start,
    "state_process_input": state_process_input,
    "option_actions": option_actions_sub_machine_fleshed_out, # Nested sub-machine
    "state_complex_process": state_complex_process,
    "state_generate_report": state_generate_report, # New state included in main machine
    "__end__": state_end,
}

# Run the engine with the enhanced runner and debug mode ON:
engine_fleshed_out = recursive_engine(state_functions_recursive_nested_fleshed_out, debug_mode=True)
runner(engine_fleshed_out, debug_mode=True) # Pass debug_mode to runner as well if needed for runner-specific debug output