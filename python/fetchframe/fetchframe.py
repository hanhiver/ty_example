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
		pass

	tylib.TYCloseDevice(hDevice)
	tylib.TYCloseInterface(hIface)
	tylib.TYISPRelease(ctypes.byref(hColorIspHandle))
	tylib.TYDeinitLib()
	print("Done!")


	 



if __name__ == '__main__':
	main()