#! /usr/bin/env python

import argparse
from docker import Client
import nagiosplugin


class Docker(nagiosplugin.Resource):

	def __init__(self, name_container):
		self.name_con = name_container

	def probe(self):
                '''Checks docker container state.

                 This method returns the following metrics: 

                `State` of container 

                '''

		c = Client(base_url='unix://var/run/docker.sock')

                # try to connect the docker service, and catch an exception if we
                # can't.

		self.container_state = c.inspect_container(self.name_con)['State']['Running']

		metrics = [
                            nagiosplugin.Metric('Container_running', self.container_state, context='default')
                          ]

		return metrics


class DockerSummary(nagiosplugin.Summary):
	#def verbose(self, results):
	#	super(DockerSummary, self).verbose(results)
	def __init__(self, name_container):
		self.name_con = name_container

	def ok(self, results):
		c = Client(base_url='unix://var/run/docker.sock')
		ip_address = c.inspect_container(self.name_con)['NetworkSettings']['IPAddress']
		return "IP Address %s" % ip_address

@nagiosplugin.guarded

def main():
	argp = argparse.ArgumentParser()
	argp.add_argument('-n', '--name', metavar='NAME',
                          help='Name of container'),

	args = argp.parse_args()

        # create our check object, if service metric !=0, consider that critical.
        #Nagios Exit Codes
	#Exit Code	Status
        #   0              OK
	#   1	        WARNING
        #   2	        CRITICAL
        #   3	        UNKNOWN
	check = nagiosplugin.Check(Docker(args.name, ),
                                   nagiosplugin.ScalarContext('Container_running', '0', '0', fmt_metric=''),
                                   DockerSummary(args.name))
	
	check.main(args.name)


if __name__ == '__main__':
	main()

