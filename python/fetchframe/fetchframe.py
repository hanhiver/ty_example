import ctypes

from TY_struct import *

TY_LIB_FILE = "../../lib/libtycam.so"
SELECTED_IFACE = 1


def main():
	tylib = TY_initLib(TY_LIB_FILE)
	ifaces = TY_getInterfaceList(tylib = tylib) 

	hIface = ctypes.c_void_p()
	res = tylib.TYOpenInterface(ifaces[SELECTED_IFACE], ctypes.byref(hIface))
	if res != 0:
		raise Exception('TYOpenInterface failed, return value: ', res)

	res = tylib.TYUpdateDeviceList(hIface)
	if res != 0:
		raise Exception('TYUpdateDeviceList failed, return value: ', res)

	num_device = ctypes.c_int()
	res = tylib.TYGetDeviceNumber(hIface, ctypes.byref(num_device))
	if res != 0:
		raise Exception('TYGetDeviceNumber failed, return value: ', res)

	print('{} devices found in the interface. '.format(num_device.value))	 



if __name__ == '__main__':
	main()