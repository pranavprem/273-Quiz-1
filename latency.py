#History on my Github, github.com/vanarp96/273-Quiz-1

import subprocess



hosts = [{"Name":"North California","ip":"50.18.56.1"}, {"Name":"North Virginia","ip":"23.23.255.255"}, {"Name":"Ireland","ip":"34.248.60.213"}, {"Name":"Tokyo","ip":"13.112.63.251"},{"Name":"Frankfurt","ip":"35.156.63.252"},{"Name":"London","ip":"52.56.34.0"},{"Name":"Singapore","ip":"46.51.216.14"},{"Name":"Seoul","ip":"52.78.63.252"},{"Name":"Ohio","ip":"52.14.64.0"},{"Name":"Oregon","ip":"35.160.63.253"},{"Name":"Mumbai","ip":"35.154.63.252"},{"Name":"Sao Paulo","ip":"52.67.255.254"},{"Name":"Sydney","ip":"13.54.63.252"},{"Name":"Central Canada","ip":"52.60.50.0"},{"Name":"GovCloud US WEST","ip":"52.222.9.163"}]
results = []
#i=0

choice = raw_input("Do you have a PC(1) or a MAC(2)?")

#print choice
flag=1
if int(choice) == 1:
	print "You chose PC. Please wait for all pings to complete. This could take a while."
	for host in hosts:
		#print "Completion " + str(i)
		#i=i+1
		#ping = subprocess.Popen(    ["ping", "-c", "3", host],    stdout = subprocess.PIPE,    stderr = subprocess.PIPE)
		ping = subprocess.Popen(["ping", "-n", "3", host["ip"]], stdout = subprocess.PIPE)
		for pingoutputline in ping.stdout.readlines():
			#if "avg" in pingoutputline:
			if "Average" in pingoutputline:
				#piece = pingoutputline.split("/")[4]
				piece = pingoutputline.split("Average")[1].split("ms")[0].split("= ")[1]
				results.append({"Name":host["Name"],"Average":float(piece),"Average Line":pingoutputline})
elif int(choice) == 2:
	print "You chose Mac. Please wait for all pings to complete. This could take a while."
	for host in hosts:
		#print "Completion " + str(i)
		#i=i+1
		ping = subprocess.Popen(    ["ping", "-c", "3", host["ip"]],    stdout = subprocess.PIPE,    stderr = subprocess.PIPE)
		#ping = subprocess.Popen(["ping", "-n", "3", host["ip"]], stdout = subprocess.PIPE)
		for pingoutputline in ping.stdout.readlines():
			if "avg" in pingoutputline:
			#if "Average" in pingoutputline:
				piece = pingoutputline.split("/")[4]
				#piece = pingoutputline.split("Average")[1].split("ms")[0].split("= ")[1]
				results.append({"Name":host["Name"],"Average":float(piece),"Average Line":pingoutputline})

else:
	print "please input either 1 for PC or 2 for Mac"
	flag = 0

if flag:
	results = sorted(results, key= lambda k: k["Average"])

	for result in results:
		print result["Name"] + " --- " + result["Average Line"]