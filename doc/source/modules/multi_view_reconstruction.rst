=========================
Multi-view Reconstruction
=========================

.. automodule:: alinea.phenomenal.multi_view_reconstruction
    :members:
    :show-inheritance:
    :synopsis: doc todo

    .. rubric:: Processing Function

    .. autosummary::

        reconstruction_3d
        kept_visible_voxel
        voxel_is_visible_in_image
        get_bounding_box_voxel_projected
        get_voxel_corners
        split_voxel_centers_in_eight
        split_voxel_centers_in_four

    .. rubric:: Post-Processing Function

    .. autosummary::

        project_voxel_centers_on_image
        error_reconstruction
        error_reconstruction_lost
        error_reconstruction_precision
        volume
