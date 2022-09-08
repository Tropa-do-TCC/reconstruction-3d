#!/usr/bin/env python

# noinspection PyUnresolvedReferences
from vtk.vtkCommonColor import vtkNamedColors
from vtk.vtkCommonDataModel import vtkImageData
from vtk.vtkFiltersCore import vtkFlyingEdges3D
from vtk.vtkFiltersSources import vtkSphereSource
from vtk.vtkIOImage import vtkDICOMImageReader
from vtk.vtkRenderingCore import (vtkActor, vtkPolyDataMapper, vtkRenderer,
                                  vtkRenderWindow, vtkRenderWindowInteractor)
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingCore import (vtkActor, vtkPolyDataMapper,
                                         vtkRenderer, vtkRenderWindow,
                                         vtkRenderWindowInteractor)

from dcm_decompress import decompress_slices

colors = vtkNamedColors()


def get_landmarks_actors():
    # Create a sphere
    sphere_source = vtkSphereSource()
    sphere_source.SetCenter(252, 88, 5)
    sphere_source.SetRadius(5)

    # Make the surface smooth.
    sphere_source.SetPhiResolution(100)
    sphere_source.SetThetaResolution(100)

    # mapper
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(sphere_source.GetOutputPort())

    # actor
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('Tomato'))
    actor.GetProperty().SetPointSize(20)

    return actor


def get_skull_actor(dicom_dir: str, iso_value: float):
    volume = vtkImageData()

    # reader
    reader = vtkDICOMImageReader()
    reader.SetDirectoryName(dicom_dir)
    reader.Update()
    volume.DeepCopy(reader.GetOutput())

    # surface
    # surface = vtkMarchingCubes()
    surface = vtkFlyingEdges3D()
    surface.SetInputData(volume)
    surface.ComputeNormalsOn()
    surface.SetValue(0, iso_value)

    # mapper
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(surface.GetOutputPort())
    mapper.ScalarVisibilityOff()

    # actor
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('Green'))

    return actor


def render_skull(dicom_dir: str, iso_value: float):
    print("Rendering...")

    if iso_value is None or dicom_dir in [None, ""]:
        print('An ISO value and a DICOMDIR are needed.')
        return

    # renderer
    renderer = vtkRenderer()
    renderer.SetBackground(colors.GetColor3d('Black'))

    # render window
    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetWindowName('Skull Reconstruction')
    render_window.SetSize(1500, 800)

    # interactor
    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # actors
    renderer.AddActor(get_skull_actor(dicom_dir, iso_value))
    renderer.AddActor(get_landmarks_actors())

    renderer.ResetCamera()

    render_window.Render()
    interactor.Start()

if __name__ == "__main__":
    dicom_dir = "dicom_dir"

    decompress_slices(dicom_dir)
    render_skull(dicom_dir, iso_value=100)
