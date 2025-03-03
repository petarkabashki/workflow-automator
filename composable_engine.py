def composable_engine(state_definitions, initial_state="__start__", debug_mode=False):
    if "__start__" not in state_definitions:
        raise ValueError("State machine must have a '__start__' state.")
    if "__end__" not in state_definitions:
        raise ValueError("State machine must have an '__end__' state.")

    engine_stack = [ # Stack to manage state machines (can be main machine or sub-machines)
        {"state_def": state_definitions, "current_state_name": initial_state, "state_generator": None}
    ]

    input_value = None

    while engine_stack: # While there are state machines in the stack to process
        current_machine_context = engine_stack[-1] # Get the current machine context from the top of the stack
        current_state_name = current_machine_context["current_state_name"]
        state_generator = current_machine_context["state_generator"]
        state_def = current_machine_context["state_def"]


        if current_state_name is None or current_state_name == "__end__":
            engine_stack.pop() # Sub-machine or main machine finished, pop it from the stack
            continue # Continue to process the next machine in the stack (if any)


        state_definition = state_def[current_state_name] # Get state definition from the *current machine's* definitions


        if state_generator is None: # If state generator is not initialized for this state
            if isinstance(state_definition, dict): # It's a sub-machine definition
                sub_machine_definition = state_definition
                # Push sub-machine context to the stack - this is composition, NOT recursion
                engine_stack.append({
                    "state_def": sub_machine_definition,
                    "current_state_name": "__start__", # Start sub-machine from __start__
                    "state_generator": None # Generator will be initialized in the next iteration
                })
                continue # Process the new sub-machine at the top of the stack in the next iteration

            elif callable(state_definition): # It's a state function
                state_function = state_definition
                current_machine_context["state_generator"] = state_function(input_data={"instruction_context": input_value}) # Initialize generator
                state_generator = current_machine_context["state_generator"] # Update local reference

            else:
                raise ValueError(f"Invalid state definition for '{current_state_name}'. Must be function or dict.")


        next_state_name = None
        parent_transition_info = None
        last_instruction_from_state = None
        instruction_result = None


        try:
            yielded_value = next(state_generator) # Get instruction from current state generator
            last_instruction_from_state = yielded_value

            if isinstance(yielded_value, dict) and "instruction" in yielded_value:
                instruction = yielded_value["instruction"]

                if instruction == "transition":
                    next_state_name = yielded_value.get("next_state")
                    instruction_result = yielded_value

                elif instruction == "parent_transition":
                    parent_transition_info = yielded_value
                    instruction_result = yielded_value
                    engine_stack.pop() # Pop the current sub-machine from stack as it requests parent transition
                    if engine_stack: # If there is a parent machine in stack
                        current_machine_context = engine_stack[-1] # Get parent machine context
                        current_machine_context["current_state_name"] = parent_transition_info.get("next_state_for_parent") # Set parent's next state
                    else:
                        current_state_name = parent_transition_info.get("next_state_for_parent") # For top-level parent transition
                    continue # Process the transition in the parent machine (or top-level) in next iteration

                elif instruction == "request_input":
                    input_request_instruction = yielded_value
                    yield input_request_instruction # Yield request input instruction to runner
                    input_value_sent_by_runner = yield # Wait for runner input
                    input_value = {"instruction": "runner_input", "input_data": input_value_sent_by_runner} # Prepare input for next state function
                    continue # Continue processing current state with received input

                else:  # All other instructions: notify, debug, error, warning, custom
                    yield yielded_value # Yield other instructions to runner
                    continue # Continue processing current state


            else:  # Unexpected yield value
                yield {"instruction": "runner_warning", "message": f"State function yielded unexpected value: {yielded_value}", "payload": {"yielded_value": yielded_value}}
                instruction_result = yielded_value
                continue # Continue processing current state


        except StopIteration: # State function finished yielding
            if parent_transition_info: # Check for parent transition again (though should be handled by parent_transition instruction)
                engine_stack.pop() # Pop finished sub-machine
                if engine_stack:
                    current_machine_context = engine_stack[-1]
                    current_machine_context["current_state_name"] = parent_transition_info.get("next_state_for_parent")
                else:
                    current_state_name = parent_transition_info.get("next_state_for_parent")
            elif last_instruction_from_state and isinstance(last_instruction_from_state, dict) and last_instruction_from_state.get("instruction") == "transition": # Check __end__ transition
                current_machine_context["current_state_name"] = last_instruction_from_state.get("next_state") # Transition within same machine
            elif instruction_result and instruction_result.get("instruction") == "transition": # Regular transition
                current_machine_context["current_state_name"] = instruction_result.get("next_state") # Transition within same machine
            else:
                current_machine_context["current_state_name"] = None # Halt current machine if no transition
            current_machine_context["state_generator"] = None # Reset generator for next state or next machine in stack
            input_value = None # Reset input for next state in sequence
            continue # Process next state in the current machine or pop from stack if needed


        except Exception as e: # Error in state function
            yield {"instruction": "runner_error", "message": f"Error in state '{current_state_name}': {e}", "payload": {"exception": str(e)}}
            current_machine_context["current_state_name"] = None # Halt current machine on error
            current_machine_context["state_generator"] = None
            engine_stack.pop() # Pop errored machine - could be refined to handle error propagation to parent
            continue # Process next machine from stack or finish if stack is empty


    yield {"instruction": "runner_notify", "message": "State machine reached '__end__' state.", "level": "info"} # Main machine reached end
