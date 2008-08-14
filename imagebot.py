#! /usr/bin/python

from springbots.springbot import load_xml
from springbots.gear import *
import sys, optparse

#
# If this module its being running as main, execute main thread
#
if __name__ == "__main__":

	# Parses command line
	parser = optparse.OptionParser()
	parser.add_option("-n", "--number", dest="number", default=1,
		help="Number of springbots from file to draw", metavar="NUMBER")
	parser.add_option("-r", "--row", dest="row", default=10,
		help="Number of springbots on each row", metavar="NUMBER")

	(options, args) = parser.parse_args()

	options.number = int(options.number)
	options.row = int(options.row)

	if len(args) == 0:
		readfile = sys.stdin
		writefile = sys.stdout
	elif len(args) == 1:
		readfile = args[0]
		writefile = sys.stdout
	else:
		readfile = args[0]
		writefile = open(args[1], 'w')

	# Load springbots
	springbots = load_xml(readfile, limit=options.number)

	# Write xml header
	writefile.write(\
"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg  version="1.1" xmlns="http://www.w3.org/2000/svg">
""")

	x_offset = 0
	y_offset = 0

	for c, springbot in enumerate(springbots):

		if c != 0 and c % options.row == 0:
			x_offset = 0
			y_offset += (y2-y1) + RADIUS*2

		x1, y1, x2, y2 = springbot.boundingBox()
		offsetx = -x1 + RADIUS*2 + x_offset
		offsety = -y1 + RADIUS*2 + y_offset

		# Writes springbot structure to output
		writefile.write("<!-- ")
		for key, value in springbot._info.iteritems():
			writefile.write('%s="%s" ' % (key, str(value)))
		writefile.write("-->\n")

		for spring in springbot.springs:
			writefile.write(\
				'\t<!-- from="%d" to="%d" amplitude="%.4f" offset="%.4f" normal="%.4f" -->\n' % \
				(spring.a.id, spring.b.id, spring.amplitude, spring.offset, spring.normal))
			writefile.write(\
				'\t<line stroke="black" stroke-width="4" x1="%d" y1="%d" x2="%d" y2="%d"/>\n' % \
				 (spring.a.pos.x+offsetx, spring.a.pos.y+offsety, spring.b.pos.x+offsetx, spring.b.pos.y+offsety))

		for node in springbot.nodes:
			writefile.write('\t<!-- id="%d" -->\n' % node.id)
			writefile.write(\
			'\t<ellipse fill="white" stroke="aqua" stroke-width="3" transform="translate(%d,%d)" rx="%d" ry="%d"/>\n' % \
			(node.pos.x+offsetx, node.pos.y+offsety, RADIUS, RADIUS))

		x_offset += (x2-x1) + RADIUS*2

	# Writes xml tail
	writefile.write("</svg>\n")

	# Closes file
	if writefile is not sys.stdout:
		writefile.close()
	else:
		sys.stdout.flush()
