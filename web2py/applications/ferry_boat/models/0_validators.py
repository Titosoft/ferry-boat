# -*- coding: utf-8 -*-
import os
class IS_PATH(object):
    def __init__(self, error_message='use a valid unix path'):
        self.error_message = error_message
    def __call__(self, value):
        try:
            if not os.path.isabs(value):
                raise Exception("Invalid Path")
            else:
                return (value, None)
        except:
            return (value, self.error_message)
