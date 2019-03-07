import ctypes
import numpy as np

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

TY_FEATURE_TYPE_LIST = {
    'TY_FEATURE_INT'              : 0x1000,
    'TY_FEATURE_FLOAT'            : 0X2000,
    'TY_FEATURE_ENUM'             : 0x3000,
    'TY_FEATURE_BOOL'             : 0x4000,
    'TY_FEATURE_STRING'           : 0x5000,
    'TY_FEATURE_BYTEARRAY'        : 0x6000,
    'TY_FEATURE_STRUCT'           : 0x7000,
}

TY_FEATURE_ID_LIST = {
    'TY_STRUCT_CAM_INTRINSIC'         : 0x0000 | TY_FEATURE_TYPE_LIST['TY_FEATURE_STRUCT'], # see TY_CAMERA_INTRINSIC
    'TY_STRUCT_EXTRINSIC_TO_LEFT_IR'  : 0x0001 | TY_FEATURE_TYPE_LIST['TY_FEATURE_STRUCT'], # extrinsic from current component to left IR, see TY_CAMERA_EXTRINSIC
    'TY_STRUCT_CAM_DISTORTION'        : 0x0006 | TY_FEATURE_TYPE_LIST['TY_FEATURE_STRUCT'], # see TY_CAMERA_DISTORTION
    'TY_STRUCT_CAM_CALIB_DATA'        : 0x0007 | TY_FEATURE_TYPE_LIST['TY_FEATURE_STRUCT'], # see TY_CAMERA_CALIB_INFO

    'TY_INT_PERSISTENT_IP'            : 0x0010 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],
    'TY_INT_PERSISTENT_SUBMASK'       : 0x0011 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],
    'TY_INT_PERSISTENT_GATEWAY'       : 0x0012 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],
    'TY_BOOL_GVSP_RESEND'             : 0x0013 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'],
    'TY_INT_PACKET_DELAY'             : 0x0014 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],    # microseconds
    'TY_INT_ACCEPTABLE_PERCENT'       : 0x0015 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],
    'TY_INT_NTP_SERVER_IP'            : 0x0016 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],    # Ntp server IP
    'TY_STRUCT_CAM_STATISTICS'        : 0x00ff | TY_FEATURE_TYPE_LIST['TY_FEATURE_STRUCT'], # statistical information, see TY_CAMERA_STATISTICS

    'TY_INT_WIDTH_MAX'                : 0x0100 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],
    'TY_INT_HEIGHT_MAX'               : 0x0101 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],
    'TY_INT_OFFSET_X'                 : 0x0102 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],
    'TY_INT_OFFSET_Y'                 : 0x0103 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],
    'TY_INT_WIDTH'                    : 0x0104 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Image width
    'TY_INT_HEIGHT'                   : 0x0105 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Image height
    'TY_ENUM_IMAGE_MODE'              : 0x0109 | TY_FEATURE_TYPE_LIST['TY_FEATURE_ENUM'], # Resolution-PixelFromat mode, see TY_IMAGE_MODE_LIST

    #@breif scale unit
    #depth image is uint16 pixel format with default millimeter unit ,for some device  can output Sub-millimeter accuracy data
    #the acutal depth (mm): PxielValue * ScaleUnit 
    'TY_FLOAT_SCALE_UNIT'             : 0x010a | TY_FEATURE_TYPE_LIST['TY_FEATURE_FLOAT'], 

    'TY_ENUM_TRIGGER_ACTIVATION'      : 0x0201 | TY_FEATURE_TYPE_LIST['TY_FEATURE_ENUM'], # Trigger activation, see TY_TRIGGER_ACTIVATION_LIST
    'TY_INT_FRAME_PER_TRIGGER'        : 0x0202 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Number of frames captured per trigger
    'TY_STRUCT_TRIGGER_PARAM'         : 0x0523 | TY_FEATURE_TYPE_LIST['TY_FEATURE_STRUCT'],  # param of trigger, see TY_TRIGGER_PARAM
    'TY_BOOL_KEEP_ALIVE_ONOFF'        : 0x0203 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Keep Alive switch
    'TY_INT_KEEP_ALIVE_TIMEOUT'       : 0x0204 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Keep Alive timeout
    'TY_BOOL_CMOS_SYNC'               : 0x0205 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Cmos sync switch
    'TY_INT_TRIGGER_DELAY_US'         : 0x0206 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Trigger delay time, in microseconds
    'TY_BOOL_TRIGGER_OUT_IO'          : 0x0207 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Trigger out IO

    'TY_BOOL_AUTO_EXPOSURE'           : 0x0300 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Auto exposure switch
    'TY_INT_EXPOSURE_TIME'            : 0x0301 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Exposure time in percentage
    'TY_BOOL_AUTO_GAIN'               : 0x0302 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Auto gain switch
    'TY_INT_GAIN'                     : 0x0303 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Sensor Gain
    'TY_BOOL_AUTO_AWB'                : 0x0304 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Auto white balance

    'TY_INT_LASER_POWER'              : 0x0500 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Laser power level
    'TY_BOOL_LASER_AUTO_CTRL'         : 0x0501 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Laser auto ctrl

    'TY_BOOL_UNDISTORTION'            : 0x0510 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Output undistorted image
    'TY_BOOL_BRIGHTNESS_HISTOGRAM'    : 0x0511 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Output bright histogram
    'TY_BOOL_DEPTH_POSTPROC'          : 0x0512 | TY_FEATURE_TYPE_LIST['TY_FEATURE_BOOL'], # Do depth image postproc

    'TY_INT_R_GAIN'                   : 0x0520 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Gain of R channel
    'TY_INT_G_GAIN'                   : 0x0521 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Gain of G channel
    'TY_INT_B_GAIN'                   : 0x0522 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Gain of B channel

    'TY_INT_ANALOG_GAIN'              : 0x0524 | TY_FEATURE_TYPE_LIST['TY_FEATURE_INT'],  # Analog gain
}

