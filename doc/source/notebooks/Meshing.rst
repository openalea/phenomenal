
Meshing
=======

1. Prerequisites
----------------

1.1 Load cloud point of voxel centers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from alinea.phenomenal.data_plants.plant_1 import plant_1_voxel_centers
    from alinea.phenomenal.display.multi_view_reconstruction import show_points_3d
    
    voxel_size = 10
    voxel_centers = plant_1_voxel_centers(voxel_size=voxel_size)
    
    # Display it
    show_points_3d(voxel_centers)

.. code:: python

    from alinea.phenomenal.multi_view_reconstruction.routines import voxel_centers_to_image_3d
    
    # Convert voxel_centers to image3D
    image_3d = voxel_centers_to_image_3d(voxel_centers, voxel_size)

2. Meshing
----------

2.1 Do meshing
~~~~~~~~~~~~~~

.. code:: python

    from alinea.phenomenal.mesh.algorithms import meshing
    
    
    vertices, faces = meshing(image_3d,
                              reduction=0.95, 
                              smoothing_iteration=2, 
                              verbose=True)


.. parsed-literal::

    ================================================================
    Marching cubes :
    	Iso value : 1.0
    
    	There are 9410 points.
    	There are 19129 polygons.
    
    ================================================================
    ================================================================
    Smoothing :
    	Feature angle : 120.0
    	Number of iteration : 2
    	Pass band : 0.01
    
    ================================================================
    ================================================================
    Decimation :
    	Reduction (percentage) : 0.95
    
    	Before decimation
    	-----------------
    	There are 9410 points.
    	There are 19129 polygons.
    
    	After decimation
    	-----------------
    	There are 484 points.
    	There are 956 polygons.
    ================================================================
    

2.3 Read & write
~~~~~~~~~~~~~~~~

.. code:: python

    from alinea.phenomenal.mesh.formats import (
        write_vertices_faces_to_json_file,
        read_json_file_to_vertices_faces)
    
    # Write
    write_vertices_faces_to_json_file(vertices, faces, 'mesh.json')
    
    # Read
    vertices, faces = read_json_file_to_vertices_faces('mesh.json')

2.4 Display it
~~~~~~~~~~~~~~

.. code:: python

    from alinea.phenomenal.display.mesh import show_mesh
    
    show_mesh(vertices, faces)

2.5 Normals of each faces
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from alinea.phenomenal.mesh.routines import normals, centers
    
    normals = normals(vertices, faces)
    centers = centers(vertices, faces)
    
    # Display it
    show_mesh(vertices, faces, normals=normals, centers=centers)

2.6. Surface area estimation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import skimage.measure
    
    surface = skimage.measure.mesh_surface_area(vertices, faces)
    
    print 'Mesh surface area : ', surface


.. parsed-literal::

    Mesh surface area :  880873.046613
    

3. PlantGL Format
-----------------

3.1 Add mesh to PantGL scene and display it
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import openalea.plantgl.scenegraph as sg
    import openalea.plantgl.all as pgl
    
    scene = sg.Scene()
    tset = sg.FaceSet(pointList=vertices, indexList=faces)
    scene += tset
    
    # Display it
    pgl.Viewer.display(scene)
