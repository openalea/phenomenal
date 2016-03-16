
Meshing
=======

1. Prerequisites
----------------

1.1 Load cloud point of voxel centers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import alinea.phenomenal.plant_1
    import alinea.phenomenal.viewer
    
    voxel_size = 3
    voxel_centers = alinea.phenomenal.plant_1.plant_1_voxel_centers(voxel_size=voxel_size)
    
    # Display it
    alinea.phenomenal.viewer.show_points_3d(voxel_centers)

2. Meshing
----------

2.1 Do meshing
~~~~~~~~~~~~~~

.. code:: python

    import alinea.phenomenal.mesh
    
    vertices, faces = alinea.phenomenal.mesh.meshing(
        voxel_centers, voxel_size,
        reduction=0.95, smoothing_iteration=2, verbose=True)


.. parsed-literal::

    ================================================================
    Marching cubes :
    	Iso value : 0.5
    
    	There are 171558 points.
    	There are 342336 polygons.
    
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
    	There are 171558 points.
    	There are 342336 polygons.
    
    	After decimation
    	-----------------
    	There are 8588 points.
    	There are 17116 polygons.
    ================================================================
    

2.3 Read & write
~~~~~~~~~~~~~~~~

.. code:: python

    # Write
    alinea.phenomenal.misc.write_mesh(vertices, faces, 'mesh')
    
    # Read
    vertices, faces = alinea.phenomenal.misc.read_mesh('mesh')

2.4 Display it
~~~~~~~~~~~~~~

.. code:: python

    import alinea.phenomenal.viewer
    
    alinea.phenomenal.viewer.show_mesh(vertices, faces)

2.5 Normals of each faces
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    normals = alinea.phenomenal.mesh.compute_normal(vertices, faces)
    centers = alinea.phenomenal.mesh.center_of_vertices(vertices, faces)
    
    # Display it
    alinea.phenomenal.viewer.show_mesh(vertices, faces, normals=normals, centers=centers)

2.6. Surface area estimation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import skimage.measure
    
    surface = skimage.measure.mesh_surface_area(vertices, faces)
    
    print 'Mesh surface area : ', surface


.. parsed-literal::

    Mesh surface area :  1052250.86034
    

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
