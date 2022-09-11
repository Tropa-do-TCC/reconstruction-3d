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
import json
import vtk

colors = vtkNamedColors()

def get_cloud_points_center(pointsArray: list):
    x = y = z = 0
    arraySize = len(pointsArray)
    for i in range(len(pointsArray)):
        x += pointsArray[i][0]
        y += pointsArray[i][1]
        z += pointsArray[i][2]
    x = x / arraySize
    y = y / arraySize
    z = z / arraySize
    return x, y, z

def get_landmarks_actors(renderer, skull_center):
    pointsPosition = []
    with open('landmarks.json', 'r') as json_file:
        data = json.load(json_file)
        landmarks = data['markups'][0]['controlPoints']
        for i in range(len(landmarks)):
            landmark = landmarks[i]['position']
            pointsPosition.append([landmark[0], landmark[1], landmark[2]])

        x_cloud_center, y_cloud_center, z_cloud_center = get_cloud_points_center(pointsPosition)
        x_distance = skull_center[0] - x_cloud_center
        y_distance = skull_center[1] - y_cloud_center
        z_distance = skull_center[2] - z_cloud_center

        for landmark in range(len(pointsPosition)):
            new_x = pointsPosition[landmark][0] + x_distance
            new_y = pointsPosition[landmark][1] + y_distance
            new_z = pointsPosition[landmark][2] + z_distance

            # Create a sphere
            sphere_source = vtkSphereSource()
            print(f"X: {new_x} Y: {new_y} Z: {new_z}")

            sphere_source.SetCenter(new_x, new_y, new_z)
            #sphere_source.SetCenter(pointsPosition[landmark][0], pointsPosition[landmark][1], pointsPosition[landmark][2])
            sphere_source.SetRadius(3)

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

            renderer.AddActor(actor)

def get_skull_actor(dicom_dir: str, iso_value: float):
    volume = vtkImageData()

    # reader
    reader = vtkDICOMImageReader()
    reader.SetDirectoryName(dicom_dir)
    reader.Update()
    volume.DeepCopy(reader.GetOutput())

    print(f"Dimesao: {volume.GetDimensions()}")

    # surface
    # surface = vtkMarchingCubes()
    surface = vtkFlyingEdges3D()
    surface.SetInputData(volume)
    surface.ComputeNormalsOn()
    surface.SetValue(0, iso_value)

    centerOfMassFilter = vtk.vtkCenterOfMass()
    centerOfMassFilter.SetInputData(volume)
    centerOfMassFilter.SetUseScalarsAsWeights(False)
    centerOfMassFilter.Update()

    center = centerOfMassFilter.GetCenter()
    print(f"Cneter of Mass x: {center[0]} Y: {center[1]} Z: {center[2]}")

    # flip transformation
    flip_x = 120.02629017829895
    flip_y = -113.34333801269531
    flip_z = -84.0

    transform = vtk.vtkTransform()
    transform.PostMultiply()
    transform.Translate(-flip_x, -flip_y, -flip_z)
    transform.RotateX(180)
    transform.RotateZ(180)
    transform.Translate(+flip_x, +flip_y, +flip_z)
    #transform.Scale(1, 1,1)
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetTransform(transform)
    transformFilter.SetInputConnection(surface.GetOutputPort())
    transformFilter.Update()

    # mapper
    mapper = vtkPolyDataMapper()
    #mapper.SetInputConnection(surface.GetOutputPort())
    mapper.SetInputConnection(transformFilter.GetOutputPort())
    mapper.ScalarVisibilityOff()

    # actor
    actor = vtkActor()
    actor.SetMapper(mapper)
    center_x, center_y, center_z = actor.GetCenter()
    #actor.RotateX(180)
    actor.GetProperty().SetOpacity(0.3)
    actor.GetProperty().SetColor(colors.GetColor3d('Green'))

    print(f"Cranio X: {center_x} Y: {center_y} Z: {center_z}")

    return actor, [center_x, center_y, center_z]


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
    skull_render, skull_center = get_skull_actor(dicom_dir, iso_value)
    renderer.AddActor(skull_render)
    get_landmarks_actors(renderer, skull_center)

    renderer.ResetCamera()

    render_window.Render()
    interactor.Start()

if __name__ == "__main__":
    dicom_dir = "ct_images"

    decompress_slices(dicom_dir)
    render_skull(dicom_dir, iso_value=100)
