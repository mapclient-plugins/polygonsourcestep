"""
MAP Client, a program to generate detailed musculoskeletal models for OpenSim.
    Copyright (C) 2012  University of Auckland
    
This file is part of MAP Client. (http://launchpad.net/mapclient)

    MAP Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MAP Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MAP Client.  If not, see <http://www.gnu.org/licenses/>..
"""

from os import path
import vtk
from numpy import array
from xml.etree import ElementTree as ET
import xml

class Reader( object ):
    """Class for reading polygon files of various formats
    """
    
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        self._points = None
        self._triangles = None
        self._nPoints = None
        self._nFaces = None
        self._dimensions = None
        self.polydata = None
        
    def setFilename( self, filename ):
        self.filename = filename

    def read(self, filename=None):
        if filename is not None:
            self.filename = filename

        filePrefix, fileExt = path.splitext(self.filename)
        fileExt = fileExt.lower()
        if fileExt == '.obj':
            self.readOBJ()
        elif fileExt=='.wrl':
            self.readVRML()
        elif fileExt=='.stl':
            self.readSTL()
        elif fileExt=='.ply':
            self.readPLY()
        elif fileExt=='.vtp':
            self.readVTP()
        else:
            print('failed to open {}'.format(self.filename))
            raise ValueError('unknown file extension')
        
    def readVRML(self, filename=None):
        if filename is not None:
            self.filename = filename
        r = vtk.vtkVRMLImporter()
        r.SetFileName( self.filename )
        r.Update()
        actors = r.GetRenderer().GetActors()
        actors.InitTraversal()
        self.polydata = actors.GetNextActor().GetMapper().GetInput()
        
        if self.polydata.GetPoints()==None:
            raise IOError, 'file not loaded'
        else:
            self._loadPoints()
            self._loadTriangles()

    def readOBJ(self, filename=None):
        if filename is not None:
            self.filename = filename

        r = vtk.vtkOBJReader()
        r.SetFileName( self.filename )
        r.Update()
        self.polydata = r.GetOutput()
        
        if self.polydata.GetPoints()==None:
            raise IOError, 'file not loaded'
        else:
            self._loadPoints()
            self._loadTriangles()

    def readPLY(self, filename=None):
        if filename is not None:
            self.filename = filename

        r = vtk.vtkPLYReader()
        r.SetFileName( self.filename )
        r.Update()
        self.polydata = r.GetOutput()
        
        if self.polydata.GetPoints()==None:
            raise IOError, 'file not loaded'
        else:
            self._loadPoints()
            self._loadTriangles()
    
    def readSTL(self, filename=None):
        if filename is not None:
            self.filename = filename

        r = vtk.vtkSTLReader()
        r.SetFileName( self.filename )
        r.Update()
        self.polydata = r.GetOutput()
        
        if self.polydata.GetPoints()==None:
            raise IOError, 'file not loaded'
        else:
            self._loadPoints()
            self._loadTriangles()

    def readVTP(self, filename=None):
        if filename is not None:
            self.filename = filename

        if self._isXML(self.filename):
            r = vtk.vtkXMLPolyDataReader()
        else:
            r = vtk.vtkPolyDataReader()
        r.SetFileName( self.filename )
        r.Update()
        self.polydata = r.GetOutput()
        
        if self.polydata.GetPoints()==None:
            raise IOError, 'file not loaded'
        else:
            self._loadPoints()
            self._loadTriangles()

    def _isXML(self, f):
        """Check if file is an xml file
        """
        with open(f, 'r') as fp:
            l = fp.readline()
            
        if l[0]=='<':
            return True
        else:
            return False 

    def _loadPoints( self ):
        P = self.polydata.GetPoints().GetData()
        self._dimensions = P.GetNumberOfComponents()
        self._nPoints = P.GetNumberOfTuples()
        
        print 'loading %(np)i points in %(d)i dimensions'%{'np':self._nPoints, 'd':self._dimensions}
        
        if self._dimensions==1:
            self._points = array([P.GetTuple1(i) for i in xrange(self._nPoints)])
        elif self._dimensions==2:
            self._points = array([P.GetTuple2(i) for i in xrange(self._nPoints)])
        elif self._dimensions==3:
            self._points = array([P.GetTuple3(i) for i in xrange(self._nPoints)])
        elif self._dimensions==4:
            self._points = array([P.GetTuple4(i) for i in xrange(self._nPoints)])
        elif self._dimensions==9:
            self._points = array([P.GetTuple9(i) for i in xrange(self._nPoints)])
        
    def _loadTriangles( self ):
        polyData = self.polydata.GetPolys().GetData()
        X = [int(polyData.GetTuple1(i)) for i in xrange(polyData.GetNumberOfTuples())]
        
        # assumes that faces are triangular
        X = array(X).reshape((-1,4))
        self._nFaces = X.shape[0]
        self._triangles = X[:,1:]
        
        print 'loaded %(f)i faces'%{'f':self._nFaces}

supported_suffixes = ('auto', 'stl', 'wrl', 'obj', 'ply', 'vtp')

def importPolygon(suffix, filename, options=None):
    if suffix not in supported_suffixes:
        raise ValueError('Unsupported suffix {}'.format(suffix))
    
    print('#########')
    print suffix
    print filename
    print('#########')
    r = Reader()
    if suffix=='auto':
        r.read(filename)
    if suffix == 'obj':
        r.readOBJ(filename)
    elif suffix=='wrl':
        r.readVRML(filename)
    elif suffix=='stl':
        r.readSTL(filename)
    elif suffix=='ply':
        r.readPLY(filename)
    elif suffix=='vtp':
        r.readVTP(filename)

    print r._points.shape
    print r._triangles.shape

    return r._points, r._triangles
