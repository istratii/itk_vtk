import os

import itk
import numpy as np
import vtk

_IMAGE_FIXED_FILE_NAME = "case6_gre1.nrrd"
_IMAGE_MOVING_FILE_NAME = "case6_gre2.nrrd"
_DATA_DIR = "./Data"
_IMAGE_FIXED_PATH = os.path.join(_DATA_DIR, _IMAGE_FIXED_FILE_NAME)
_IMAGE_MOVING_PATH = os.path.join(_DATA_DIR, _IMAGE_MOVING_FILE_NAME)


def step2_images_alignment(fixed_image, moving_image):
    dimension = fixed_image.GetImageDimension()
    FixedImageType = type(fixed_image)
    MovingImageType = type(moving_image)

    TransformType = itk.TranslationTransform[itk.D, dimension]
    initialTransform = TransformType.New()

    optimizer = itk.RegularStepGradientDescentOptimizerv4.New()

    optimizer.SetLearningRate(4)
    optimizer.SetMinimumStepLength(0.001)
    optimizer.SetNumberOfIterations(200)

    metric = itk.MeanSquaresImageToImageMetricv4[FixedImageType, MovingImageType].New()
    fixed_interpolation = itk.LinearInterpolateImageFunction[
        FixedImageType, itk.D
    ].New()
    metric.SetFixedInterpolator(fixed_interpolation)

    registration = itk.ImageRegistrationMethodv4[FixedImageType, FixedImageType].New(
        FixedImage=fixed_image,
        MovingImage=moving_image,
        Metric=metric,
        Optimizer=optimizer,
        InitialTransform=initialTransform,
    )

    moving_initial_transform = TransformType.New()
    initial_parameters = moving_initial_transform.GetParameters()
    initial_parameters.Fill(0)
    moving_initial_transform.SetParameters(initial_parameters)
    registration.SetMovingInitialTransform(moving_initial_transform)

    identity_transform = TransformType.New()
    identity_transform.SetIdentity()
    registration.SetFixedInitialTransform(identity_transform)

    registration.SetNumberOfLevels(1)

    registration.Update()

    transform = registration.GetTransform()
    final_parameters = transform.GetParameters()
    translation = [final_parameters.GetElement(i) for i in range(dimension)]

    number_of_iterations = optimizer.GetCurrentIteration()

    best_value = optimizer.GetValue()

    print("Result = ")
    for i in range(dimension):
        print(f" Translation along axis {i} = {translation[i]}")
    print(" Iterations    = " + str(number_of_iterations))
    print(" Metric value  = " + str(best_value))

    CompositeTransformType = itk.CompositeTransform[itk.D, dimension]
    output_composite_transform = CompositeTransformType.New()
    output_composite_transform.AddTransform(moving_initial_transform)
    output_composite_transform.AddTransform(registration.GetModifiableTransform())

    resampler = itk.ResampleImageFilter.New(
        Input=moving_image,
        Transform=transform,
        UseReferenceImage=True,
        ReferenceImage=fixed_image,
    )
    resampler.SetDefaultPixelValue(100)
    resampler.Update()
    image_output = resampler.GetOutput()
    return image_output


def _segment_tumor(image, seed_points, intensity_range=0.1):
    res = np.zeros_like(itk.array_from_image(image))
    for seed_point in seed_points:
        seed_value = image.GetPixel(seed_point)
        lower_thresh = seed_value * (1 - intensity_range)
        upper_thresh = seed_value * (1 + intensity_range)
        connected_threshold_filter = itk.ConnectedThresholdImageFilter.New(
            Input=image,
            Lower=lower_thresh,
            Upper=upper_thresh,
            ReplaceValue=1,
        )
        connected_threshold_filter.AddSeed(seed_point)
        connected_threshold_filter.Update()
        out = connected_threshold_filter.GetOutput()
        out = itk.array_from_image(out)
        res = np.maximum(res, out)
    res = itk.image_from_array(res)
    res.CopyInformation(image)
    return res


def _binary_closing(image, radius=1):
    StructuringElementType = itk.FlatStructuringElement[3]
    structuring_element = StructuringElementType.Ball(radius)
    ClosingFilterType = itk.BinaryMorphologicalClosingImageFilter[
        type(image), type(image), StructuringElementType
    ]
    closing_filter = ClosingFilterType.New()
    closing_filter.SetInput(image)
    closing_filter.SetKernel(structuring_element)
    closing_filter.SetForegroundValue(1)
    closing_filter.Update()
    return closing_filter.GetOutput()


def step3_images_segmentation(image_fixed, image_output):
    image_fixed_segmented = _segment_tumor(
        image_fixed, [(120, 65, 84), (99, 77, 84)], 0.23
    )
    image_fixed_segmented = itk.image_from_array(
        itk.array_from_image(image_fixed_segmented).astype(np.uint8)
    )
    image_fixed_segmented = _binary_closing(image_fixed_segmented)
    image_output_segmented = _segment_tumor(
        image_output, [(120, 65, 80), (99, 77, 80)], 0.23
    )
    image_output_segmented = itk.image_from_array(
        itk.array_from_image(image_output_segmented).astype(np.uint8)
    )
    image_output_segmented = _binary_closing(image_output_segmented)
    return image_fixed_segmented, image_output_segmented


def step4_visualization(image_fixed_segmented, image_output_segmented):
    image_diff = itk.image_from_array(
        itk.array_from_image(image_fixed_segmented).astype(np.float32)
        - itk.array_from_image(image_output_segmented).astype(np.float32)
    )
    vtk_diff_image = itk.vtk_image_from_image(image_diff)
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(vtk_diff_image)
    color_func = vtk.vtkColorTransferFunction()
    color_func.AddRGBPoint(-1, 1, 0, 0)
    color_func.AddRGBPoint(0, 0, 0, 0)
    color_func.AddRGBPoint(1, 0, 1, 0)
    opacity_func = vtk.vtkPiecewiseFunction()
    opacity_func.AddPoint(-1, 0.5)
    opacity_func.AddPoint(0, 0)
    opacity_func.AddPoint(1, 0.5)
    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_func)
    volume_property.SetScalarOpacity(opacity_func)
    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(volume_property)
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 600)
    render_window.SetWindowName("Tumor Evolution")
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    renderer.AddVolume(volume)
    renderer.SetBackground(0, 0, 0)
    render_window.Render()
    interactor.Start()


def main():
    pixel_t = itk.F
    image_fixed = itk.imread(_IMAGE_FIXED_PATH, pixel_t)
    image_moving = itk.imread(_IMAGE_MOVING_PATH, pixel_t)
    print("[X] Step 1: Data - Done")
    image_output = step2_images_alignment(image_fixed, image_moving)
    print("[X] Step 2: Images Alignment - Done")
    image_fixed_segmented, image_output_segmented = step3_images_segmentation(
        image_fixed, image_output
    )
    print("[X] Step 3: Images Segmentation - Done")
    step4_visualization(image_fixed_segmented, image_output_segmented)
    print("[X] Step 4: Images Visualization - Done")


if __name__ == "__main__":
    main()
