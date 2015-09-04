# -*- python -*-
#
#       test_reconstruction_3D_with_manual_calibration: Module Description
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

"""
Write the doc here...
"""

__revision__ = ""

#       ========================================================================
#       External Import
import cv2
import skimage.morphology
from math import degrees, acos
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import copy

#       ========================================================================
#       Local Import
import vplants.treeeditor3d.mtgeditor as mtgeditor

from openalea.plantgl.all import *

#       ========================================================================
#       Code

def skeletonize_image_skimage(image):
    """

    :param image:
    :return:
    """

    image[image == 255] = 1
    skeleton = skimage.morphology.skeletonize(image)
    skeleton = skeleton.astype(np.uint8)
    skeleton[skeleton > 0] = 255

    return skeleton


def skeletonize_image_opencv(image):
    skeleton = np.zeros(image.shape, np.uint8)

    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    while cv2.countNonZero(image) > 0:
        eroded = cv2.erode(image, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(image, temp)
        skeleton = cv2.bitwise_or(skeleton, temp)
        image = eroded.copy()

    return skeleton


def skeletonize_3d_xu_method(cubes,
                             bin_ratio,
                             k=20,
                             connect_all_points=True,
                             verbose=False):

    vectors = list()

    for cube in cubes:
        x = np.double(cube.position[0, 0])      # x
        y = - np.double(cube.position[0, 2])    # z
        z = - np.double(cube.position[0, 1])    # y

        v = Vector3(x, y, z)
        vectors.append(v)

    points = euclidian_contraction(Point3Array(vectors), 40)

    root = Vector3(points[points.getZMinIndex()])

    mini, maxi = points.getZMinAndMaxIndex()
    z_distance = points[maxi].z - points[mini].z
    bin_length = z_distance / bin_ratio

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

    print len(positions), len(parents), len(point_components)
    del points[len_root]

    segments = list()
    segments.append([positions[0], root])

    for i in range(1, len(positions)):
        segments.append([positions[i], positions[parents[i]]])

    return segments


def euclidian_contraction(points, radius):
    return contract_point3(points, radius)


def closest_cubes(cube, cubes):
    r = cube.radius

    x = cube.position[0, 0] + r
    y = cube.position[0, 1] + r
    z = cube.position[0, 2] + r
    pos = np.float32([[x, y, z]])

    dist = np.linalg.norm(cube.position - pos) * 2
    closest_neighbors = list()
    for c in cubes:
        if c is cube:
            continue

        distance = np.linalg.norm(cube.position - c.position)
        if distance <= dist:
            closest_neighbors.append(c)

    return closest_neighbors


def skeletonize_3d_transform_distance(cubes):

    import phenomenal.test.tools_test as tools_test

    cubes_transform = list()
    number = 1

    cubes_save = copy.copy(cubes)

    tools_test.show_cube(cubes, 10)

    while cubes:

        cubes_tmp = list()
        while True:
            try:
                cube = cubes.pop()
                closest = closest_cubes(cube, cubes_save)

                if len(closest) < 26:
                    cubes_transform.append([number, cube])
                else:
                    cubes_tmp.append(cube)

            except IndexError:
                break

        number += 1
        tools_test.show_cube(cubes_tmp, 10)
        cubes = cubes_tmp
        cubes_save = copy.copy(cubes)



    print len(cubes), len(cubes_transform)


def my_xu_method(mtg, startfrom, pointList, binlength,
                 k=20,
                 verbose=False,
                 filter_short_branch=False,
                 angle_between_trunk_and_lateral=60):

    rootpos = Vector3(mtg.property('position')[startfrom])

    print 'startfrom and rootpos : ', startfrom, rootpos

    root = len(pointList)
    connect_all_points = False if mtg.nb_vertices(mtg.max_scale()) > 1 else True
    pointList.append(rootpos)
    connect_all_points = False

    print 'binlength :', binlength

    positions, parents, pointcomponents = \
        skeleton_from_distance_to_root_clusters(
            pointList,
            root,
            binlength,
            k,
            connect_all_points=True,
            verbose=verbose)

    print len(positions), len(parents), len(pointcomponents)

    del pointList[root]


    segments = list()
    segments.append([positions[0], rootpos])

    for i in range(1, len(positions)):
        segments.append([positions[i], positions[parents[i]]])

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    for i in range(len(positions)):
        x1 = positions[i][0]
        y1 = positions[i][1]
        z1 = positions[i][2]

        index_parent = parents[i]

        if i == 0:
            x2 = rootpos[0]
            y2 = rootpos[1]
            z2 = rootpos[2]
        else:
            x2 = positions[index_parent][0]
            y2 = positions[index_parent][1]
            z2 = positions[index_parent][2]

        ax.plot([x1, x2],
                [y1, y2],
                [z1, z2], label='parametric curve')

    plt.show()

    children, root = determine_children(parents)
    print children, root

    clength = subtrees_size(children, root)

    node2skel = {}
    assert parents[0] == 0
    if verbose:
        print positions[0], mtg.property('position')[startfrom]
    if norm(positions[0]-rootpos) > 1e-3:
        startfrom = mtg.add_child(parent=startfrom,position=positions[0])
    node2skel[0] = startfrom

    # for node, parent in enumerate(parents[1:len(parents)]):
    #     if verbose: print node, parent, node2skel.get(parent)
    #     ni = mtg.add_child(parent=node2skel[parent],position=positions[node+1])
    #     node2skel[node+1] = ni

    mchildren = list(children[root])
    npositions = mtg.property('position')
    removed = []
    if len(mchildren) >= 2 and filter_short_branch:
        mchildren = [c for c in mchildren if len(children[c]) > 0]
        if len(mchildren) != len(children[root]):
            removed = list(set(children[root])-set(mchildren))

    mchildren.sort(lambda x, y: -cmp(clength[x], clength[y]))
    toprocess = [(c,startfrom,'<' if i == 0 else '+') for i,c in enumerate(mchildren)]
    while len(toprocess) > 0:
        nid, parent, edge_type = toprocess.pop(0)
        pos = positions[nid]
        mtgnode = mtg.add_child(parent = parent, label='N',edge_type = edge_type, position = pos)
        mchildren = list(children[nid])
        if len(mchildren) > 0:
            if len(mchildren) >= 2 and filter_short_branch:
                mchildren = [c for c in mchildren if len(children[c]) > 0]
                if len(mchildren) != len(children[nid]):
                    removed = list(set(children[nid])-set(mchildren))
            if len(mchildren) > 0:
                mchildren.sort(lambda x,y : -cmp(clength[x],clength[y]))
                first_edge_type = '<'
                langle = degrees(acos(dot(direction(pos-npositions[parent]),direction(positions[mchildren[0]]-pos))))
                if langle > angle_between_trunk_and_lateral:
                    first_edge_type = '+'
                edges_types = [first_edge_type]+['+' for i in xrange(len(mchildren)-1)]
                toprocess += [(c,mtgnode,e) for c,e in zip(mchildren,edges_types)]

    print 'Remove short nodes ',','.join(map(str,removed))
    return mtg


def test_skeletonize_3d(cubes, bin_ratio):

    # ui = editor_ui.Ui_MainWindow()

    qapp = mtgeditor.QApplication([])
    w = mtgeditor.MTGEditor()
    w.show()

    vectors = list()

    for cube in cubes:
        x = np.double(cube.position[0, 0])      # x
        y = - np.double(cube.position[0, 2])    # z
        z = - np.double(cube.position[0, 1])    # y
        v = Vector3(x, y, z)
        vectors.append(v)

    points = PointSet(Point3Array(vectors))

    root = Vector3(points.pointList[points.pointList.getZMinIndex()])



    points = PointSet(euclidian_contraction(Point3Array(vectors), 40))


    w.mtgeditor.setPoints(points)

    root = Vector3(points.pointList[points.pointList.getZMinIndex()])
    w.mtgeditor.addRoot(root)

    startfrom = 2
    mini, maxi = points.pointList.getZMinAndMaxIndex()
    zdist = points.pointList[maxi].z - points.pointList[mini].z
    binlength = zdist / bin_ratio
    verbose = True

    my_xu_method(w.mtgeditor.mtg,
                 startfrom,
                 points.pointList,
                 binlength,
                 verbose=verbose)

    w.mtgeditor.updateMTGView()
    w.mtgeditor.updateGL()
    qapp.exec_()


#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    test_skeletonize_3d()






