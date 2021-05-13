import numpy as np
from PIL import Image
from scipy import ndimage

import torch
import torchvision.transforms as transforms

class TPSTransform(object):
    def __init__(self, tps_points_per_dim = 5):
        self.tps_points_per_dim = tps_points_per_dim
        return

    def __apply_tps(self, img, tps_params):
        img_np = np.array(img)
        #print( "[__apply_tps] <before> img_np shape={}, min={}, max={} : ".format(img_np.shape, np.min(img_np), np.max(img_np)) )
        if( len(img_np.shape) != 3 ):
            img_np = img_np.reshape(img_np.shape[0], img_np.shape[1], -1)
            img_np = tps_warp_2( img_np, tps_params['dst'], tps_params['src'], interpolation_order = 0 )
        else:
            img_np = tps_warp_2( img_np, tps_params['dst'], tps_params['src'], interpolation_order = 1 )            

        #print( "[__apply_tps] <after> img_np shape={}, min={}, max={} : ".format(img_np.shape, np.min(img_np), np.max(img_np)) )
        new_img = Image.fromarray(img_np.squeeze())
        return new_img

    def __call__(self, img):
        #print( "img.size : ", img.size )
        w, h = img.size
        img_np = np.array(img)
        src = _get_regular_grid(img_np, points_per_dim=self.tps_points_per_dim )
        dst = _generate_random_vectors(img_np, src, scale=0.1 * w)
        tps_params = {'src': src, 'dst': dst}
        #print( "src : ", src )
        #print( "dst : ", dst )

        new_img = self.__apply_tps(img, tps_params)
        #print( "new_img.size : ", new_img.size )
        return new_img


# Copyright 2007 Zachary Pincus
# This file is part of CellTool.
#
# CellTool is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# File available at https://github.com/zpincus/celltool under the
# GNU General Public License v2.0.
#
# The code was modified to reflect the image instead of filling with
# black pixels for the skin-data-augmentation project.


def warp_images(from_points, to_points, images, output_region, interpolation_order = 1, approximate_grid=2):
    """Define a thin-plate-spline warping transform that warps from the from_points
    to the to_points, and then warp the given images by that transform. This
    transform is described in the paper: "Principal Warps: Thin-Plate Splines and
    the Decomposition of Deformations" by F.L. Bookstein.
    Parameters:
        - from_points and to_points: Nx2 arrays containing N 2D landmark points.
        - images: list of images to warp with the given warp transform.
        - output_region: the (xmin, ymin, xmax, ymax) region of the output
                image that should be produced. (Note: The region is inclusive, i.e.
                xmin <= x <= xmax)
        - interpolation_order: if 1, then use linear interpolation; if 0 then use
                nearest-neighbor.
        - approximate_grid: defining the warping transform is slow. If approximate_grid
                is greater than 1, then the transform is defined on a grid 'approximate_grid'
                times smaller than the output image region, and then the transform is
                bilinearly interpolated to the larger region. This is fairly accurate
                for values up to 10 or so.
    """
    transform = _make_inverse_warp(from_points, to_points, output_region, approximate_grid)
    return [ndimage.map_coordinates(np.asarray(image), transform, order=interpolation_order, mode='reflect') for image in images]

def _make_inverse_warp(from_points, to_points, output_region, approximate_grid):
    x_min, y_min, x_max, y_max = output_region
    if approximate_grid is None: approximate_grid = 1
    x_steps = (x_max - x_min) / approximate_grid
    y_steps = (y_max - y_min) / approximate_grid
    x, y = np.mgrid[x_min:x_max:x_steps*1j, y_min:y_max:y_steps*1j]

    # make the reverse transform warping from the to_points to the from_points, because we
    # do image interpolation in this reverse fashion
    transform = _make_warp(to_points, from_points, x, y)

    if approximate_grid != 1:
        # linearly interpolate the zoomed transform grid
        new_x, new_y = np.mgrid[x_min:x_max+1, y_min:y_max+1]
        x_fracs, x_indices = np.modf((x_steps-1)*(new_x-x_min)/float(x_max-x_min))
        y_fracs, y_indices = np.modf((y_steps-1)*(new_y-y_min)/float(y_max-y_min))
        x_indices = x_indices.astype(int)
        y_indices = y_indices.astype(int)
        x1 = 1 - x_fracs
        y1 = 1 - y_fracs
        ix1 = (x_indices+1).clip(0, x_steps-1).astype(int)
        iy1 = (y_indices+1).clip(0, y_steps-1).astype(int)
        t00 = transform[0][(x_indices, y_indices)]
        t01 = transform[0][(x_indices, iy1)]
        t10 = transform[0][(ix1, y_indices)]
        t11 = transform[0][(ix1, iy1)]
        transform_x = t00*x1*y1 + t01*x1*y_fracs + t10*x_fracs*y1 + t11*x_fracs*y_fracs
        t00 = transform[1][(x_indices, y_indices)]
        t01 = transform[1][(x_indices, iy1)]
        t10 = transform[1][(ix1, y_indices)]
        t11 = transform[1][(ix1, iy1)]
        transform_y = t00*x1*y1 + t01*x1*y_fracs + t10*x_fracs*y1 + t11*x_fracs*y_fracs
        transform = [transform_x, transform_y]
    return transform