TY_EVENT_LIST = {
    'TY_EVENT_DEVICE_OFFLINE'     : -2001,
    'TY_EVENT_LICENSE_ERROR'      : -2002,
    'TY_EVENT_FW_INIT_ERROR'      : -2003,
}

TY_TRIGGER_MODE_LIST = {
    'TY_TRIGGER_MODE_OFF'         : 0, #not trigger mode, continuous mode
    'TY_TRIGGER_MODE_SLAVE'       : 1, #slave mode, receive soft/hardware triggers
    'TY_TRIGGER_MODE_M_SIG'       : 2, #master mode 1, sending one trigger signal once received a soft/hardware trigger
    'TY_TRIGGER_MODE_M_PER'       : 3, #master mode 2, periodic sending one trigger signals, 'fps' param should be set
}

TY_PIXEL_BITS_LIST = {
    'TY_PIXEL_8BIT'               : 0x1 << 28,
    'TY_PIXEL_16BIT'              : 0x2 << 28,
    'TY_PIXEL_24BIT'              : 0x3 << 28,
    'TY_PIXEL_32BIT'              : 0x4 << 28,
}

TY_PIXEL_FORMAT_LIST = {
    'TY_PIXEL_FORMAT_UNDEFINED'   : 0,
    'TY_PIXEL_FORMAT_MONO'        : (TY_PIXEL_BITS_LIST['TY_PIXEL_8BIT']  | (0x0 << 24)), # 0x10000000
    'TY_PIXEL_FORMAT_BAYER8GB'    : (TY_PIXEL_BITS_LIST['TY_PIXEL_8BIT']  | (0x1 << 24)), # 0x11000000
    'TY_PIXEL_FORMAT_DEPTH16'     : (TY_PIXEL_BITS_LIST['TY_PIXEL_16BIT'] | (0x0 << 24)), # 0x20000000
    'TY_PIXEL_FORMAT_YVYU'        : (TY_PIXEL_BITS_LIST['TY_PIXEL_16BIT'] | (0x1 << 24)), # 0x21000000, yvyu422
    'TY_PIXEL_FORMAT_YUYV'        : (TY_PIXEL_BITS_LIST['TY_PIXEL_16BIT'] | (0x2 << 24)), # 0x22000000, yuyv422
    'TY_PIXEL_FORMAT_RGB'         : (TY_PIXEL_BITS_LIST['TY_PIXEL_24BIT'] | (0x0 << 24)), # 0x30000000
    'TY_PIXEL_FORMAT_BGR'         : (TY_PIXEL_BITS_LIST['TY_PIXEL_24BIT'] | (0x1 << 24)), # 0x31000000
    'TY_PIXEL_FORMAT_JPEG'        : (TY_PIXEL_BITS_LIST['TY_PIXEL_24BIT'] | (0x2 << 24)), # 0x32000000
    'TY_PIXEL_FORMAT_MJPG'        : (TY_PIXEL_BITS_LIST['TY_PIXEL_24BIT'] | (0x3 << 24)), # 0x33000000
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

class TY_EVENT_INFO(ctypes.Structure):
	_fields_ = [('eventId', ctypes.c_int), 
				('message', ctypes.c_char * 124)]

class TY_TRIGGER_PARAM(ctypes.Structure):
	_fields_ = [('mode', ctypes.c_int16), 
				('fps', ctypes.c_int8), 
				('rsvd', ctypes.c_int8)]

class TY_IMAGE_DATA(ctypes.Structure):
	_fields_ = [('timestamp', ctypes.c_uint64), 
				('imageIndex', ctypes.c_int32), 
				('status', ctypes.c_int32), 
				('componentID', ctypes.c_int32), 
				('size', ctypes.c_int32), 
				('buffer', ctypes.c_void_p),
				('width', ctypes.c_int32), 
				('height', ctypes.c_int32), 
				('pixelFormat', ctypes.c_int32), 
				('reserved', ctypes.c_int32 * 9)]

class TY_FRAME_DATA(ctypes.Structure):
	_fields_ = [('userBuffer', ctypes.c_void_p), 
				('bufferSize', ctypes.c_int32), 
				('validCount', ctypes.c_int32), 
				('reserved', ctypes.c_int32 * 6), 
				('image', TY_IMAGE_DATA * 10)]




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

def phaseFrame(frame):
	out = {'depth' : None, 
		   'color' : None, 
		   'ir_left' : None, 
		   'ir_right' : None}

	valid_count = frame.validCount

	for i in range(valid_count):
		#print("PHASE FRAME: {}".format(i))

		if frame.image[i].componentID == TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_DEPTH_CAM']:
			py_buf = ctypes.cast(frame.image[i].buffer, ctypes.POINTER(ctypes.c_uint16))
			np_image = np.ctypeslib.as_array(py_buf, shape = (frame.image[i].height, frame.image[i].width))
			#np_image = np_data.reshape((frame.image[i].height, frame.image[i].width))
			out['depth'] = np_image
			#print('Depth: Size: {}, Width: {}, Height: {}, shape: {}'.format(
			#		frame.image[i].size, 
			#		frame.image[i].width, 
			#		frame.image[i].height, 
			#		np_image.shape))

		elif frame.image[i].componentID == TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_IR_CAM_LEFT']:
			py_buf = ctypes.cast(frame.image[i].buffer, ctypes.POINTER(ctypes.c_uint8))
			np_image = np.ctypeslib.as_array(py_buf, shape = (frame.image[i].height, frame.image[i].width))
			out['ir_left'] = np_image
			#print('IR(L): Size: {}, Width: {}, Height: {}, shape: {}'.format(
			#		frame.image[i].size, 
			#		frame.image[i].width, 
			#		frame.image[i].height, 
			#		np_image.shape))

		elif frame.image[i].componentID == TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_IR_CAM_RIGHT']:
			py_buf = ctypes.cast(frame.image[i].buffer, ctypes.POINTER(ctypes.c_uint8))
			np_image = np.ctypeslib.as_array(py_buf, shape = (frame.image[i].height, frame.image[i].width))
			out['ir_right'] = np_image
			#print('IR(L): Size: {}, Width: {}, Height: {}, shape: {}'.format(
			#		frame.image[i].size, 
			#		frame.image[i].width, 
			#		frame.image[i].height,
			#		np_image.shape))


		elif frame.image[i].componentID == TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_RGB_CAM']:
			py_buf = ctypes.cast(frame.image[i].buffer, ctypes.POINTER(ctypes.c_uint8 * 2))
			np_image = np.ctypeslib.as_array(py_buf, shape = (frame.image[i].height, frame.image[i].width))
			out['color'] = np_image
			#print('Color: Size: {}, Width: {}, Height: {}, shape: {}, Pixel_format: {}'.format(
			#		frame.image[i].size, 
			#		frame.image[i].width, 
			#		frame.image[i].height, 
			#		np_image.shape, 
			#		getkey(TY_PIXEL_FORMAT_LIST, frame.image[i].pixelFormat) 
			#		))

	return out


		


