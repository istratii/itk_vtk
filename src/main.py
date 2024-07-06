
import itk
import matplotlib.pyplot as plt

def registred_images(fixed_filepath, moving_filepath, output_filepath):
    PixelType = itk.F
    fixed_image = itk.imread(fixed_filepath, PixelType)
    moving_image = itk.imread(moving_filepath, PixelType)

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
    fixed_interpolation = itk.LinearInterpolateImageFunction[FixedImageType, itk.D].New()
    metric.SetFixedInterpolator(fixed_interpolation)

    registration = itk.ImageRegistrationMethodv4[FixedImageType, FixedImageType].New(               FixedImage=fixed_image, 
                                               MovingImage=moving_image, 
                                               Metric=metric,
                                               Optimizer=optimizer, 
                                               InitialTransform=initialTransform)

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

    resampler = itk.ResampleImageFilter.New(Input=moving_image, Transform=transform, UseReferenceImage=True,
                                            ReferenceImage=fixed_image)
    resampler.SetDefaultPixelValue(100)

    OutputPixelType = itk.ctype('unsigned char')
    OutputImageType = itk.Image[OutputPixelType, dimension]
    caster = itk.CastImageFilter[FixedImageType, OutputImageType].New(resampler)

    itk.imwrite(caster, output_filepath)

    print(f"Registered image saved to {output_filepath}")




def main():
    # Dmages
    fixed_filepath = '../Data/case6_gre1.nrrd'
    moving_filepath = '../Data/case6_gre2.nrrd'
    output_filepath = '../Data/brain-registered.nrrd'
    # Recalage 
    registred_images(fixed_filepath, moving_filepath, output_filepath)
    # Segmentation
    # TO DO 
    # Visulasition 
    # TO DO 
    
main()