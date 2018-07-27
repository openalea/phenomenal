#include "skel.h"
#include <stdio.h>
#include <stdlib.h>

int fc(int n,
       const unsigned char* image_1,
       const unsigned char* image_2,
       unsigned char* image_output)
{
    for(int i = 0;  i < n;  ++i)
    {
        for(int j = 0; j < n; ++j)
        {
            image_output[i * n + j] = image_1[i * n + j] + image_2[i * n + j];
        }
    }
    return n;
}

bool is_uncovered(const int* image,
                  const int* shape,
                  const int** images,
                  const int* len_images,
                  const int* nb_required_pixel)
{
    bool uncovered = true;
    int sum_positive_pixel = 0;

    for (int xy = 0; xy < shape[0] * shape[1]; ++xy)
    {
        if (image[xy] == 0)
        {
            continue;
        }
        else
        {
            uncovered = true;
            for (int k = 0;  k < *len_images;  ++k)
            {
                if (images[k][xy] > 0)
                {
                    uncovered = false;
                    break;
                }
            }
            if (uncovered)
            {
                ++sum_positive_pixel;
                if (sum_positive_pixel >= *nb_required_pixel)
                {
                    return true;
                }
            }
        }
    }

    return false;
}


int my_func_c(int** images,
              int** shapes,
              unsigned char* is_removed,
              int len_segments,
              int len_images,
              int nb_required_pixel,
              int required_visible)
{

    int weight = 0;

    const int** imgs = (const int**) malloc(
        (len_segments + 1) * sizeof(const int*));
    int len_imgs = 0;

    for(int i = 0;  i < len_segments;  ++i)
    {
        weight = 0;
        for(int j = 0; j < len_images; ++j)
        {
            len_imgs = 0;
            for (int k = 0;  k < len_segments;  ++k)
            {
                if (k != i && is_removed[k] == 0)
                {
                    imgs[len_imgs] = images[k * len_images + j];
                    len_imgs++;
                }
            }
            imgs[len_imgs] = images[len_segments * len_images + j];
            len_imgs++;

            if (is_uncovered(images[i * len_images + j],
                             shapes[i * len_images + j],
                             imgs,
                             &len_imgs,
                             &nb_required_pixel))
            {
                weight += 1;
                if (weight >= required_visible)
                {
                    break;
                }
            }
        }
        if (weight < required_visible)
        {
            is_removed[i] = 1;
        }
    }
    free(imgs);
    return 0;
}

