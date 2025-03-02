import pytest
from engine import Engine


def test_basic_transition():
    def start():
        yield "transition", "next_state"

    def next_state():
        yield "done", {}

    registered_functions = {
        "__start__": start,
        "next_state": next_state
    }
    engine = Engine(registered_functions)
    engine_instance = engine.run()
    result = next(engine_instance)
    assert result[0] == "__start__"
    assert result[1:] == ("transition", "next_state")
    instruction, context = result[1:]
    with pytest.raises(StopIteration):
        result = engine_instance.send((instruction, context))


def test_end_state():
    def start():
        yield "transition", "__end__"
    registered_functions = {
        "__start__": start
    }
    engine = Engine(registered_functions)
    engine_instance = engine.run()
    result = next(engine_instance)
    assert result[0] == "__start__"
    assert result[1:] == ("transition", "__end__")
    instruction, context = result[1:]
    with pytest.raises(StopIteration):
        result = engine_instance.send((instruction, context))


def test_invalid_transition():
    def start():
        yield "transition", "invalid"

    registered_functions = {
        "__start__": start
    }
    engine = Engine(registered_functions)
    engine_instance = engine.run()
    result = next(engine_instance)
    assert result[0] == "__start__"
    assert result[1:] == ("transition", "invalid")
    instruction, context = result[1:]
    with pytest.raises(StopIteration):
        result = engine_instance.send((instruction, context))


def test_stop_iteration():
    def start():
        yield "transition", "next"

    def next_state():
        return None  # next_state will now be primed but not executed

    registered_functions = {
        "__start__": start,
        "next": next_state
    }
    engine = Engine(registered_functions)
    engine_instance = engine.run()

    result = next(engine_instance)
    assert result[0] == "__start__"
    assert result[1:] == ("transition", "next")
    instruction, context = result[1:]
    with pytest.raises(StopIteration):
        engine_instance.send((instruction, context))