import logging

import requests

from app import config


def log(*args, level=logging.INFO, codeblock=None, **kwargs):
    items = [x if isinstance(x, str) else repr(x) for x in args]
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
        webhook_msg += f"\n```\n{codeblock}\n```"
    requests.post(config.AUDIT_WEBHOOK, json={"content": webhook_msg})