_small = 1e-100
def _U(x):
    return (x**2) * np.where(x<_small, 0, np.log(x))

def _interpoint_distances(points):
    xd = np.subtract.outer(points[:,0], points[:,0])
    yd = np.subtract.outer(points[:,1], points[:,1])
    return np.sqrt(xd**2 + yd**2)

def _make_L_matrix(points):
    n = len(points)
    K = _U(_interpoint_distances(points))
    P = np.ones((n, 3))
    P[:,1:] = points
    O = np.zeros((3, 3))
    L = np.asarray(np.bmat([[K, P],[P.transpose(), O]]))
    return L

def _calculate_f(coeffs, points, x, y):
    w = coeffs[:-3]
    a1, ax, ay = coeffs[-3:]
    # The following uses too much RAM:
    # distances = _U(np.sqrt((points[:,0]-x[...,np.newaxis])**2 + (points[:,1]-y[...,np.newaxis])**2))
    # summation = (w * distances).sum(axis=-1)
    summation = np.zeros(x.shape)
    for wi, Pi in zip(w, points):
        summation += wi * _U(np.sqrt((x-Pi[0])**2 + (y-Pi[1])**2))
    return a1 + ax*x + ay*y + summation

def _make_warp(from_points, to_points, x_vals, y_vals):
    from_points, to_points = np.asarray(from_points), np.asarray(to_points)
    err = np.seterr(divide='ignore')
    L = _make_L_matrix(from_points)
    V = np.resize(to_points, (len(to_points)+3, 2))
    V[-3:, :] = 0
    coeffs = np.dot(np.linalg.pinv(L), V)
    x_warp = _calculate_f(coeffs[:,0], from_points, x_vals, y_vals)
    y_warp = _calculate_f(coeffs[:,1], from_points, x_vals, y_vals)
    np.seterr(**err)
    return [x_warp, y_warp]


#----------------------------------
#
#----------------------------------
def _get_regular_grid(image, points_per_dim):
    nrows, ncols = image.shape[0], image.shape[1]
    rows = np.linspace(0, nrows, points_per_dim)
    cols = np.linspace(0, ncols, points_per_dim)
    rows, cols = np.meshgrid(rows, cols)
    return np.dstack([cols.flat, rows.flat])[0]


def _generate_random_vectors(image, src_points, scale):
    dst_pts = src_points + np.random.uniform(-scale, scale, src_points.shape)
    return dst_pts


def _thin_plate_spline_warp(image, src_points, dst_points, keep_corners=True, interpolation_order = 1):
    width, height = image.shape[:2]
    if keep_corners:
        corner_points = np.array(
            [[0, 0], [0, width], [height, 0], [height, width]])
        src_points = np.concatenate((src_points, corner_points))
        dst_points = np.concatenate((dst_points, corner_points))

    """
    #print( "[_thin_plate_spline_warp] image.shape", image.shape )
    if( len(image.shape) == 3 ):
        #print( "[_thin_plate_spline_warp] np.moveaxis(image, 2, 0).shape", np.moveaxis(image, 2, 0).shape )
        out = warp_images( src_points, dst_points, np.moveaxis(image, 2, 0), (0, 0, width - 1, height - 1), interpolation_order = 1 )
        out = np.moveaxis(np.array(out), 0, 2)
    else:
        image = np.moveaxis(image, 1, 0).reshape(-1,image.shape[0],image.shape[1])
        #print( "[_thin_plate_spline_warp] image.shape", image.shape )
        out = warp_images( src_points, dst_points, image, (0, 0, width - 1, height - 1), interpolation_order = 0 )
        out = np.moveaxis(np.array(out), 0, 2).squeeze()
        #print( "out.shape : ", out.shape )
        #print( "[_thin_plate_spline_warp] out.shape", out.shape )
    """
    out = warp_images( src_points, dst_points, np.moveaxis(image, 2, 0), (0, 0, width - 1, height - 1), interpolation_order )
    out = np.moveaxis(np.array(out), 0, 2)
    return out


def tps_warp(image, points_per_dim, scale):
    width, height = image.shape[:2]
    src = _get_regular_grid(image, points_per_dim=points_per_dim)
    dst = _generate_random_vectors(image, src, scale=scale*width)
    out = _thin_plate_spline_warp(image, src, dst)
    return out

def tps_warp_2(image, dst, src, interpolation_order = 1):
    out = _thin_plate_spline_warp(image, src, dst, interpolation_order)
    return out

