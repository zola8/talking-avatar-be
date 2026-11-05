# How the streaming works

Frontend:  POST /chat/stream

- Headers: X-User-Id: <uuid>, Content-Type: application/json
- Body: {"agent_id": "writer", "content": "hello"}

Backend:

1. ChatService.stream_handle(user_id, agent_id, content)
2. Validates agent_id is in registry → if not, yields event: error
3. Persists the user message immediately
4. Loads full history from store (in-memory for now; Postgres later)
5. Calls agent.iter(history, content) — yields SSE event dicts
    - For PydantAI agent: agent.iter() runs the LLM, yielding:
        - FunctionToolCallEvent → event: step (tool_call)
        - FunctionToolResultEvent → event: step (tool_result)
        - PartDeltaEvent → event: delta (text chunk)
        - ThinkingPartDelta → event: step (reasoning)
        - FinalResultEvent → marks completion
    - For EchoAgent: fake steps + chunked deltas for testing
6. On event: final — persists the assistant message (with embedded steps)
7. Yields event: done
8. Connection closes

Frontend SSE dispatcher:

- event: step → logWindow.appendStep()
- event: delta → chatWindow.appendText()
- event: final → chatWindow.finalize(), messagesStore.add()
- event: done → close stream
- event: error → show error in both
