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
	parser.add_option("-i", "--index", dest="index", default=0,
		help="Springbot index in population file", metavar="INDEX")

	(options, args) = parser.parse_args()

	if len(args) == 0:
		readfile = sys.stdin
		writefile = sys.stdout
	elif len(args) == 1:
		readfile = args[0]
		writefile = sys.stdout
	else:
		readfile = args[0]
		writefile = open(args[1], 'w')

	# Load springbot
	springbot = load_xml(readfile, limit=options.index+1)[options.index]
	x1, y1, x2, y2 = springbot.boundingBox()
	offsetx = -x1 + RADIUS*2
	offsety = -y1 + RADIUS*2

	# Writes springbot structure to output
	writefile.write(\
"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<!-- """)

	for key, value in springbot._info.iteritems():
		writefile.write('%s="%s" ' % (key, str(value)))

	writefile.write(\
"""-->
<svg  version="1.1" xmlns="http://www.w3.org/2000/svg">
""")

	for spring in springbot.springs:
		writefile.write(\
'\t<!-- from="%d" to="%d" amplitude="%.4f" offset="%.4f" normal="%.4f" -->\n' % \
(spring.a.id, spring.b.id, spring.amplitude, spring.offset, spring.normal))
		writefile.write(\
'\t<line stroke="black" stroke-width="2" x1="%d" y1="%d" x2="%d" y2="%d"/>\n' % \
 (spring.a.pos.x+offsetx, spring.a.pos.y+offsety, spring.b.pos.x+offsetx, spring.b.pos.y+offsety))

	for node in springbot.nodes:
		writefile.write('\t<!-- id="%d" -->\n' % node.id)
		writefile.write(\
'\t<ellipse fill="white" stroke="aqua" stroke-width="3" transform="translate(%d,%d)" rx="%d" ry="%d"/>\n' % \
(node.pos.x+offsetx, node.pos.y+offsety, RADIUS, RADIUS))

	writefile.write("</svg>\n")

	# Closes file
	if writefile is not sys.stdout:
		writefile.close()
	else:
		sys.stdout.flush()

