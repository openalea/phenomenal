# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================

import vtk
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy


class Mesh:
    """Mesh interface based on vtkPolyData"""

    def __init__(self, poly_data=None):
        self.poly_data = poly_data or vtk.vtkPolyData()

    def __getattr__(self, name):
        return getattr(self.poly_data, name)

    @property
    def vertices(self):
        points = self.GetPoints()
        if points is None:
            return np.empty((0, 3))

        return vtk_to_numpy(points.GetData())

    @property
    def faces(self):
        polys = self.GetPolys()
        if polys is None or polys.GetNumberOfCells() == 0:
            return np.empty((0, 0), dtype=int)
        connectivity = vtk_to_numpy(polys.GetConnectivityArray())
        return connectivity.reshape(-1, 3)

    @property
    def colors(self):
        data = self.GetPointData().GetScalars()
        if data is None:
            return np.empty((0, 3))

        return vtk_to_numpy(data)


    @property
    def vids(self):
        data = self.GetPointData().GetArray("Vids")
        if data is None:
            return np.empty((0, 0))

        return vtk_to_numpy(data)

    @staticmethod
    def from_pymesh(vertices, faces, colors=None, vids=None):
        """Instantiate a Mesh from vertices, triangular faces, colors and vids.

        Parameters
        ----------
        vertices : array-like, shape (N, 3)
            Vertex coordinates. Accepts a NumPy array or a sequence of
            three-dimensional coordinate sequences.

        faces : array-like, shape (M, 3)
            Triangle connectivity. Each row contains three indices into
            `vertices`. Accepts a NumPy array or a sequence of index sequences.

        vertex_colors : array-like, shape (N, 3), optional
            RGB color values for each vertex, with integer components in
            the range [0, 255].

        vids : array-like, shape (N, 1), optional
            Identifier for vertices.

        Returns
        -------
        Mesh
            A polygonal mesh containing the vertices, triangular faces,
            and optional point and cell RGB colors.
        """

        poly_data = vtk.vtkPolyData()

        # vertices
        vertices = np.ascontiguousarray(vertices, dtype=np.float64)
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(vertices, deep=True))
        poly_data.SetPoints(points)

        # faces
        faces = np.asarray(faces, dtype=np.int64)
        offsets = np.arange(0, 3 * len(faces) + 1, 3, dtype=np.int64)
        connectivity = np.ascontiguousarray(faces.ravel(), dtype=np.int64)
        polys = vtk.vtkCellArray()
        polys.SetData(
            numpy_to_vtkIdTypeArray(offsets, deep=True),
            numpy_to_vtkIdTypeArray(connectivity, deep=True),
        )
        poly_data.SetPolys(polys)

        if colors is not None:
            colors = np.ascontiguousarray(colors, dtype=np.uint8)
            vtk_colors = numpy_to_vtk(colors, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
            vtk_colors.SetNumberOfComponents(3)
            vtk_colors.SetName("Colors")
            poly_data.GetPointData().SetScalars(vtk_colors)

        if vids is not None:
            vtk_vids = numpy_to_vtk(np.ascontiguousarray(vids), deep=True)
            vtk_vids.SetName("Vids")
            poly_data.GetPointData().AddArray(vtk_vids)

        return Mesh(poly_data)

    def write_ply(self, filename) -> None:
        """
        Write a vtk to ply file.

        Parameters
        ----------
        filename: str
            The name of the file to write to.
        """
        ply_writer = vtk.vtkPLYWriter()
        ply_writer.SetFileTypeToASCII()
        ply_writer.SetFileName(filename)
        ply_writer.SetInputData(self.poly_data)
        ply_writer.Write()

    @staticmethod
    def from_ply(filename):
        """
        Instantiate from a ply file.

        Parameters
        ----------
        filename: str
            The name of the file to read.
        Returns
        -------
        Mesh
        """
        ply_reader = vtk.vtkPLYReader()
        ply_reader.SetFileName(filename)
        ply_reader.Update()
        poly_data = ply_reader.GetOutput()

        return Mesh(poly_data)
