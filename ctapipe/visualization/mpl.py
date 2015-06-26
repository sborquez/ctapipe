"""
Visualization routines using MatPlotLib
"""

from matplotlib import pyplot as plt
from matplotlib import transforms
from matplotlib.collections import RegularPolyCollection
from matplotlib.patches import Ellipse
import numpy as np

__all__ = ['CameraDisplay']


class CameraDisplay(object):

    """Camera Display using MatPlotLib

    Parameters
    ----------

    geometry : `~ctapipe.io.CameraGeometry`
        Definition of the Camera/Image
    axis : `matplotlib.axes._subplots.AxesSubplot`
        a MatPlotLib Axis object to plot on, or None to create a new one

    Implementation Details:
    -----------------------

    Pixels are rendered as a
    `matplotlib.collections.RegularPolyCollection`, which is the most
    efficient way in MatPlotLib to display complex pixel shapes.

    """

    def __init__(self, geometry, axes=None, title="Camera"):
        self.axes = axes if axes is not None else plt.gca()
        self.geom = geometry
        self.polys = None
        self.cmap = plt.cm.jet

        # initialize the plot and generate the pixels as a
        # RegularPolyCollection

        xx, yy, rr = (self.geom.pix_x.value, self.geom.pix_y.value,
                      self.geom.pix_r.data)
        offsets = list(zip(xx, yy))

        offset_trans = self.axes.transData
        trans = self.axes.transData
        fig = self.axes.get_figure()
        trans = fig.dpi_scale_trans + transforms.Affine2D().scale(1.0 / 72.0)
        self.axes.set_aspect('equal', 'datalim')

        if self.geom.pix_type == 'hexagonal':
            self.polys = RegularPolyCollection(numsides=6,
                                               rotation=np.radians(0),
                                               offsets=offsets,
                                               sizes=self._radius_to_size(rr),
                                               transOffset=offset_trans)
            self.polys.set_cmap(plt.cm.jet)
            self.polys.set_linewidth(0)
            self.polys.set_array(np.zeros_like(self.geom.pix_x))
            self.polys.set_transform(trans)
            self.axes.add_collection(self.polys, autolim=True)
        else:
            raise ValueError(
                "Unimplemented pixel type: {}", self.geom.pix_type)

        self.axes.set_title(title)
        self.axes.set_xlabel("X position ({})".format(self.geom.pix_x.unit))
        self.axes.set_ylabel("Y position ({})".format(self.geom.pix_y.unit))
        self.axes.autoscale_view()

    def _radius_to_size(self, radii):
        """compute radius in screen coordinates and returns the size in
        points^2, needed for the size parameter of
        RegularPolyCollection. This may not be needed if the
        transormations are set up correctly

        """

        rr = radii.ravel()
        center = np.zeros([len(rr), 2])
        offset = np.column_stack([center[:, 0], rr])

        offset_pix = (self.axes.transData.transform(center)
                      - self.axes.transData.transform(offset))
        rad_pix = offset_pix[:, 1]
        rad_pix.shape = radii.shape
        return (np.pi * rad_pix ** 2) / 2.0

    def draw_image(self, image):
        """
        Change the image displayed on the Camera. 

        Parameters
        ----------
        image: array_like
            array of values corresponding to the pixels in the CameraGeometry.
        """

        self.polys.set_array(image)
        plt.draw()  # is there a better way to update this?

    def add_moment_ellipse(self, centroid, length, width , phi, assymmetry=0.0,
                            **kwargs):
        """
        plot an ellipse on top of the camera

        Parameters
        ----------
        centroid: (float,float)
            position of centroid
        length: float
            major axis
        width: float
            minor axis
        phi: float
            rotation angle wrt "up", clockwise, in radians
        assymmetry: float
            3rd-order moment for directionality if known
        kwargs: 
            any MatPlotLib style arguments to pass to the Ellipse patch
        
        TODO:
        -----
        - Check consistency of phi angle

        """
        ellipse = Ellipse(xy=centroid, width=width, height=length,
                          angle=np.degrees(phi), fill=False, **kwargs)
        self.axes.add_patch(ellipse)
        plt.draw()
        return ellipse

