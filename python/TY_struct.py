import ctypes

TY_LIB_FILE = "../../lib/libtycam.so"

def getkey(dict, value):
	return [ k for k,v in dict.items() if v == value ]

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

TY_INTERFACE_TYPE_LIST = {
	'TY_INTERFACE_UNKNOWN'        : 0,
    'TY_INTERFACE_RAW'            : 1,
    'TY_INTERFACE_USB'            : 2,
    'TY_INTERFACE_ETHERNET'       : 4,
    'TY_INTERFACE_IEEE80211'      : 8,
    'TY_INTERFACE_ALL'            : 0xffff,
}

TY_DEVICE_COMPONENT_LIST = {
    'TY_COMPONENT_DEVICE'         : 0x80000000, # Abstract component stands for whole device, always enabled
    'TY_COMPONENT_DEPTH_CAM'      : 0x00010000, # Depth camera
    'TY_COMPONENT_IR_CAM_LEFT'    : 0x00040000, # Left IR camera
    'TY_COMPONENT_IR_CAM_RIGHT'   : 0x00080000, # Right IR camera
    'TY_COMPONENT_RGB_CAM_LEFT'   : 0x00100000, # Left RGB camera
    'TY_COMPONENT_RGB_CAM_RIGHT'  : 0x00200000, # Right RGB camera
    'TY_COMPONENT_LASER'          : 0x00400000, # Laser
    'TY_COMPONENT_IMU'            : 0x00800000, # Inertial Measurement Unit
    'TY_COMPONENT_BRIGHT_HISTO'   : 0x01000000, # virtual component for brightness histogram of ir

    'TY_COMPONENT_RGB_CAM'        : 0x00100000 # Some device has only one RGB camera, map it to left
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

class TY_DEVICE_USB_INFO(ctypes.Structure):
	_fields_ = [('bus', ctypes.c_int), 
				('addr', ctypes.c_int), 
				('reserved', ctypes.c_char * 248)]

class TY_INTERFACE_INFO(ctypes.Structure):
	_fields_ = [('name', ctypes.c_char * 32), 
				('id', ctypes.c_char * 32),
				('type', ctypes.c_int),
				('reserved', ctypes.c_char * 4), 
				('netInfo', TY_DEVICE_NET_INFO)]


class TY_DEVICE_BASE_INFO(ctypes.Structure):
	
	class _UNION(ctypes.Union):
		_fields_ = [('netInfo', TY_DEVICE_NET_INFO), 
					('usbInfo', TY_DEVICE_USB_INFO)]

	_anonymous_ = ('_union', )

	_fields_ = [('iface', TY_INTERFACE_INFO), 
				('id', ctypes.c_char * 32), 
				('vendorName', ctypes.c_char * 32), 
				('modelName', ctypes.c_char * 32), 
				('hardwareVersion', TY_VERSION_INFO), 
				('firmwareVersion', TY_VERSION_INFO), 
				('_union', _UNION), 
				('reserved', ctypes.c_char * 256)]

class TY_ENUM_ENTRY(ctypes.Structure):
	_fields_ = [('description', ctypes.c_char * 64), 
				('value', ctypes.c_int), 
				('reserved', ctypes.c_int * 3)]

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

	return interfaces


def TY_getDeviceList(tylib, iface_id):

	hIface = ctypes.c_void_p()
		
	res = tylib.TYOpenInterface(iface_id, ctypes.byref(hIface))
	if res != 0:
		raise Exception('TYOpenInterface failed, return value: ', res)

	res = tylib.TYUpdateDeviceList(hIface)
	if res != 0:
		raise Exception('TYUpdateDeviceList failed, return value: ', res)

	num_device = ctypes.c_int(0)
	res = tylib.TYGetDeviceNumber(hIface, ctypes.byref(num_device))
	if res != 0:
		raise Exception('TYGetDeviceNumber failed, return value: ', res)
	
	if num_device.value == 0:
		return []

	dev_info_array = TY_DEVICE_BASE_INFO * num_device.value

	devs = dev_info_array()
	res = tylib.TYGetDeviceList(hIface, 
								ctypes.pointer(devs), 
								num_device, 
								ctypes.byref(num_device))

	if res != 0:
		raise Exception('TYGetDeviceList failed, return value: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	if len(devs) != num_device.value:
		raise Exception('TYGetDeviceList error, wrong device number: ', len(devs))

	for dev in devs:
		if dev.iface.type  != TY_INTERFACE_TYPE_LIST['TY_INTERFACE_ETHERNET'] \
			and dev.iface.type != TY_INTERFACE_TYPE_LIST['TY_INTERFACE_ETHERNET']:

			handle = ctypes.c_void_p(0)

			res = tylib.TYOpenDevice(hIface, dev.id, ctypes.byref(handle))
			
			if res == 0:
				tylib.TYGetDeviceInfo(handle, ctypes.byref(dev))
				tylib.TYCloseDevice(handle)
			else: 
				raise Exception('TYOpenDevice failed, return value: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	tylib.TYCloseInterface(hIface)	

	return devs 



