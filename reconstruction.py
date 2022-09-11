#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtk
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

colors = vtk.vtkNamedColors()


def PointToGlyph(points, scale):
    bounds = points.GetBounds()
    maxLen = 0
    for i in range(1, 3):
        maxLen = max(bounds[i + 1] - bounds[i], maxLen)

    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetRadius(scale * maxLen)

    pd = vtk.vtkPolyData()
    pd.SetPoints(points)

    mapper = vtk.vtkGlyph3DMapper()
    mapper.SetInputData(pd)
    mapper.SetSourceConnection(sphereSource.GetOutputPort())
    mapper.ScalarVisibilityOff()
    mapper.ScalingOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor


def get_landmarks_actors(array_points=[], color=""):
    sourcePoints = vtk.vtkPoints()
    for point in array_points:
        sourcePoints.InsertNextPoint(float(point[0]), float(point[1]), float(point[2]))

    landmarkTransform = vtk.vtkLandmarkTransform()
    landmarkTransform.SetSourceLandmarks(sourcePoints)

    source = vtk.vtkPolyData()
    source.SetPoints(sourcePoints)

    sourceGlyphFilter = vtk.vtkVertexGlyphFilter()
    sourceGlyphFilter.SetInputData(source)
    sourceGlyphFilter.Update()

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(sourceGlyphFilter.GetOutputPort())
    transformFilter.SetTransform(landmarkTransform)
    transformFilter.Update()

    sourceActor = PointToGlyph(sourceGlyphFilter.GetOutput().GetPoints(), 0.03)
    sourceActor.GetProperty().SetColor(colors.GetColor3d(color))

    return sourceActor


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


def render_skull(dicom_dir: str,
                 iso_value: float,
                 original_landmarks=[],
                 predict_landmarks=[]):
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
    renderer.AddActor(get_landmarks_actors(original_landmarks, "tomato"))
    renderer.AddActor(get_landmarks_actors(predict_landmarks, "blue"))

    renderer.ResetCamera()

    render_window.Render()
    interactor.Start()


if __name__ == "__main__":
    dicom_dir = "dicom_dir"

    render_skull(dicom_dir, iso_value=100)


def reconstruct_with_landmarks(dcm_folder, original_landmarks, predict_landmarks):
    render_skull(dcm_folder,
                 iso_value=100,
                 original_landmarks=original_landmarks,
                 predict_landmarks=predict_landmarks)
