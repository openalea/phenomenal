# -*- python -*-
#
#       skeletonize_3d.py :
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
#       ========================================================================

#       ========================================================================
#       External Import
from math import degrees, acos
import numpy as np


#       ========================================================================
#       Local Import
import vplants.treeeditor3d.mtgeditor as mtgeditor
from openalea.plantgl.all import *

#       ========================================================================
#       Code


def cubes_to_point3array(cubes):
    vectors = list()
    for cube in cubes:
        x = np.double(cube.position[0, 0])
        y = np.double(cube.position[0, 1])
        z = np.double(cube.position[0, 2])

        v = Vector3(x, y, z)
        vectors.append(v)

    return vectors


def euclidian_contraction(points, radius):
    return contract_point3(points, radius)


def skeletonize_3d_xu_method(points,
                             bin_length,
                             k=20,
                             connect_all_points=True,
                             verbose=False):

    root = Vector3(points[points.getZMinIndex()])

    len_root = len(points)
    points.append(root)

    positions, parents, point_components = \
        skeleton_from_distance_to_root_clusters(
            points,
            len_root,
            bin_length,
            k=k,
            connect_all_points=connect_all_points,
            verbose=verbose)

    del points[len_root]

    return positions, parents, point_components, root


def skeletonize_3d_segment(cubes,
                           contraction_radius,
                           bin_length,
                           k=20,
                           connect_all_points=True,
                           verbose=False):

    vectors = cubes_to_point3array(cubes)

    points = Point3Array(vectors)

    points = euclidian_contraction(points, contraction_radius)

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

        segments.append([positions[i], positions[parents[i]], my_point])

    return segments


def skeletonize_3d(cubes,
                   contraction_radius,
                   bin_ratio,
                   k=20,
                   connect_all_points=True,
                   verbose=False):

    vectors = cubes_to_point3array(cubes)

    points = Point3Array(vectors)

    points = euclidian_contraction(points, contraction_radius)

    positions, parents, point_components, root = skeletonize_3d_xu_method(
        points,
        bin_ratio,
        k=k,
        connect_all_points=connect_all_points,
        verbose=verbose)

    return positions, parents, point_components, root


def test_skeletonize_3d(cubes,
                        contraction_radius,
                        bin_ratio,
                        k=20,
                        connect_all_points=True,
                        verbose=True):

    positions, parents, pointcomponents, root_position = skeletonize_3d(
        cubes,
        contraction_radius,
        bin_ratio,
        k=k,
        connect_all_points=connect_all_points,
        verbose=verbose)


    vectors = cubes_to_point3array(cubes)
    points = PointSet(euclidian_contraction(Point3Array(vectors),
                                            contraction_radius))


    qapp = mtgeditor.QApplication([])
    w = mtgeditor.MTGEditor()
    w.show()

    w.mtgeditor.setPoints(points)
    w.mtgeditor.addRoot(root_position)
    mtg = w.mtgeditor.mtg

    startfrom = 2

    filter_short_branch = False
    angle_between_trunk_and_lateral = 60

    children, root = determine_children(parents)
    print children, root

    clength = subtrees_size(children, root)

    node2skel = {}
    if norm(positions[0] - root_position) > 1e-3:
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

                langle = degrees(acos(dot(
                    direction(pos - npositions[parent]),
                    direction(positions[mchildren[0]] - pos))))

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


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None