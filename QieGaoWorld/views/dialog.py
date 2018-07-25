# 自定义的dialog（用来替换UIKit自带的dialog）
import json
import logging

from django.template.loader import render_to_string


# status: 'failed' 'ok', dialog_type: 'primary' 'danger' 'success' 'warning', text: 你想说的话
# ext: 扩展dict，将被加入response中，具体请看源代码
def dialog(status, dialog_type, text, ext=None):
    if ext is None:
        ext = {}
    response = {
        "status": status,
        "msg": render_to_string("dialog.html", {
            'type': dialog_type,
            'text': text
        })
    }
    for e in ext:
        response[e] = ext[e]
    return json.dumps(response)
