import logging

import requests

from app import config


def _send(content):
    requests.post(config.AUDIT_WEBHOOK, json={"content": content})


def log(*args, level=logging.INFO, codeblock=None, **kwargs):
    items = [str(x) for x in args]
    for key, value in kwargs.items():
        items.append(f"{key}={repr(value)}")
    console_msg = " ".join(items)
    if codeblock:
        console_msg += "\n" + codeblock
    logging.log(level, msg=console_msg)

    if not config.AUDIT_WEBHOOK:
        return

    webhook_msg = "\n".join(items).replace("`", "\\`")
    if codeblock:
        webhook_msg_codeblock = f"{webhook_msg}\n```\n{codeblock}\n```"
    else:
        webhook_msg_codeblock = webhook_msg

    if len(webhook_msg_codeblock) < 2000:
        _send(webhook_msg_codeblock)
        return
    chunks = [
        webhook_msg[i : i + 2000] for i in range(0, len(webhook_msg), 2000)
    ]
    for i in range(0, len(codeblock), 1900):
        content = codeblock[i : i + 1900]
        chunks.append(f"```\n{content.strip()}\n```")
    for chunk in chunks:
        _send(chunk)
