# CELL 3: Runner (runner - Reused)
from composable_state_functions import *
from composable_engine import *

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
        
        
# CELL 4: State Machine Definitions (Modified to use sub-engine definition functions)

# State Machine Definitions - Interchangeable Style (Modified to use sub-engine definition functions)
state_functions_interchangeable_nested_functions = {
    "__start__": state_start,
    "state_process_input": state_process_input,
    "option_actions": create_option_actions_sub_machine,  # Assign the FUNCTION here, not the dictionary directly
    "state_complex_process": state_complex_process,
    "state_generate_report": state_generate_report,
    "__end__": state_end,
}

# Example Usage (to run the state machine - place in another cell if needed):
if __name__ == "__main__":
    engine_callable_sub_engines = composable_engine(state_functions_interchangeable_nested_functions, debug_mode=True)
    runner(engine_callable_sub_engines, debug_mode=True)