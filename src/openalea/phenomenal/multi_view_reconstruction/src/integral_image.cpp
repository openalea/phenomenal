#include "integral_image.h"

void c_integral_image(const unsigned char* input,
                      const unsigned int size_x,
                      const unsigned int size_y,
                      unsigned int* output)
{

    /* ####################################################### */
    /*             INITIALIZE BORDER X OF THE IMAGE            */
    /* ####################################################### */
    for(unsigned int x = 1; x < size_x; ++x)
    {
        if (input[x * size_y] > 0)
        {
            output[x * size_y] = 1;
        }
        else
        {
            output[x * size_y] = 0;
        }
    }

    /* ####################################################### */
    /*               INITIALIZE BORDER Y OF THE IMAGE          */
    /* ####################################################### */

    for(unsigned int y = 1; y < size_y; ++y)
    {
        if (input[y] > 0)
        {
            output[y] = 1;
        }
        else
        {
            output[y] = 0;
        }
    }

    /* ####################################################### */
    /*               ALL THE IMAGES                            */
    /* ####################################################### */

    int r = 0;
    for(unsigned int x = 1; x < size_x; ++x)
    {
        for(unsigned int y = 1; y < size_y; ++y)
        {
            if (input[x * size_y + y] > 0)
            {
                r = 1;
            }
            else
            {
                r = 0;
            }
            r += output[(x - 1) * size_y + y];
            r += output[x * size_y + y - 1];
            r -= output[(x - 1) * size_y + y - 1];
            output[x * size_y + y] = r;
        }
    }
}