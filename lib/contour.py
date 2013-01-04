#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import fileinput
import math
import string
import spline

datapath = "../data"

class Contour:

    def __init__(self):
        self.name = ""
        self.description = ""
        self.top = []
        self.bottom = []
        self.holes = []
        self.labels = []

    def dist_2d(self, pt1, pt2):
        dx = pt2[0]-pt1[0]
        dy = pt2[1]-pt1[1]
        return math.sqrt(dx*dx + dy*dy)

    def simple_interp(self, points, v):
        index = spline.binsearch(points, v)
        n = len(points) - 1
        if index < n:ls

            xrange = points[index+1][0] - points[index][0]
            yrange = points[index+1][1] - points[index][1]
	    # print(" xrange = $xrange\n")
            percent = (v - points[index][0]) / xrange
	    # print(" percent = $percent\n")
            return points[index][1] + percent * yrange
        else:
            return points[index][1]

    def fit(self, maxpts = 30, maxerror = 0.1):
        self.top = list( self.curve_fit(self.top, maxpts, maxerror) )
        self.bottom = list( self.curve_fit(self.bottom, maxpts, maxerror) )

    def curve_fit(self, curve, maxpts = 30, maxerror = 0.1):
        wip = []

        # start with the end points
        n = len(curve)
        wip.append( curve[0] )
        wip.append( curve[n-1] )

        # iterate until termination conditions are met
        done = False
        while not done:
            maxy = 0
            maxx = 0
            maxdiff = 0
            maxi = -1
            # iterate over the orginal interior points
            for i in range(1, n-1):
                pt = curve[i]
                iy = self.simple_interp(wip, pt[0])
                diff = math.fabs(pt[1] - iy)
                if diff > maxdiff and diff > maxerror:
                    maxdiff = diff
                    maxi = i
                    maxx = pt[0]
                    maxy = pt[1]

            if maxi > -1:
                # found a match for a furthest off point
	        #print "($#wipx) inserting -> $maxx , $maxy at pos ";

                # find insertion point
                pos = 0
                wipn = len(wip)
                #print str(pos) + " " + str(wipn)
                while pos < wipn and maxx > wip[pos][0]:
                    pos += 1
                    #print pos
	        #print "$pos\n";
                wip.insert( pos, (maxx, maxy) )
            else:
                done = True

            if len(wip) >= maxpts:
                done = True

        return wip

    def display(self):
        for pt in self.top:
            print str(pt[0]) + " " + str(pt[1])
        for pt in self.bottom:
            print str(pt[0]) + " " + str(pt[1])

    def rotate_point( self, pt, angle ):
        rad = math.radians(angle)
        newx = pt[0] * math.cos(rad) - pt[1] * math.sin(rad)
        newy = pt[1] * math.cos(rad) + pt[0] * math.sin(rad)
        return (newx, newy)

    def rotate(self, angle):
        newtop = []
        newbottom = []
        newholes = []
        newlabels = []
        for pt in self.top:
            newtop.append( self.rotate_point(pt, angle) )
        for pt in self.bottom:
            newbottom.append( self.rotate_point(pt, angle) )
        for hole in self.holes:
            newpt = self.rotate_point( (hole[0], hole[1]), angle)
            newholes.append( (newpt[0], newpt[1], hole[2]) )
        for label in self.labels:
            newpt = self.rotate_point( (label[0], label[1]), angle)
            newlabels.append( (newpt[0], newpt[1], label[2], label[3] + angle, label[4]) )
        self.top = list(newtop)
        self.bottom = list(newbottom)
        self.holes = list(newholes)
        self.labels = list(newlabels)

    def scale(self, hsize, vsize):
        newtop = []
        newbottom = []
        newholes = []
        newlabels = []
        for pt in self.top:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            newtop.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            newbottom.append( (newx, newy) )
        for hole in self.holes:
            newx = ( hole[0] * hsize )
            newy = ( hole[1] * vsize )
            if hsize <= vsize:
                newr = math.fabs( hole[2] * hsize )
            else:
                newr = math.fabs( hole[2] * vsize )
            newholes.append( (newx, newy, newr) )
        for label in self.labels:
            newx = ( label[0] * hsize )
            newy = ( label[1] * vsize )
            newlabels.append( (newx, newy, label[2], label[3], label[4]) )
        self.top = list(newtop)
        self.bottom = list(newbottom)
        self.holes = list(newholes)
        self.labels = list(newlabels)

    def move(self, x, y):
        newtop = []
        newbottom = []
        newholes = []
        newlabels = []
        for pt in self.top:
            newx = pt[0] + x
            newy = pt[1] + y
            newtop.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] + x
            newy = pt[1] + y
            newbottom.append( (newx, newy) )
        for hole in self.holes:
            newx = hole[0] + x
            newy = hole[1] + y
            newholes.append( (newx, newy, hole[2]) )
        for label in self.labels:
            newx = label[0] + x
            newy = label[1] + y
            newlabels.append( (newx, newy, label[2], label[3], label[4]) )
        self.top = list(newtop)
        self.bottom = list(newbottom)
        self.holes = list(newholes)
        self.labels = list(newlabels)

    # rel top/bottom, tangent/vertical, xpos, ysize
    def cutout(self, side = "top", orientation = "tangent", xpos = 0, xsize = 0, ysize = 0):

        top = False
        if side == "top":
            top = True

        tangent = False
        if orientation == "tangent":
            tangent = True;

        curve = []
        if top:
            curve = list(self.top)
        else:
            curve = list(self.bottom)

        n = len(curve)

        newcurve = []
        ypos = self.simple_interp(curve, xpos)

        angle = 0
        if tangent:
            slopes = spline.derivative1(curve)
            index = spline.binsearch(curve, xpos)
            slope = slopes[index]
            rad = math.atan2(slope,1)
            angle = math.degrees(rad)
        if not top:
            angle += 180
            if angle > 360:
                angle -= 360
        xhalf = xsize / 2
        r0 = self.rotate_point( (-xhalf, 0), angle )
        r1 = self.rotate_point( (-xhalf, -ysize), angle )
        r2 = self.rotate_point( (xhalf, -ysize), angle )
        r3 = self.rotate_point( (xhalf, 0), angle )
        if tangent:
            p0 = ( r0[0] + xpos, r0[1] + ypos )
            p1 = ( r1[0] + xpos, r1[1] + ypos )
            p2 = ( r2[0] + xpos, r2[1] + ypos )
            p3 = ( r3[0] + xpos, r3[1] + ypos )
        else:
            x = r0[0] + xpos
            p0 = ( r0[0] + xpos, self.simple_interp(curve, x) )
            p1 = ( r1[0] + xpos, r1[1] + ypos )
            p2 = ( r2[0] + xpos, r2[1] + ypos )
            x = r3[0] + xpos
            p3 = ( r3[0] + xpos, self.simple_interp(curve, x) )

        i = 0
        # nose portion
        while (curve[i][0] < p0[0] and curve[i][0] < p3[0]) and i < n:
            newcurve.append( curve[i] )
            i += 1
        # cut out
        if top:
            newcurve.append( p0 )
            newcurve.append( p1 )
            newcurve.append( p2 )
            newcurve.append( p3 )
        else:
            newcurve.append( p3 )
            newcurve.append( p2 )
            newcurve.append( p1 )
            newcurve.append( p0 )
        # skip airfoil coutout points
        while (curve[i][0] <= p0[0] or curve[i][0] <= p3[0]) and i < n:
            i += 1
        # tail portion
        while i < n:
            newcurve.append( curve[i] )
            i += 1
        if top:
            self.top = list(newcurve)
        else:
            self.bottom = list(newcurve)

    def cutout_stringer(self, side = "top", orientation = "tangent", xpos = 0, xsize = 0, ysize = 0):
        self.cutout(side, orientation, xpos, xsize, ysize)

    def add_build_tab(self, side = "top", xpos = 0, xsize = 0, yextra = 0):
        # find the y value of the attach point and compute the size of
        # the tab needed
        bounds = self.get_bounds()
        if side == "top":
            ypos = self.simple_interp(self.top, xpos)
            ysize = bounds[1][1] - ypos + yextra
        else:
            ypos = self.simple_interp(self.bottom, xpos)
            ysize = ypos - bounds[0][1] + yextra
        self.cutout(side, "vertical", xpos, xsize, -ysize)

    def add_hole(self, xpos, ypos, radius):
        self.holes.append( (xpos, ypos, radius) )        

    def add_label(self, xpos, ypos, size, rotate, text):
        self.labels.append( (xpos, ypos, size, rotate, text) )        

    def project_point(self, top, slopes, index, orig, ysize):
        slope = slopes[index]
        rad = math.atan2(slope,1)
        angle = math.degrees(rad)
        #print "xpos " + str(xpos) + " angle = " + str(angle)
        if not top:
            angle += 180
            if angle > 360:
                angle -= 360
        r0 = self.rotate_point( (0, ysize), angle )
        pt = ( r0[0] + orig[0], r0[1] + orig[1] )
        if top and pt[1] < 0.0:
            pt = (pt[0], 0.0)
        elif not top and pt[1] > 0.0:
            pt = (pt[0], 0.0)
        return pt

    def cutout_sweep(self, side = "top", xstart = 0, xsize = 0, ysize = 0):
        top = False
        if side == "top":
            top = True

        curve = []
        if top:
            curve = list(self.top)
        else:
            curve = list(self.bottom)

        n = len(curve)
        newcurve = []

        # nose portion
        i = 0
        while curve[i][0] < xstart and i < n:
            newcurve.append( curve[i] )
            i += 1

        # anchor sweep
        ypos = self.simple_interp(curve, xstart)
        newcurve.append( (xstart, ypos) )

        # sweep cutout
        slopes = spline.derivative1(curve)
        dist = 0.0
        xpos = xstart
        index = spline.binsearch(curve, xpos)
        first = True
        next_dist = 0
        while dist + next_dist <= xsize and index < n:
            dist += next_dist
            ypos = self.simple_interp(curve, xpos)
            pt = self.project_point(top, slopes, index, (xpos, ypos), -ysize)
            newcurve.append( pt )
            if index < n - 1:
                nextpt = curve[index+1]
                next_dist = self.dist_2d( (xpos, ypos), nextpt )
                xpos = nextpt[0]
            index += 1

        if index < n - 1:
            # finish sweep (advance x in proportion to get close to the
            # right total sweep dist
            rem = xsize - dist
            print "rem = " + str(rem)
            pct = rem / next_dist
            print "pct of next step = " + str(pct)
            xpos = curve[index-1][0]
            dx = curve[index][0] - xpos
            xpos += dx * rem
            ypos = self.simple_interp(curve, xpos)
            pt = self.project_point(top, slopes, index-1, (xpos, ypos), -ysize)
            newcurve.append( pt )
            newcurve.append( (xpos, ypos) )

        # tail portion
        while index < n:
            newcurve.append( curve[index] )
            index += 1

        if top:
            self.top = list(newcurve)
        else:
            self.bottom = list(newcurve)

    def get_bounds(self):
        if len(self.top) < 1:
            return ( (0,0), (0,0) )
        pt = self.top[0]
        minx = pt[0]
        maxx = pt[0]
        miny = pt[1]
        maxy = pt[1]
        for pt in self.top + self.bottom:
            if pt[0] < minx:
                minx = pt[0]
            if pt[0] > maxx:
                maxx = pt[0]
            if pt[1] < miny:
                miny = pt[1]
            if pt[1] > maxy:
                maxy = pt[1]
        return ( (minx, miny), (maxx, maxy) )