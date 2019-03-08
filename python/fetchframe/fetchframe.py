import ctypes
import numpy as np
import cv2

from TY_struct import *

#TY_LIB_FILE = "../../libtycam.so"
#TY_LIB_FILE = "/home/grace/camport3/lib/linux/lib_x64/libtycam.so"
NUM_FRAMES = 100

def eventCallback(event_info, user_data):
	if event_info.contents.eventId == TY_EVENT_LIST['TY_EVENT_DEVICE_OFFLINE']:
		print('Event Callback: Device Offline. ')
	elif event_info.contents.eventId == TY_EVENT_LIST['TY_EVENT_LICENSE_ERROR']:
		print('Event Callback: License Error! ')

def main():
	print("\n=== Prepare TY Library ===")
	tylib = TY_initLib(TY_LIB_FILE)
	#print(tylib.TYISPUpdateDevice)
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

	print("\n=== Setup devices and components ===")

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

		print("Supported Modes: ")
		for image_mode in image_mode_list:
			print('    - ', image_mode.description.decode())

		for image_mode in image_mode_list:
			width = (image_mode.value & 0x00ffffff) >> 12
			height = (image_mode.value & 0x00ffffff) & 0x0fff
			#print("width = {}, height = {}. ".format(width, height))
			if width == 320 or height == 320: 
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

		scale_unit = ctypes.c_float(1.0)
		res = tylib.TYGetFloat(hDevice, 
							   TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_DEPTH_CAM'], 
							   TY_FEATURE_ID_LIST['TY_FLOAT_SCALE_UNIT'], 
							   ctypes.byref(scale_unit))
		#if res != 0:
		#	raise Exception('TYGetFloat TY_COMPONENT_DEPTH_CAM TY_FLOAT_SCALE_UNIT failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

		print("Get the scale_unit: ", scale_unit.value)

	print("\n=== Prepare image buffer ===")

	frameSize = ctypes.c_int()
	res = tylib.TYGetFrameBufferSize(hDevice, ctypes.byref(frameSize))
	if res != 0:
		raise Exception('TYGetFrameBufferSize failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	print("Frame size is: ", frameSize.value)

	#frameBuffer0 = ctypes.pointer(ctypes.create_string_buffer(frameSize.value))
	#frameBuffer1 = ctypes.pointer(ctypes.create_string_buffer(frameSize.value))

	frameBuffer0 = ctypes.create_string_buffer(frameSize.value)
	frameBuffer1 = ctypes.create_string_buffer(frameSize.value)

	print("Enqueue buffer[0] ({}, {})".format(frameBuffer0, frameSize.value))
	res = tylib.TYEnqueueBuffer(hDevice, frameBuffer0, frameSize.value)
	if res != 0:
		raise Exception('TYEnqueueBuffer frameBuffer0 failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	print("Enqueue buffer[1] ({}, {})".format(frameBuffer1, frameSize.value))
	res = tylib.TYEnqueueBuffer(hDevice, frameBuffer1, frameSize.value)
	if res != 0:
		raise Exception('TYEnqueueBuffer frameBuffer1 failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	print("Register event callback.")
	event = TY_EVENT_INFO() # TY_EVENT
	void_p_NULL = ctypes.c_void_p(0)
	callback_func = ctypes.CFUNCTYPE(None, ctypes.POINTER(TY_EVENT_INFO), ctypes.c_void_p)
	callback = callback_func(eventCallback)
	res = tylib.TYRegisterEventCallback(hDevice, ctypes.byref(event), void_p_NULL)
	if res != 0:
		raise Exception('TYRegisterEventCallback failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	hasTrigger = ctypes.c_bool()
	res = tylib.TYHasFeature(hDevice, 
							 TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_DEVICE'], 
							 TY_FEATURE_ID_LIST['TY_STRUCT_TRIGGER_PARAM'], 
							 ctypes.byref(hasTrigger))
	if res != 0:
		raise Exception('TYHasFeature TY_COMPONENT_DEVICE TY_STRUCT_TRIGGER_PARAM failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)


	if hasTrigger.value: 
		print("Device has a trigger, disable it. ")
		trigger = TY_TRIGGER_PARAM()
		trigger.mode = TY_TRIGGER_MODE_LIST['TY_TRIGGER_MODE_OFF']
		res = tylib.TYSetStruct(hDevice, 
								TY_DEVICE_COMPONENT_LIST['TY_COMPONENT_DEVICE'], 
								TY_FEATURE_ID_LIST['TY_STRUCT_TRIGGER_PARAM'], 
								ctypes.byref(trigger),
								ctypes.sizeof(trigger))
		if res != 0:
			raise Exception('TYSetStruct TY_COMPONENT_DEVICE TY_STRUCT_TRIGGER_PARAM failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	else:
		print("Device has no trigger. ")

	print("\n=== Fetch the frames ===")

	print("Start Capture ")
	res = tylib.TYStartCapture(hDevice)
	if res != 0:
		raise Exception('TYStartCapture failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)


	frame = TY_FRAME_DATA()
	index = 1

	print("Get into loop to fetch {} frames.".format(NUM_FRAMES))

	frameBuffer = ctypes.create_string_buffer(frameSize.value)

	for i in range(NUM_FRAMES):
		res = tylib.TYFetchFrame(hDevice, ctypes.byref(frame), -1)
		if res == 0:
			print("Get frame {}".format(index))
			index += 1

			print("Buffer size of the frame: ", frame.bufferSize)
			out = phaseFrame(frame)

			for channel in out:
				print("OUT channel: <{}>, image shape: {}.".format(channel, out[channel].shape))
				if channel == 'depth':
					np.savetxt('depth.csv', out[channel], fmt = '%d', delimiter = ',')

					max_level = out[channel].max()
					min_level = (out[channel][out[channel] > 0]).min()
					ptp_level = max_level - min_level

					print("MAX Level is: {}, MIN level is: {}.".format(max_level, min_level))

					for i in range(out[channel].shape[0]):
						for j in range(out[channel].shape[1]):
							if out[channel][i][j] > 0:
								out[channel][i][j] - min_level

					image_norm = out[channel] * 256 / ptp_level
					cv2.namedWindow('image', cv2.WINDOW_NORMAL)
					cv2.imshow('image', image_norm)
					#cv2.waitKey(0)
					if cv2.waitKey(10) & 0xFF == ord('q'):
						break
			
			#print("Update ISP device. ")
			#tylib.TYISPUpdateDevice(hColorIspHandle)

			print("Enqueue the buffers. ")
			#frame.userBuffer = frameBuffer
			print("Enqueue frame.userBuffer ({:x}, {})".format(frame.userBuffer, frame.bufferSize))
			#ret = tylib.TYEnqueueBuffer(hDevice, frame.userBuffer, frame.bufferSize)
			ret = tylib.TYEnqueueBuffer(hDevice, frameBuffer, frame.bufferSize)
			if ret != 0:
				raise Exception('TYEnqueueBuffer failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

		else:
			raise Exception('TYFetchFrame failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)
	

	print("Finished frames fetch, stop capture. ")
	res = tylib.TYStopCapture(hDevice)
	if res != 0:
		raise Exception('TYStopCapture failed: {}'.format(getkey(TY_STATUS_LIST, res)), res)

	print("Close the devices. ")
	tylib.TYCloseDevice(hDevice)

	print("Close the interface. ")
	tylib.TYCloseInterface(hIface)
	tylib.TYISPRelease(ctypes.byref(hColorIspHandle))
	tylib.TYDeinitLib()
	print("Done!")



if __name__ == '__main__':
	main()