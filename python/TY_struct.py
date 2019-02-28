import ctypes

TY_LIB_FILE = "../../lib/libtycam.so"

def TY_initLib(lib_file):
	tylib = ctypes.cdll.LoadLibrary(lib_file)

	res = tylib._TYInitLib()

	if res != 0:
		raise Exception('Lib initial failed, return value: ', res)

	return tylib

class TY_VERSION_INFO(ctypes.Structure):
	_fields_ = [ ('major', ctypes.c_int), 
				 ('minor', ctypes.c_int), 
				 ('patch', ctypes.c_int), 
				 ('reserved', ctypes.c_int) ]

class TY_DEVICE_NET_INFO(ctypes.Structure):
	_fields_ = [ ('mac', ctypes.c_char * 32), 
				 ('ip', ctypes.c_char * 32), 
				 ('netmask', ctypes.c_char * 32), 
				 ('gateway', ctypes.c_char * 32), 
				 ('broadcast', ctypes.c_char * 32), 
				 ('reserved', ctypes.c_char * 96) ]

class TY_INTERFACE_INFO(ctypes.Structure):
	_fields_ = [ ('name', ctypes.c_char * 32), 
				 ('id', ctypes.c_char * 32),
				 ('type', ctypes.c_int),
				 ('reserved', ctypes.c_char * 4), 
				 ('netInfo', TY_DEVICE_NET_INFO) ]