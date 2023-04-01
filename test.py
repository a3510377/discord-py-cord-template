import traceback


def fun():
    s = traceback.extract_stack()
    print(s[-2].filename)


fun()
