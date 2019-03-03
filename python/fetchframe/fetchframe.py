import ctypes

from TY_struct import *

TY_LIB_FILE = "../../lib/libtycam.so"
SELECTED_IFACE = 1


def main():
	tylib = TY_initLib(TY_LIB_FILE)
	ifaces = TY_getInterfaceList(tylib = tylib) 

	selected = []

	for iface in ifaces:
		devs = TY_getDeviceList(tylib, iface.id)
		if len(devs) > 0:
			selected.append(devs)
			selectedDev = devs[0]
		else:
			continue

	print('{} devices found. '.format(len(selected)))


	hIface = ctypes.c_void_p(0) #TY_INTERFACE_HANDLE
	hDevice = ctypes.c_void_p(0) #TY_DEV_HANDLE
	hColorIspHandle = ctypes.c_void_p(0) #TY_ISP_HANDLE

	res = tylib.TYOpenInterface(selectedDev.iface.id, ctypes.byref(hIface))
	if res != 0:
		raise Exception('TYOpenInterface failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	res = tylib.TYOpenDevice(hIface, selectedDev.id, ctypes.byref(hDevice))
	if res != 0:
		raise Exception('TYOpenDevice failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	allComps = ctypes.c_int(0)
	res = tylib.TYGetComponentIDs(hDevice, ctypes.byref(allComps))
	if res != 0:
		raise Exception('TYGetComponentIDs failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	if allComps.value & TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_RGB_CAM']:
		print("Has RGB camera, open it")
		
		res = tylib.TYEnableComponents(hDevice, TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_RGB_CAM'])
		if res != 0:
			raise Exception('TYEnableComponents TY_COMPONENT_RGB_CAM failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

		res = tylib.TYISPCreate(ctypes.byref(hColorIspHandle))
		if res != 0:
			raise Exception('TYISPCreate failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	if allComps.value & TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_IR_CAM_LEFT']:
		print("Has IR left camera, open it")

		res = tylib.TYEnableComponents(hDevice, TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_IR_CAM_LEFT'])
		if res != 0:
			raise Exception('TYEnableComponents TY_COMPONENT_IR_CAM_LEFT failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	if allComps.value & TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_IR_CAM_RIGHT']:
		print("Has IR right camera, open it")

		res = tylib.TYEnableComponents(hDevice, TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_IR_CAM_RIGHT'])
		if res != 0:
			raise Exception('TYEnableComponents TY_COMPONENT_IR_CAM_RIGHT failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	print("Configure components, open depth cam")
	if allComps.value & TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_DEPTH_CAM']:
		entry_num = ctypes.c_int(0)
		res = tylib.TYGetEnumEntryCount(hDevice, 
										TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_DEPTH_CAM'], 
										TY_FEATURE_ID_LIST['TY_ENUM_IMAGE_MODE'],
										ctypes.byref(entry_num))
		if res != 0:
			raise Exception('TYGetEnumEntryCount failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

		print('{} entry_num found. '.format(entry_num.value))

		if entry_num.value == 0:
			raise Exception('No emnu_entry found: {}'.format('TY_STATUS_ERROR'))

		enum_entry_array = TY_ENUM_ENTRY * entry_num.value
		image_mode_list = enum_entry_array()
		res = tylib.TYGetEnumEntryInfo(hDevice, 
									   TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_DEPTH_CAM'], 
									   TY_FEATURE_ID_LIST['TY_ENUM_IMAGE_MODE'],
									   ctypes.byref(image_mode_list), 
									   entry_num, 
									   ctypes.byref(entry_num))
		if res != 0:
			raise Exception('TYGetEnumEntryInfo TY_COMPONENT_DEPTH_CAM, TY_ENUM_IMAGE_MODE failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

		for image_mode in image_mode_list:
			width = (image_mode.value & 0x00ffffff) >> 12
			height = (image_mode.value & 0x00ffffff) & 0x0fff
			print("width = {}, height = {}. ".format(width, height))
			if width == 640 or height == 640: 
				print("Select Depth Image Mode: {}".format(image_mode.description.decode()))
				res = tylib.TYSetEnum(hDevice, 
									  TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_DEPTH_CAM'], 
									  TY_FEATURE_ID_LIST['TY_ENUM_IMAGE_MODE'], 
									  image_mode.value)
				if res == TY_STATUS_LIST['TY_STATUS_OK'] or res == TY_STATUS_LIST['TY_STATUS_NOT_PERMITTED']:
					break

		res = tylib.TYEnableComponents(hDevice, TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_DEPTH_CAM'])
		if res != 0:
			raise Exception('TYEnableComponents TY_COMPONENT_DEPTH_CAM failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	tylib.TYCloseDevice(hDevice)
	tylib.TYCloseInterface(hIface)
	tylib.TYISPRelease(ctypes.byref(hColorIspHandle))
	tylib.TYDeinitLib()
	print("Done!")


	 



if __name__ == '__main__':
	main()