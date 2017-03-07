
import traceback

def printerr(e):
    traceback.print_exception(type(e), e, e.__traceback__)
