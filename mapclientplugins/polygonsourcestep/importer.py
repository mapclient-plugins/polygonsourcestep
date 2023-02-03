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


class Reader(object):
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

    def set_filename(self, filename):
        self.filename = filename

    def get_points(self):
        return self._points

    def get_triangles(self):
        return self._triangles

    def read(self, filename=None):
        if filename is not None:
            self.filename = filename

        filePrefix, fileExt = path.splitext(self.filename)
        fileExt = fileExt.lower()
        if fileExt == '.obj':
            self.read_obj()
        elif fileExt == '.wrl':
            self.read_vrml()
        elif fileExt == '.stl':
            self.read_stl()
        elif fileExt == '.ply':
            self.read_ply()
        elif fileExt == '.vtp':
            self.read_vtp()
        else:
            print('failed to open {}'.format(self.filename))
            raise ValueError('unknown file extension')

    def read_vrml(self, filename=None):
        if filename is not None:
            self.filename = filename
        r = vtk.vtkVRMLImporter()
        r.SetFileName(self.filename)
        r.Update()
        actors = r.GetRenderer().GetActors()
        actors.InitTraversal()
        self.polydata = actors.GetNextActor().GetMapper().GetInput()

        if self.polydata.GetPoints() is None:
            raise IOError('file not loaded')
        else:
            self._load_points()
            self._load_triangles()

    def read_obj(self, filename=None):
        if filename is not None:
            self.filename = filename

        r = vtk.vtkOBJReader()
        r.SetFileName(self.filename)
        r.Update()
        self.polydata = r.GetOutput()

        if self.polydata.GetPoints() is None:
            raise IOError('file not loaded')
        else:
            self._load_points()
            self._load_triangles()

    def read_ply(self, filename=None):
        if filename is not None:
            self.filename = filename

        r = vtk.vtkPLYReader()
        r.SetFileName(self.filename)
        r.Update()
        self.polydata = r.GetOutput()

        if self.polydata.GetPoints() is None:
            raise IOError('file not loaded')
        else:
            self._load_points()
            self._load_triangles()

    def read_stl(self, filename=None):
        if filename is not None:
            self.filename = filename

        r = vtk.vtkSTLReader()
        r.SetFileName(self.filename)
        r.Update()
        self.polydata = r.GetOutput()

        if self.polydata.GetPoints() is None:
            raise IOError('file not loaded')
        else:
            self._load_points()
            self._load_triangles()

    def read_vtp(self, filename=None):
        if filename is not None:
            self.filename = filename

        if self._is_xml(self.filename):
            r = vtk.vtkXMLPolyDataReader()
        else:
            r = vtk.vtkPolyDataReader()
        r.SetFileName(self.filename)
        r.Update()
        self.polydata = r.GetOutput()

        if self.polydata.GetPoints() is None:
            raise IOError('file not loaded')
        else:
            self._load_points()
            self._load_triangles()

    @staticmethod
    def _is_xml(f):
        """Check if file is an xml file
        """
        with open(f, 'r') as fp:
            line = fp.readline()

        if line[0] == '<':
            return True
        else:
            return False

    def _load_points(self):
        P = self.polydata.GetPoints().GetData()
        self._dimensions = P.GetNumberOfComponents()
        self._nPoints = P.GetNumberOfTuples()

        if self._dimensions == 1:
            self._points = array([P.GetTuple1(i) for i in range(self._nPoints)])
        elif self._dimensions == 2:
            self._points = array([P.GetTuple2(i) for i in range(self._nPoints)])
        elif self._dimensions == 3:
            self._points = array([P.GetTuple3(i) for i in range(self._nPoints)])
        elif self._dimensions == 4:
            self._points = array([P.GetTuple4(i) for i in range(self._nPoints)])
        elif self._dimensions == 9:
            self._points = array([P.GetTuple9(i) for i in range(self._nPoints)])

    def _load_triangles(self):
        polyData = self.polydata.GetPolys().GetData()
        X = [int(polyData.GetTuple1(i)) for i in range(polyData.GetNumberOfTuples())]

        # assumes that faces are triangular
        X = array(X).reshape((-1, 4))
        self._nFaces = X.shape[0]
        self._triangles = X[:, 1:]


supported_suffixes = ('auto', 'stl', 'wrl', 'obj', 'ply', 'vtp')


def import_polygon(suffix, filename):
    if suffix not in supported_suffixes:
        raise ValueError('Unsupported suffix {}'.format(suffix))

    r = Reader()
    if suffix == 'auto':
        r.read(filename)
    if suffix == 'obj':
        r.read_obj(filename)
    elif suffix == 'wrl':
        r.read_vrml(filename)
    elif suffix == 'stl':
        r.read_stl(filename)
    elif suffix == 'ply':
        r.read_ply(filename)
    elif suffix == 'vtp':
        r.read_vtp(filename)

    return r.get_points(), r.get_triangles()
