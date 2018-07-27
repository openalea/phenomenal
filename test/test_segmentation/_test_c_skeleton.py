import openalea.phenomenal.segmentation._c_skeleton as c_skeleton
import numpy

# n = 3
# a = numpy.zeros((n, n), dtype=numpy.uint8)
# b = numpy.ones((n, n), dtype=numpy.uint8)
# z = numpy.zeros((n, n), dtype=numpy.uint8)
# c_skeleton.fpy(n, a, b, z)

# ==============================================================================

n = 5
len_segments = 2
len_images = 2
list_array = [None] * len_segments * len_images
for i in range(len_segments):
    for j in range(len_images):
        list_array[i * len_images + j] = numpy.random.rand(n, n)

is_removed = numpy.zeros(len_segments, dtype=numpy.uint8)
print is_removed
c_skeleton.skeletonize(list_array, is_removed, len_segments, len_images)
print is_removed