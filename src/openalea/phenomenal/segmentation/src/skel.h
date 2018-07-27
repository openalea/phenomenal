// fc.h: numpy arrays from cython , double*

int fc(int n,
       const unsigned char* a,
       const unsigned char* b,
       unsigned char* z);


int my_func_c(int **images,
              int **shapes,
              unsigned char* is_removed,
              int len_segments,
              int len_images,
              int nb_required_pixel,
              int required_visible);
