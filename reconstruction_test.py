import vtk

from vtk.vtkCommonColor import vtkNamedColors
from vtk.vtkCommonDataModel import vtkImageData
from vtk.vtkFiltersCore import vtkFlyingEdges3D, vtkMarchingCubes
from vtk.vtkFiltersSources import vtkSphereSource
from vtk.vtkRenderingCore import (vtkActor, vtkPolyDataMapper, vtkRenderer,
                                  vtkRenderWindow, vtkRenderWindowInteractor)
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingCore import (vtkActor, vtkPolyDataMapper,
                                         vtkRenderer, vtkRenderWindow,
                                         vtkRenderWindowInteractor)

import json

colors = vtkNamedColors()


def load_landmarks_in_ras_coordinates() -> vtk.vtkPoints:
    points = vtk.vtkPoints()

    with open('landmarks.json', 'r') as json_file:
        data = json.load(json_file)
        lps_landmarks = [landmark['position'] for landmark in data['markups'][0]['controlPoints']]

        print(lps_landmarks)
        for lps_landmark in lps_landmarks:
            ras_landmark = [-lps_landmark[0], -lps_landmark[1], lps_landmark[2]]
            points.InsertNextPoint(ras_landmark)

    return points


def point_to_glyph(points):
    bounds = points.GetBounds()
    max_len = 0
    for i in range(1, 3):
        max_len = max(bounds[i + 1] - bounds[i], max_len)

    sphere_source = vtkSphereSource()
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


def get_landmarks_actor() -> vtkActor:
    ras_landmarks = load_landmarks_in_ras_coordinates()

    # transform
    landmark_transform = vtk.vtkLandmarkTransform()
    landmark_transform.SetSourceLandmarks(ras_landmarks)

    # polydata
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(ras_landmarks)

    # filter
    glyph_filter = vtk.vtkVertexGlyphFilter()
    glyph_filter.SetInputData(polydata)
    glyph_filter.Update()

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputConnection(glyph_filter.GetOutputPort())
    transform_filter.SetTransform(landmark_transform)
    transform_filter.Update()

    # actor
    actor = point_to_glyph(glyph_filter.GetOutput().GetPoints())
    actor.GetProperty().SetColor(colors.GetColor3d("tomato"))

    return actor


def get_skull_actor(nifti_file: str, iso_value: float):
    # reader
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(nifti_file)
    reader.Update()

    # volume
    volume = vtkImageData()
    volume.DeepCopy(reader.GetOutput())

    # surface
    surface = vtkFlyingEdges3D()
    surface.SetInputData(volume)
    surface.ComputeNormalsOn()
    surface.SetValue(0, iso_value)

    # transformations
    coordinates_transform = vtk.vtkTransform()
    coordinates_transform.SetMatrix(reader.GetQFormMatrix())

    transform_filter = vtk.vtkTransformFilter()
    transform_filter.SetTransform(coordinates_transform)
    transform_filter.SetInputConnection(surface.GetOutputPort())
    transform_filter.Update()

    # mapper
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(transform_filter.GetOutputPort())
    mapper.ScalarVisibilityOff()

    # actor
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(1)
    actor.GetProperty().SetColor(colors.GetColor3d('Green'))

    return actor


def render_skull(nifti_file: str, iso_value: float):
    print("Rendering...")

    if iso_value is None or nifti_file in [None, ""]:
        print('An ISO value and a nifti file are needed.')
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
    renderer.AddActor(get_skull_actor(nifti_file, iso_value))
    renderer.AddActor(get_landmarks_actor())

    renderer.ResetCamera()

    render_window.Render()
    interactor.Start()


if __name__ == "__main__":
    render_skull(nifti_file="cts.nii.gz", iso_value=100)
