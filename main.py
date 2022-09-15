import vtk

from vtk.vtkCommonColor import vtkNamedColors
from vtk.vtkCommonDataModel import vtkImageData
from vtk.vtkFiltersCore import vtkFlyingEdges3D, vtkMarchingCubes
from vtk.vtkFiltersSources import vtkSphereSource
from vtk.vtkIOImage import vtkDICOMImageReader
from vtk.vtkRenderingCore import (vtkActor, vtkPolyDataMapper, vtkRenderer,
                                  vtkRenderWindow, vtkRenderWindowInteractor)
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingCore import (vtkActor, vtkPolyDataMapper,
                                         vtkRenderer, vtkRenderWindow,
                                         vtkRenderWindowInteractor)
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor

from dcm_decompress import decompress_slices

import json

colors = vtkNamedColors()


def point_to_glyph(points):
    bounds = points.GetBounds()
    max_len = 0
    for i in range(1, 3):
        max_len = max(bounds[i + 1] - bounds[i], max_len)

    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetRadius(2)

    # polydata
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    # mapper
    mapper = vtk.vtkGlyph3DMapper()
    mapper.SetInputData(polydata)
    mapper.SetSourceConnection(sphere_source.GetOutputPort())
    mapper.ScalarVisibilityOff()
    mapper.ScalingOff()

    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor

def translate_to_origin(actor: vtkActor) -> vtk.vtkTransform:
    center_of_mass = actor.GetCenter()
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    transform.Translate(-center_of_mass[0], -center_of_mass[1], -center_of_mass[2])

    return transform

def get_landmarks_actor() -> vtkActor:
    points = vtk.vtkPoints()

    with open('landmarks.json', 'r') as json_file:
        data = json.load(json_file)
        landmarks = [landmark['position'] for landmark in data['markups'][0]['controlPoints']]

        [points.InsertNextPoint(landmark) for landmark in landmarks]

    landmark_transform = vtk.vtkLandmarkTransform()
    landmark_transform.SetSourceLandmarks(points)

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    glyph_filter = vtk.vtkVertexGlyphFilter()
    glyph_filter.SetInputData(polydata)
    glyph_filter.Update()

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputConnection(glyph_filter.GetOutputPort())
    transform_filter.SetTransform(landmark_transform)
    transform_filter.Update()

    actor = point_to_glyph(glyph_filter.GetOutput().GetPoints())
    actor.GetProperty().SetColor(colors.GetColor3d("tomato"))

    origin_translation = translate_to_origin(actor)
    actor.SetUserTransform(origin_translation)

    return actor


def get_skull_actor(dicom_dir: str, iso_value: float) -> vtkActor:
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
    actor.GetProperty().SetOpacity(1)
    actor.GetProperty().SetColor(colors.GetColor3d('Green'))

    transform = translate_to_origin(actor)
    transform.RotateZ(180)
    transform.RotateX(90)

    actor.SetUserTransform(transform)

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
    renderer.AddActor(get_landmarks_actor())

    renderer.ResetCamera()

    render_window.Render()
    interactor.Start()

if __name__ == "__main__":
    dicom_dir = "dicomdir"
    decompress_slices(dicom_dir)

    render_skull(dicom_dir, iso_value=100)
