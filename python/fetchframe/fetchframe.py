import ctpyes

from TY_struct import *

TY_LIB_FILE = "../../lib/libtycam.so"

def TY_initLib(lib_file):
	tylib = ctypes.cdll.LoadLibrary(lib_file)

	res = tylib._TYInitLib()

	if res != 0:
		raise Exception('Lib initial failed, return value: ', res)

	return tylib

def main():
	tylib = TY_initLib(TY_LIB_FILE)

	color = 1
	ir = 1
	depth = 1

	

if __name__ == '__main__':
	main()