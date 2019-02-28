import ctypes

from TY_struct import *

def TY_getLibVersion(tylib):
	"""
	class TY_VERSION_INFO(ctypes.Structure):
		_fields_ = [ ('major', ctypes.c_int), 
					 ('minor', ctypes.c_int), 
					 ('patch', ctypes.c_int), 
					 ('reserved', ctypes.c_int) ]
	"""

	ver = TY_VERSION_INFO()
	res = tylib.TYLibVersion(ctypes.byref(ver))

	if res != 0:
		raise Exception('Get Lib version failed, return value: ', res)
	
	print('TY Lib version: {}.{}.{} '.format(ver.major, ver.minor, ver.patch))

	return ver.major, ver.minor, ver.patch

def TY_getInterfaceNumber(tylib):
	res = tylib.TYUpdateInterfaceList()
	if res != 0:
		raise Exception('Update interface list failed, return value: ', res)

	num_interface = ctypes.c_int()
	res = tylib.TYGetInterfaceNumber(ctypes.byref(num_interface))
	if res != 0:
		raise Exception('Get interface number failed, return value: ', res)

	print('{} interfaces found. '.format(num_interface.value))

	return num_interface.value

def TY_getInterfaceList(tylib):
	num_interface = TY_getInterfaceNumber(tylib)

	if num_interface == 0:
		return []

	"""
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
	"""

	interface_info_array = TY_INTERFACE_INFO * num_interface
	interfaces = interface_info_array()

	interface_number = ctypes.c_int()
	interface_number.value = num_interface

	res = tylib.TYGetInterfaceList(ctypes.pointer(interfaces), 
							 	   interface_number, 
							 	   ctypes.byref(interface_number))
	if res != 0:
		raise Exception('Get interfaces list failed, return value: ', res)

	index = 1
	for item in interfaces: 
		print('Found interface {}: '.format(index))
		index += 1

		print('    name: {}'.format(item.name.decode()))
		print('    id:   {}'.format(item.id.decode()))
		print('    type: {}'.format(item.type))

		if item.type == 4 or item.type == 8:
			print('     - MAC:       {}'.format(item.netInfo.mac.decode()))
			print('     - ip:        {}'.format(item.netInfo.ip.decode()))
			print('     - netmask:   {}'.format(item.netInfo.netmask.decode()))
			print('     - gateway:   {}'.format(item.netInfo.gateway.decode()))
			print('     - broadcast: {}'.format(item.netInfo.broadcast.decode()))

	return interfaces

def main():
	tylib = TY_initLib(TY_LIB_FILE)
	TY_getLibVersion(tylib = tylib)
	TY_getInterfaceNumber(tylib = tylib)
	TY_getInterfaceList(tylib = tylib)

if __name__ == '__main__':
	main()
