import ctypes

from TY_struct import *


def main():     
	tylib = TY_initLib(TY_LIB_FILE)     
	print('')
	TY_getLibVersion(tylib = tylib)     
	print('')     
	ifaces = TY_getInterfaceList(tylib = tylib)

	index = 1
	for item in ifaces: 
		print('Interface #{}: '.format(index))
		index += 1

		print('    name: {}'.format(item.name.decode()))
		print('    id:   {}'.format(item.id.decode()))
		print('    type: {}'.format(item.type))

		if item.type == TY_INTERFACE_TYPE_LIST['TY_INTERFACE_ETHERNET'] \
			or item.type == TY_INTERFACE_TYPE_LIST['TY_INTERFACE_ETHERNET']:

			print('     - MAC:       {}'.format(item.netInfo.mac.decode()))
			print('     - ip:        {}'.format(item.netInfo.ip.decode()))
			print('     - netmask:   {}'.format(item.netInfo.netmask.decode()))
			print('     - gateway:   {}'.format(item.netInfo.gateway.decode()))
			print('     - broadcast: {}'.format(item.netInfo.broadcast.decode()))

		devs = TY_getDeviceList(tylib, item.id)
		print('     {} devices found in the interface. '.format(len(devs)))	 

		for dev in devs:
			if dev.iface.type  == TY_INTERFACE_TYPE_LIST['TY_INTERFACE_ETHERNET'] \
				or dev.iface.type == TY_INTERFACE_TYPE_LIST['TY_INTERFACE_ETHERNET']:

				print("      - device {}: ".format(dev.id));
				print("            vender     : ".format(dev.vendorName.decode()))
				print("            model      : ".format(dev.modelName.decode()))
				print("            device MAC : ".format(dev.netInfo.mac.decode()))
				print("            device IP  : ".format(dev.netInfo.ip.decode()))

			else:

				print("     - Dev vonder {}: ".format(dev.vendorName.decode()))
				print("     - Dev model  {}: ".format(dev.modelName.decode()))

	tylib.TYDeinitLib()
	print("Done!")

if __name__ == '__main__':
	main()
