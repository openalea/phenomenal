import numpy as np
cimport numpy as np
from libc.stdlib cimport malloc, free

cdef extern from "skel.h":
    int fc(int n, unsigned char * a, unsigned char* b, unsigned char* z)

cdef extern from "skel.h":
    int my_func_c(int **data,
                  int **shape,
                  unsigned char* is_removed,
                  int len_segments,
                  int len_images,
                  int nb_required_pixel,
                  int required_visible)


def fpy(n, np.ndarray[np.uint8_t, ndim=2] a,
           np.ndarray[np.uint8_t, ndim=2] b,
           np.ndarray[np.uint8_t, ndim=2] z):
    """ wrap np arrays to fc( a.data ... ) """
    assert n <= len(a) == len(b) == len(z)
    fcret = fc(n,
               <const unsigned char*> a.data,
               <const unsigned char*> b.data,
               <unsigned char*> z.data)

    return fcret


def skeletonize(list list_of_arrays,
                np.ndarray[np.uint8_t, ndim=1] is_removed,
                int len_segments,
                int len_images,
                int nb_required_pixel,
                int required_visible):

    cdef int n_arrays  = len_segments * len_images + len_images
    cdef int **images = <int **> malloc(n_arrays * sizeof(int *))
    cdef int **shapes   = <int **> malloc(n_arrays * sizeof(int *))
    cdef int x;
    cdef np.ndarray[int, ndim=2, mode="c"] temp;

    for i in range(n_arrays):
        temp = list_of_arrays[i]
        images[i]  = &temp[0, 0]
        shapes[i] = <int *> malloc(2 * sizeof(int))
        for j in range(2):
            shapes[i][j] = list_of_arrays[i].shape[j]

    x = my_func_c(images,
                  shapes,
                  <unsigned char*> is_removed.data,
                  len_segments,
                  len_images,
                  nb_required_pixel,
                  required_visible)
    # Free memory
    for i in range(n_arrays):
        free(shapes[i])
    free(images)
    free(shapes)

    return x
