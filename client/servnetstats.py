import sys
import socket
import multiprocessing
import glob

def get_iface_json(iface):

	# build our directory name
	directory = "/sys/class/net/{0}/statistics/".format(iface)

	# get all of the files in the directory with the stats for the interface
	files = glob.glob("{0}{1}".format(directory,"*"))
	
	# open json object
	json = "{"

	# iterate through each file and add it to the json object
	for afile in files:

		print "Processing {0} ...".format(afile)

		#open the file for reading
		f = open(afile,'r')

		# get the value from the file, removing any spaces or new lines
		value = f.readline().strip()

		# get the name of the file from it's long name
		parts = afile.split('/')
		name = parts[len(parts)-1]

		# add the name and value combo to the json object
		json += '"{0}":"{1}",'.format(name,value)

	# remove last comma
	json = json[0:len(json)-1]

	# close json object
	json += "}"

	# return our built json object
	return json

def net_listen(iface,host):

        # create a socket to work with
        s = socket.socket()

        # set the port we are going to listen on
        port = 28080

        print "Host: {0}, Port: {1}".format(host,port)

        # bind tot the host name and port
        s.bind((host, port))

        # listen for clients (max of 16)
        s.listen(16)

        # sit in a loop handling socket connections
        while True:
                # accept the client, note: blocking
                c, addr = s.accept()

                print "INFO: Client Connection Accepted"

                global bytes_per_second
                #payload = '{0}"BPS":"{1}"{2}\n\n'.format('{',bytes_per_second,'}')

		payload = get_iface_json(iface)

                # create our response string
                str_bps =  'HTTP/1.0 200 OK\n'
                str_bps += 'Content-Type: text/html\n'
                str_bps += 'Access-Control-Allow-Origin: *\n';
		str_bps += 'Content-Length: {0}\n\n'.format(len(payload))
                str_bps += payload

                print "INFO:\tSending:"
                print "INFO:\t\t{0}".format(str_bps)

                c.send(str_bps)
                c.close()

def main(argv):

	# make sure we have been passed in the information we need
	if( len(argv) != 3 ):
                print "Usage:\n"
                print "\tgetbandiwidth.py <interface_name> <host_address>\n\n";
                return

	print "Starting application."

	# decode input data
	iface = argv[1]
	host = argv[2]
	
	#files = get_iface_json(iface)

	#print files

	print "Launching Network Listening Thread ..."

	# create our thread to handle the network communications
	netthread = multiprocessing.Process(target=net_listen,args=(iface,host,))

	# start the thread
	netthread.start()
 
	#print "\tDone!"

if __name__ == '__main__': sys.exit(main(sys.argv))
