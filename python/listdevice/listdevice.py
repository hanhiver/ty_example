import ctypes

tylib = ctypes.cdll.LoadLibrary("../../lib/libtycam.so")

def TY_getLibVersion