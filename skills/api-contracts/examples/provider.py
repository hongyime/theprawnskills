"""Synthetic provider: identifiers enter as exact text, before JSON serialization."""
import json


def order_wire(found: bool = True) -> bytes:
    if found:
        body = {'status': 200, 'data': {'id': '9007199254740993',
                                       'label': 'Sample order', 'assignedTo': None}}
    else:
        body = {'status': 404, 'error': {'code': 'NOT_FOUND', 'message': 'Order missing'}}
    return json.dumps(body).encode('utf-8')
