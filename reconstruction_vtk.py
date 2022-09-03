#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtk.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtk.vtkRenderingOpenGL2

from vtk import vtkTransform

from vtk.vtkCommonColor import vtkNamedColors

from vtk.vtkCommonDataModel import vtkImageData
from vtk.vtkFiltersCore import (
    vtkFlyingEdges3D,
    vtkMarchingCubes
)

from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints, vtkUnsignedCharArray

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData
)
from vtk.vtkFiltersSources import vtkSphereSource
from vtk.vtkIOImage import vtkDICOMImageReader
from vtk.vtkImagingHybrid import vtkVoxelModeller
from vtk.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkRenderingCore import vtkProp3D


colors = vtkNamedColors()


def calculate_dicom_coordinates(reader: vtkDICOMImageReader):
    transform = vtkTransform()
    transform.RotateWXYZ(180, 1.0, 1.0, 0)
    # rotation.SetInputConnection(reader.GetOutputPort())

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetTransform(transform)
    transformFilter.SetInputConnection(reader.GetOutputPort())
    transformFilter.Update()


def get_landmarks_actors():
    colors = vtkNamedColors()

    # Create a sphere
    sphereSource = vtkSphereSource()
    sphereSource.SetCenter(50, 100, 300)
    sphereSource.SetRadius(5)

    # Make the surface smooth.
    sphereSource.SetPhiResolution(100)
    sphereSource.SetThetaResolution(100)

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('Tomato'))
    actor.GetProperty().SetPointSize(20)

    return actor


def get_skull_surface():
    can_use_flying_edges = vtk_version_ok(8, 2, 0)

    if can_use_flying_edges:
        try:
            surface = vtkFlyingEdges3D()
        except AttributeError:
            surface = vtkMarchingCubes()
    else:
        surface = vtkMarchingCubes()

    return surface


def get_skull_actor(iso_value, dicom_dir):
    volume = vtkImageData()

    # reader
    reader = vtkDICOMImageReader()
    reader.SetDirectoryName(dicom_dir)
    reader.Update()
    volume.DeepCopy(reader.GetOutput())

    # surface
    surface = get_skull_surface()
    surface.SetInputData(volume)
    surface.ComputeNormalsOn()
    surface.SetValue(0, iso_value)

    # flip transformation
    transform = vtkTransform()
    transform.RotateWXYZ(180, 1.0, 1.0, 0)
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetTransform(transform)
    transformFilter.SetInputConnection(surface.GetOutputPort())
    transformFilter.Update()

    # mapper
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(transformFilter.GetOutputPort())
    mapper.ScalarVisibilityOff()

    # actor
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('Green'))

    return actor


def main(dicom_dir, iso_value):
    if iso_value is None and dicom_dir is not None:
        print('An ISO value is needed.')
        return

    renderer = vtkRenderer()
    renderer.SetBackground(colors.GetColor3d('Black'))

    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetWindowName('Cranial Reconstruction: ' + dicom_dir)
    render_window.SetSize(1500, 800)

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    renderer.AddActor(get_skull_actor(iso_value, dicom_dir))
    renderer.AddActor(get_landmarks_actors())

    renderer.ResetCamera()

    render_window.Render()
    interactor.Start()


def vtk_version_ok(major, minor, build):
    """
    Check the VTK version.

    :param major: Major version.
    :param minor: Minor version.
    :param build: Build version.
    :return: True if the requested VTK version is greater or equal to the actual VTK version.
    """
    needed_version = 10000000000 * int(major) + 100000000 * int(minor) + int(build)

    vtk_version_number = 10000000000 * vtk.VTK_MAJOR_VERSION + 100000000 * vtk.VTK_MINOR_VERSION \
                         + vtk.VTK_BUILD_VERSION

    return vtk_version_number >= needed_version