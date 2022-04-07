# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 11:20:25 2020

@author: Eduardo Angulo
@author: Camila Lozano
"""

# Imports

import os
import vtk

from os.path import isfile, join


# Get Program Parameters
def get_program_parameters():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('folder_path', nargs='?', 
	                    default=None, help='data folder path')
	parser.add_argument('--oval', dest='o_value', type=float, 
	                    default=None, help='ocean initial isovalue')
	parser.add_argument('--aval', dest='a_value', type=float, 
	                    default=None, help='asteroid initial isovalue')
	parser.add_argument('--otrans', dest='o_trans', type=float,
						default=None, help='ocean initial transparency')
	parser.add_argument('--atrans', dest='a_trans', type=float,
						default=None, help='asteroid initial transparency')
	parser.add_argument('--itime', dest='time_index', type=int,
						default=None, help='initial time index')
	args = parser.parse_args()
	return args.folder_path, args.o_value, args.a_value, args.o_trans, args.a_trans, args.time_index


"""
- UI Methods
"""

# Convert Hex Color to RGB
def convertHex2RGB(hex_col):
	h = hex_col.lstrip('#')
	rgb = list(int(h[i:i+2], 16) for i in (0, 2, 4))
	rgb = list(map(lambda x: x / 255.0, rgb))
	return rgb


# Generate Ocean Color Transfer Function
def generateOceanCTF():
	colorList = [
		'#9898ff',
		'#8484ff',
		'#6f6fff',
		'#5a5aff',
		'#4646ff',
		'#3232ff',
		'#2d2de5',
		'#2828cc',
		'#2323b2',
		'#1e1e99',
		'#19197f'
	]
	colorFunction = vtk.vtkColorTransferFunction()
	i = 0
	for color in colorList:
		rgb = convertHex2RGB(color)
		colorFunction.AddRGBPoint(i, rgb[0], rgb[1], rgb[2])
		i = i + 0.1
	return colorFunction


# Generate Asteroid Color Transfer Function
def generateAsteroidCTF():
	colorList = [
		'#b2a190',
		'#a28e79',
		'#937b63',
		'#83684d',
		'#745537',
		'#654321',
		'#5a3c1d',
		'#50351a',
		'#462e17',
		'#3c2813',
		'#322110'
	]
	colorFunction = vtk.vtkColorTransferFunction()
	i = 0
	for color in colorList:
		rgb = convertHex2RGB(color)
		colorFunction.AddRGBPoint(i, rgb[0], rgb[1], rgb[2])
		i = i + 0.1
	return colorFunction


# Create Slide Bar Method
def createSlideBar(min_, max_, val, x1, x2, y, name):
	slideBar = vtk.vtkSliderRepresentation2D()
	slideBar.SetMinimumValue(min_)
	slideBar.SetMaximumValue(max_)
	slideBar.SetValue(val)
	slideBar.SetTitleText(name)
	slideBar.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
	slideBar.GetPoint1Coordinate().SetValue(x1, y)
	slideBar.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
	slideBar.GetPoint2Coordinate().SetValue(x2, y)
	slideBar.SetTitleHeight(0.025)
	slideBar.SetLabelHeight(0.02)
	return slideBar


# Create Slider Widget Method
def createSliderWidget(slideBar, interactor):
	sliderWidget = vtk.vtkSliderWidget()
	sliderWidget.SetInteractor(interactor)
	sliderWidget.SetRepresentation(slideBar)
	sliderWidget.SetAnimationModeToAnimate()
	sliderWidget.SetEnabled(True)
	return sliderWidget


# Create Scalar Bar Method
def createScalarBar(mapper, title, labels, x, y):
	scalarBar = vtk.vtkScalarBarActor()
	scalarBar.SetOrientationToHorizontal()
	scalarBar.UnconstrainedFontSizeOff()
	scalarBar.SetLookupTable(mapper.GetLookupTable())
	scalarBar.SetTitle(title)
	scalarBar.SetNumberOfLabels(labels)
	scalarBar.SetLabelFormat("%.2f")
	scalarBar.SetPosition(x, y)
	scalarBar.SetWidth(0.5)
	scalarBar.SetHeight(0.1)
	return scalarBar


"""
- Callback Methods
"""

# Ocean Isovalue Slide Bar Callback Method
def vtkOceanIsovalueSlideBarCallback(obj, event):
	global o_contours
	slideBar = obj.GetRepresentation()
	value = slideBar.GetValue()
	o_contours.SetValue(0, value)


# Ocean Opacity Slide Bar Callback Method
def vtkOceanOpacitySlideBarCallback(obj, event):
	global o_actor
	slideBar = obj.GetRepresentation()
	value = slideBar.GetValue()
	o_actor.GetProperty().SetOpacity(value)


# Asteroid Isovalue Slide Bar Callback Method
def vtkAsteroidIsovalueSlideBarCallback(obj, event):
	global a_contours
	slideBar = obj.GetRepresentation()
	value = slideBar.GetValue()
	a_contours.SetValue(0, value)


# Asteroid Opacity Slide Bar Callback Method
def vtkAsteroidOpacitySlideBarCallback(obj, event):
	global a_actor
	slideBar = obj.GetRepresentation()
	value = slideBar.GetValue()
	a_actor.GetProperty().SetOpacity(value)


# Time Value Slider Bar Callback Method
def vtkTimeSlideBarCallback(obj, event):
	global o_reader, a_reader, folder_path, data_files
	slideBar = obj.GetRepresentation()
	value = round(slideBar.GetValue())

	o_reader.SetFileName(join(folder_path, data_files[value]))
	o_reader.Update()
	o_reader.GetOutput().GetPointData().SetActiveScalars('v02')
	o_reader.Update()

	a_reader.SetFileName(join(folder_path, data_files[value]))
	a_reader.Update()
	a_reader.GetOutput().GetPointData().SetActiveScalars('v03')
	a_reader.Update()


"""
- Main Method
"""

def main():
	global o_reader, a_reader, folder_path, data_files, o_contours, o_actor, a_contours, a_actor

	folder_path, o_value, a_value, o_trans, a_trans, time_index = get_program_parameters()

	# List all Files in Folder
	data_files = [f for f in os.listdir(folder_path) if isfile(join(folder_path, f))]
	data_files.sort()

	# Get and Set Time Index
	if time_index is None:
		time_index = 0
	elif not (0 <= time_index < len(data_files)):
		time_index = 0

	# Load Ocean Data
	o_reader = vtk.vtkXMLImageDataReader()
	o_reader.SetFileName(join(folder_path, data_files[time_index]))
	o_reader.Update()
	o_reader.GetOutput().GetPointData().SetActiveScalars('v02')
	o_reader.Update()

	# Load Asteroid Data
	a_reader = vtk.vtkXMLImageDataReader()
	a_reader.SetFileName(join(folder_path, data_files[time_index]))
	a_reader.Update()
	a_reader.GetOutput().GetPointData().SetActiveScalars('v03')
	a_reader.Update()

	# Get Ocean Scalar Range
	o_range = o_reader.GetOutput().GetScalarRange()
	o_min_val = o_range[0]
	o_max_val = o_range[1]
	o_mid_val = (o_min_val + o_max_val) / 2

	# Get Asteroid Scalar Range
	a_range = a_reader.GetOutput().GetScalarRange()
	a_min_val = a_range[0]
	a_max_val = a_range[1]
	a_mid_val = (a_min_val + a_max_val) / 2

	# Get Initial Contour Value
	if o_value is None:
		o_value = o_mid_val
	elif not (o_min_val <= o_value <= o_max_val):
		o_value = o_mid_val

	if a_value is None:
		a_value = a_mid_val
	elif not (a_min_val <= a_value <= a_max_val):
		a_value = a_mid_val

	# Get Initial Opacity Value
	if o_trans is None:
		o_trans = 1
	elif not (0 <= o_trans <= 1):
		o_trans = 1

	if a_trans is None:
		a_trans = 1
	elif not (0 <= a_trans <= 1):
		a_trans = 1

	# Generate Contours for Ocean
	o_contours = vtk.vtkContourFilter()
	o_contours.SetInputConnection(o_reader.GetOutputPort());
	o_contours.ComputeNormalsOn()
	o_contours.ComputeScalarsOn()
	o_contours.GenerateTrianglesOn()
	o_contours.CreateDefaultLocator()
	o_contours.SetValue(0, o_value)

	# Generate Contours for Asteroid
	a_contours = vtk.vtkContourFilter()
	a_contours.SetInputConnection(a_reader.GetOutputPort());
	a_contours.ComputeNormalsOn()
	a_contours.ComputeScalarsOn()
	a_contours.GenerateTrianglesOn()
	a_contours.CreateDefaultLocator()
	a_contours.SetValue(0, a_value)

	# Create Ocean CTF, Mapper and Actor
	o_ctf = generateOceanCTF()

	o_mapper = vtk.vtkDataSetMapper()
	o_mapper.SetInputConnection(o_contours.GetOutputPort())
	o_mapper.SetLookupTable(o_ctf)

	o_actor = vtk.vtkActor()
	o_actor.SetMapper(o_mapper)
	o_actor.GetProperty().SetOpacity(o_trans)

	# Create Asteroid CTF, Mapper and Actor
	a_ctf = generateAsteroidCTF()

	a_mapper = vtk.vtkDataSetMapper()
	a_mapper.SetInputConnection(a_contours.GetOutputPort())
	a_mapper.SetLookupTable(a_ctf)

	a_actor = vtk.vtkActor()
	a_actor.SetMapper(a_mapper)
	a_actor.GetProperty().SetOpacity(a_trans)

	# Create Renderer, Render Window and Render Window Interactor
	ren = vtk.vtkRenderer()
	renWin = vtk.vtkRenderWindow()
	renWin.AddRenderer(ren)
	iren = vtk.vtkRenderWindowInteractor()
	iren.SetRenderWindow(renWin)

	# Add Ocean and Asteroid Actors
	ren.AddActor(o_actor)
	ren.AddActor(a_actor)

	# Depth Peeling
	ren.SetUseDepthPeeling(1)
	ren.SetMaximumNumberOfPeels(100)
	ren.SetOcclusionRatio(0.1)
	renWin.SetAlphaBitPlanes(1)
	renWin.SetMultiSamples(0)

	# Set Renderer Properties
	ren.ResetCamera()
	ren.GetActiveCamera().Zoom(1.0)
	back_rgb = convertHex2RGB('#51576e')
	ren.SetBackground(back_rgb[0], back_rgb[1], back_rgb[2])
	ren.ResetCameraClippingRange()

	renWin.SetSize(1000, 600)

	# Ocean Isovalue Slider Bar
	oceanIsovalueSlideBar = createSlideBar(o_min_val, o_max_val, o_value, 
	                                  		0.05, 0.20, 0.1, "Ocean Isovalue")
	oceanIsovalueSliderWidget = createSliderWidget(oceanIsovalueSlideBar, iren)
	oceanIsovalueSliderWidget.AddObserver("InteractionEvent", 
	                                 		vtkOceanIsovalueSlideBarCallback)

	# Ocean Opacity Slider Bar
	oceanOpacitySlideBar = createSlideBar(0, 1, o_trans, 0.05, 0.20, 0.25, "Ocean Opacity")
	oceanOpacitySliderWidget = createSliderWidget(oceanOpacitySlideBar, iren)
	oceanOpacitySliderWidget.AddObserver("InteractionEvent", 
	                                 		vtkOceanOpacitySlideBarCallback)

	# Asteroid Isovalue Slider Bar
	asteroidIsovalueSlideBar = createSlideBar(a_min_val, a_max_val, a_value, 
	                                  		0.80, 0.95, 0.1, "Asteroid Isovalue")
	asteroidIsovalueSliderWidget = createSliderWidget(asteroidIsovalueSlideBar, iren)
	asteroidIsovalueSliderWidget.AddObserver("InteractionEvent", 
	                                 		vtkAsteroidIsovalueSlideBarCallback)

	# Asteroid Opacity Slider Bar
	asteroidOpacitySlideBar = createSlideBar(0, 1, a_trans, 0.80, 0.95, 0.25, "Asteroid Opacity")
	asteroidOpacitySliderWidget = createSliderWidget(asteroidOpacitySlideBar, iren)
	asteroidOpacitySliderWidget.AddObserver("InteractionEvent", 
	                                 		vtkAsteroidOpacitySlideBarCallback)

	# Time Index Slide Bar
	timeSlideBar = createSlideBar(0, len(data_files) - 1, time_index, 0.25, 0.75, 0.9, "Time")
	timeSliderWidget = createSliderWidget(timeSlideBar, iren)
	timeSliderWidget.AddObserver("InteractionEvent", vtkTimeSlideBarCallback)

	# Ocean and Asteroid Isovalue Scalar Bar
	oceanScalarBar = createScalarBar(o_mapper, "Ocean Isovalue", 6, 0.25, 0.15)
	asteroidScalarBar = createScalarBar(a_mapper, "Asteroid Isovalue", 6, 0.25, 0.03)

	ren.AddActor2D(oceanScalarBar)
	ren.AddActor2D(asteroidScalarBar)

	# Initialize Render
	iren.Initialize()
	renWin.Render()
	iren.Start()


if __name__ == '__main__':
	main()