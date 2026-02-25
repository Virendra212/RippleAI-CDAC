@tool
def add_numbers(a: int, b: int) -> int:
    """Adds two integers when user asks explicitly to add numbers return the result."""
    logger.info(f"add_numbers TOOL CALLED → a={a}, b={b}")
    return f"{a + b} is the result of addition"


@tool
def addToDatabase(action: str, payload: dict | str):
    """
    Sends an action request to put details in database.
    """
    event = {
        "action": action,
        "payload": payload
    }

    producer.send(TOPIC, json.dumps(event).encode("utf-8"))
    producer.flush()

    return f"request has been sent to db. '{action}' has been triggered."


@tool
def addPostToKafka(action: str, payload: dict | str):
    """
    Send posts to users.
    """
    event = {
        "action": action,
        "payload": payload
    }

    producer.send(TOPIC, json.dumps(event).encode("utf-8"))
    producer.flush()
    return "Post sent to users."