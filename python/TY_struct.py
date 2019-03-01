import ctypes

TY_LIB_FILE = "../../lib/libtycam.so"

TY_STATUS_LIST = {
    'TY_STATUS_OK'                : 0,
    'TY_STATUS_ERROR'             : -1001,
    'TY_STATUS_NOT_INITED'        : -1002,
    'TY_STATUS_NOT_IMPLEMENTED'   : -1003,
    'TY_STATUS_NOT_PERMITTED'     : -1004,
    'TY_STATUS_DEVICE_ERROR'      : -1005,
    'TY_STATUS_INVALID_PARAMETER' : -1006,
    'TY_STATUS_INVALID_HANDLE'    : -1007,
    'TY_STATUS_INVALID_COMPONENT' : -1008,
    'TY_STATUS_INVALID_FEATURE'   : -1009,
    'TY_STATUS_WRONG_TYPE'        : -1010,
    'TY_STATUS_WRONG_SIZE'        : -1011,
    'TY_STATUS_OUT_OF_MEMORY'     : -1012,
    'TY_STATUS_OUT_OF_RANGE'      : -1013,
    'TY_STATUS_TIMEOUT'           : -1014,
    'TY_STATUS_WRONG_MODE'        : -1015,
    'TY_STATUS_BUSY'              : -1016,
    'TY_STATUS_IDLE'              : -1017,
    'TY_STATUS_NO_DATA'           : -1018,
    'TY_STATUS_NO_BUFFER'         : -1019,
    'TY_STATUS_NULL_POINTER'      : -1020,
    'TY_STATUS_READONLY_FEATURE'  : -1021,
    'TY_STATUS_INVALID_DESCRIPTOR': -1022,
    'TY_STATUS_INVALID_INTERFACE' : -1023,
    'TY_STATUS_FIRMWARE_ERROR'    : -1024, 
    }


class TY_VERSION_INFO(ctypes.Structure):
	_fields_ = [('major', ctypes.c_int), 
				('minor', ctypes.c_int), 
				('patch', ctypes.c_int), 
				('reserved', ctypes.c_int)]

class TY_DEVICE_NET_INFO(ctypes.Structure):
	_fields_ = [('mac', ctypes.c_char * 32), 
				('ip', ctypes.c_char * 32), 
				('netmask', ctypes.c_char * 32), 
				('gateway', ctypes.c_char * 32), 
				('broadcast', ctypes.c_char * 32), 
				('reserved', ctypes.c_char * 96)]

class TY_INTERFACE_INFO(ctypes.Structure):
	_fields_ = [('name', ctypes.c_char * 32), 
				('id', ctypes.c_char * 32),
				('type', ctypes.c_int),
				('reserved', ctypes.c_char * 4), 
				('netInfo', TY_DEVICE_NET_INFO)]

class TY_DEVICE_BASE_INFO(ctypes.Structure):
	_fields_ = [('id', ctypes.c_char * 32), 
				('vendorName', ctypes.c_char * 32), 
				('modelName', ctypes.c_char * 32), 
				('hardwareVersion', TY_VERSION_INFO), 
				('firmwareVersion', TY_VERSION_INFO)]

def TY_initLib(lib_file):
	tylib = None

	tylib = ctypes.cdll.LoadLibrary(lib_file)
	res = tylib._TYInitLib()

	if res != 0:
		raise Exception('Lib initial failed, return value: ', res)

	return tylib


def TY_getLibVersion(tylib):

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
		print('Interface #{}: '.format(index))
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

		print('')

	return interfaces




