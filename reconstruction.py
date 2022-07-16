import vtk
# Define the rendering window 、 Interactive mode
aRender = vtk.vtkRenderer()
Renwin = vtk.vtkRenderWindow()
Renwin.AddRenderer(aRender)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(Renwin)
# Define a picture reading interface
# Read PNG Replace the picture with PNG_Reader = vtk.vtkPNGReader()
Jpg_Reader = vtk.vtkJPEGReader()
Jpg_Reader.SetNumberOfScalarComponents(1)
Jpg_Reader.SetFileDimensionality(3) # It shows that the image is three-dimensional
# Define image size , This line indicates that the image size is （512*512*240）
Jpg_Reader.SetDataExtent(0, 512, 0, 512, 0, 240)
# Set the storage location of the image
Jpg_Reader.SetFilePrefix("./ct_images_output/")
# Set image prefix name
# Indicates that the image prefix is a number （ Such as ：0.jpg）
Jpg_Reader.SetFilePattern("%sCT%06d.jpg")
Jpg_Reader.Update()
Jpg_Reader.SetDataByteOrderToLittleEndian()
# Method of calculating contour
contour = vtk.vtkMarchingCubes()
contour.SetInputConnection(Jpg_Reader.GetOutputPort())
contour.ComputeNormalsOn()
contour.SetValue(0, 100)
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(contour.GetOutputPort())
mapper.ScalarVisibilityOff()
actor = vtk.vtkActor()
actor.SetMapper(mapper)
renderer = vtk.vtkRenderer()
renderer.SetBackground([0.1, 0.1, 0.5])
renderer.AddActor(actor)
window = vtk.vtkRenderWindow()
window.SetSize(512, 512)
window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
# Start showing
window.Render()
interactor.Initialize()
interactor.Start()