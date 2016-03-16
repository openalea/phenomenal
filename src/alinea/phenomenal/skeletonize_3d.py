# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
import math

import numpy
import openalea.plantgl.algo
import openalea.plantgl.scenegraph
import openalea.plantgl.math

import vplants.treeeditor3d.mtgeditor


# ==============================================================================


def voxel_centers_to_vectors(voxel_centers):

    vectors = list()
    for voxel_center in voxel_centers:
        vectors.append(
            openalea.plantgl.math.Vector3(numpy.double(voxel_center[0]),
                                          numpy.double(voxel_center[1]),
                                          numpy.double(voxel_center[2])))

    return vectors


def skeletonize_3d_xu_method(points,
                             bin_length,
                             k=20,
                             connect_all_points=True,
                             verbose=False):

    root = openalea.plantgl.math.Vector3(points[points.getZMinIndex()])

    len_root = len(points)
    points.append(root)

    positions, parents, point_components = \
        openalea.plantgl.algo.skeleton_from_distance_to_root_clusters(
            points,
            len_root,
            bin_length,
            k=k,
            connect_all_points=connect_all_points,
            verbose=verbose)

    del points[len_root]

    return positions, parents, point_components, root


def skeletonize_3d_segment(points_3d,
                           contraction_radius=0,
                           bin_length=50,
                           k=20,
                           connect_all_points=True,
                           verbose=False):

    vectors = voxel_centers_to_vectors(points_3d)

    points = openalea.plantgl.scenegraph.Point3Array(vectors)

    if contraction_radius != 0:
        points = openalea.plantgl.algo.contract_point3(
            points, contraction_radius)

    positions, parents, point_components, root = skeletonize_3d_xu_method(
        points,
        bin_length,
        k=k,
        connect_all_points=connect_all_points,
        verbose=verbose)

    print len(positions), len(parents), len(point_components), root

    segments = list()

    print len(points)
    my_point = list()
    for index_position in point_components[0]:
        if index_position < len(points):
            my_point.append(points[index_position])

    segments.append([positions[0], root, my_point])

    for i in range(1, len(positions)):
        my_point = list()
        for index_position in point_components[i]:
                my_point.append(points[index_position])

        print i, positions[i], parents[i], positions[parents[i]]

        segments.append([positions[i], positions[parents[i]], my_point])

    return segments


def skeletonize_3d(voxel_centers,
                   contraction_radius=0,
                   bin_ratio=50,
                   k=20,
                   connect_all_points=True,
                   verbose=False):

    vectors = voxel_centers_to_vectors(voxel_centers)

    points = openalea.plantgl.scenegraph.Point3Array(vectors)
    if contraction_radius != 0:
        points = openalea.plantgl.algo.contract_point3(
            points, contraction_radius)

    positions, parents, point_components, root = skeletonize_3d_xu_method(
        points,
        bin_ratio,
        k=k,
        connect_all_points=connect_all_points,
        verbose=verbose)

    return positions, parents, point_components, root


def test_skeletonize_3d(voxel_centers,
                        contraction_radius=10,
                        bin_ratio=50,
                        k=20,
                        connect_all_points=True,
                        verbose=True):

    positions, parents, pointcomponents, root_position = skeletonize_3d(
        voxel_centers,
        contraction_radius,
        bin_ratio,
        k=k,
        connect_all_points=connect_all_points,
        verbose=verbose)

    vectors = voxel_centers_to_vectors(voxel_centers)

    points = openalea.plantgl.algo.contract_point3(
        openalea.plantgl.scenegraph.Point3Array(vectors), contraction_radius)
    points = openalea.plantgl.scenegraph.PointSet(points)

    qapp = vplants.treeeditor3d.mtgeditor.QApplication([])
    w = vplants.treeeditor3d.mtgeditor.MTGEditor()
    w.show()

    w.mtgeditor.setPoints(points)
    w.mtgeditor.addRoot(root_position)
    mtg = w.mtgeditor.mtg

    startfrom = 2

    filter_short_branch = False
    angle_between_trunk_and_lateral = 60

    children, root = openalea.plantgl.algo.determine_children(parents)
    print children, root

    clength = openalea.plantgl.algo.subtrees_size(children, root)

    node2skel = {}
    if openalea.plantgl.math.norm(positions[0] - root_position) > 1e-3:
        startfrom = mtg.add_child(parent=startfrom, position=positions[0])
    node2skel[0] = startfrom

    mchildren = list(children[root])
    npositions = mtg.property('position')
    removed = []
    if len(mchildren) >= 2 and filter_short_branch:
        mchildren = [c for c in mchildren if len(children[c]) > 0]
        if len(mchildren) != len(children[root]):
            removed = list(set(children[root]) - set(mchildren))

    mchildren.sort(lambda x, y: -cmp(clength[x], clength[y]))
    toprocess = [(c, startfrom, '<' if i == 0 else '+') for i, c in
                 enumerate(mchildren)]
    while len(toprocess) > 0:
        nid, parent, edge_type = toprocess.pop(0)
        pos = positions[nid]

        mtgnode = mtg.add_child(parent=parent,
                                label='N',
                                edge_type=edge_type,
                                position=pos)

        mchildren = list(children[nid])

        if len(mchildren) > 0:
            if len(mchildren) >= 2 and filter_short_branch:
                mchildren = [c for c in mchildren if len(children[c]) > 0]
                if len(mchildren) != len(children[nid]):
                    removed = list(set(children[nid]) - set(mchildren))
            if len(mchildren) > 0:

                mchildren.sort(lambda x, y: -cmp(clength[x], clength[y]))

                first_edge_type = '<'

                langle = math.degrees(math.acos(openalea.plantgl.math.dot(
                    openalea.plantgl.math.direction(
                        pos - npositions[parent]),
                    openalea.plantgl.math.direction(
                        positions[mchildren[0]] - pos))))

                if langle > angle_between_trunk_and_lateral:
                    first_edge_type = '+'
                edges_types = [first_edge_type] + ['+' for i in
                                                   xrange(len(mchildren) - 1)]
                toprocess += [(c, mtgnode, e) for c, e in
                              zip(mchildren, edges_types)]

    print 'Remove short nodes ',','.join(map(str,removed))

    w.mtgeditor.updateMTGView()
    w.mtgeditor.updateGL()
    qapp.exec_()

if __name__ == '__main__':

    import alinea.phenomenal.plant_1

    voxel_size = 20
    voxel_centers = alinea.phenomenal.plant_1.plant_1_voxel_centers(
        voxel_size=voxel_size)

    test_skeletonize_3d(voxel_centers)