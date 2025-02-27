import asyncio
import unittest
import graphviz
from engine import EngineExecutor


class TestEngineExecutor(unittest.IsolatedAsyncioTestCase):

    async def test_basic_workflow(self):
        dot_source = """
        strict digraph {
            __start__ -> state1;
            state1 -> state2;
            state2 -> __end__;
        }
        """
        graph = graphviz.Source(dot_source)

        class StateFunctions:
            async def state1(self, context, executor):
                pass

            async def state2(self, context, executor):
                pass

        executor = EngineExecutor(graph, StateFunctions())
        await executor.run()
        self.assertEqual(executor.current_state, "__end__")
        self.assertEqual(len(executor.interaction_history), 3)

    async def test_user_input(self):
        dot_source = """
        strict digraph {
            __start__ -> state1;
            state1 -> __end__;
        }
        """
        graph = graphviz.Source(dot_source)

        class StateFunctions:
            async def state1(self, context, executor):
                user_input = await executor._request_input("Enter something:")
                context["received_input"] = user_input

        executor = EngineExecutor(graph, StateFunctions())

        # Simulate user input in a separate task
        async def provide_input():
            await asyncio.sleep(0.1)  # Wait for the request to be made
            await executor.send_input("Test Input")

        input_task = asyncio.create_task(provide_input())
        await executor.run()
        await input_task

        self.assertEqual(executor.context.get("received_input"), "Test Input")
        self.assertEqual(len(executor.interaction_history), 4)
        self.assertEqual(executor.interaction_history[1][1], "Enter something:")
        self.assertEqual(executor.interaction_history[2][1], "Test Input")

    async def test_file_upload(self):
        dot_source = """
        strict digraph {
            __start__ -> state1;
            state1 -> __end__;
        }
        """
        graph = graphviz.Source(dot_source)

        class StateFunctions:
            async def state1(self, context, executor):
                await executor._request_input("Upload a file:")

        executor = EngineExecutor(graph, StateFunctions())

        # Simulate file upload
        async def provide_file():
            await asyncio.sleep(0.1)
            await executor.upload_file("test_file.txt")

        file_task = asyncio.create_task(provide_file())
        await executor.run()
        await file_task

        self.assertEqual(executor.context.get("last_file"), "test_file.txt")
        self.assertEqual(len(executor.interaction_history), 4)
        self.assertEqual(executor.interaction_history[2][1], "Uploaded file: test_file.txt")

    async def test_method_override(self):
        dot_source = """
        strict digraph {
            __start__ -> state1;
            state1 -> state2;
            state2 -> __end__;
        }
        """
        graph = graphviz.Source(dot_source)

        class StateFunctions:
            async def state1(self, context, executor):
                return "state3"  # Override transition

            async def state2(self, context, executor):
                pass

            async def state3(self, context, executor):
                pass
        executor = EngineExecutor(graph, StateFunctions())
        await executor.run()
        self.assertEqual(executor.current_state, "state3")  # Should end in state3, not state2
        self.assertEqual(len(executor.interaction_history), 2)


    async def test_no_outgoing_edges(self):
        dot_source = """
        strict digraph {
            __start__ -> state1;
            state1;
        }
        """
        graph = graphviz.Source(dot_source)

        class StateFunctions:
            async def state1(self, context, executor):
                pass

        executor = EngineExecutor(graph, StateFunctions())
        await executor.run()
        self.assertEqual(executor.current_state, "__end__")
        self.assertEqual(len(executor.interaction_history), 3) # Includes final transition
        self.assertIn("No outgoing edges from state: state1", executor.interaction_history[1][1])

    async def test_interaction_history_content(self):
        dot_source = """
                strict digraph {
                    __start__ -> state1;
                    state1 -> __end__;
                }
                """
        graph = graphviz.Source(dot_source)

        class StateFunctions:
            async def state1(self, context, executor):
                await executor._request_input("Enter your name:")
                await executor.send_input("John Doe")

        executor = EngineExecutor(graph, StateFunctions())
        await executor.run()

        self.assertEqual(len(executor.interaction_history), 5)
        self.assertEqual(executor.interaction_history[0], ("system", "Transition to state: __start__"))
        self.assertEqual(executor.interaction_history[1], ("system", "Transition to state: state1"))
        self.assertEqual(executor.interaction_history[2], ("system", "Enter your name:"))
        self.assertEqual(executor.interaction_history[3], ("user", "John Doe"))
        self.assertEqual(executor.interaction_history[4], ("system", "Transition to state: __end__"))
