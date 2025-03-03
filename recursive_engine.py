
def recursive_engine(state_definitions, initial_state="__start__", debug_mode=False):
    if "__start__" not in state_definitions:
        raise ValueError("State machine must have a '__start__' state.")
    if "__end__" not in state_definitions:
        raise ValueError("State machine must have an '__end__' state.")

    current_state_name = initial_state
    input_value = None

    while current_state_name and current_state_name != "__end__":
        state_definition = state_definitions[current_state_name]

        if callable(state_definition):  # Treat as state function
            state_function = state_definition
        elif isinstance(state_definition, dict):  # Treat as sub-state machine
            sub_machine_definition = state_definition
            state_function = lambda input_data: recursive_engine(sub_machine_definition, initial_state="__start__", debug_mode=debug_mode) # Recursive call
        else:
            raise ValueError(f"Invalid state definition for '{current_state_name}'. Must be function or dict.")

        next_state_name = None
        parent_transition_info = None
        last_instruction_from_state = None # Track last instruction yielded from the state function

        try:
            state_generator = state_function(input_data={"instruction_context": input_value})
            instruction_result = None

            while True:
                try:
                    yielded_value = next(state_generator)
                    last_instruction_from_state = yielded_value # Store every yielded value as last instruction

                    if isinstance(yielded_value, dict) and "instruction" in yielded_value:
                        instruction = yielded_value["instruction"]

                        if instruction == "transition":
                            next_state_name = yielded_value.get("next_state")
                            instruction_result = yielded_value

                        elif instruction == "parent_transition":
                            parent_transition_info = yielded_value
                            instruction_result = yielded_value
                            break  # Break inner loop

                        elif instruction == "request_input":  # Directly pass to runner
                            yield yielded_value  # Pass request_input instruction to runner
                            input_value_sent_by_runner = yield  # Wait for runner to send input back
                            input_value = {"instruction": "runner_input", "input_data": input_value_sent_by_runner}  # Prepare for next state function

                        else:  # All other instructions: notify, debug, error, warning, custom - pass directly to runner
                            yield yielded_value  # Pass all other instructions directly to runner
                            instruction_result = yielded_value

                    else:  # Handle unexpected yield values - still pass to runner as warning
                        yield {"instruction": "runner_warning", "message": f"State function yielded unexpected value: {yielded_value}", "payload": {"yielded_value": yielded_value}}
                        instruction_result = yielded_value


                except StopIteration:
                    if parent_transition_info:
                        current_state_name = parent_transition_info.get("next_state_for_parent")
                    elif last_instruction_from_state and isinstance(last_instruction_from_state, dict) and last_instruction_from_state.get("instruction") == "transition": # Check last instruction for transition on StopIteration
                        current_state_name = last_instruction_from_state.get("next_state") # Use transition from __end__ state if available
                    elif instruction_result and instruction_result.get("instruction") == "transition": # Fallback to regular transition
                        current_state_name = instruction_result.get("next_state")
                    else:
                        current_state_name = None # Halt if no transition
                    input_value = None
                    break

        except StopIteration:
            current_state_name = None
            yield {"instruction": "runner_notify", "message": "State machine halted (via state function return).", "level": "info"}
            break
        except Exception as e:
            yield {"instruction": "runner_error", "message": f"Error in state '{current_state_name}': {e}", "payload": {"exception": str(e)}}
            current_state_name = None
            break

    yield {"instruction": "runner_notify", "message": "State machine reached '__end__' state.", "level": "info"}

