"""Container module for the new cubic spline classes.

Authors:
--------
- Atsushi Sakai (@Atsushi_twi) (author of the original code)
- Paulo Sanchez (@erlete) (author of the modified code)
"""


import bisect
import math

import numpy as np
from matplotlib import pyplot as plt

from bidimensional.coordinates import Coordinate


class Spline:
    """Main class. Represents a cubic spline.

    Parameters:
    -----------
    - x: 1d array of x values.
    - y: 1d array of y values.

    Notes:
    ------
    - The number of x and y values must be the same.

    Notes about mathematical implementations:
    -----------------------------------------
    - Since the spline is a cubic function composite, each segment is defined
        by a polynomial function of the form f(x) = a*x^3 + b*x^2 + c*x + d.
    - A property of said polynomial function is that, at x = x_n, f(x) = y_n
        and at x = x_(n + 1), f(x) = y_(n + 1), g(x) = y_(n + 1). This means
        that the images of each pair of segments, given a boundary point, are
        the same.
    - Another property is that the second and third derivatives of a given
        spline segment have the same images at the boundary points as well.
    """

    def __init__(self, x, y):
        self.x, self.y = x, y

        # Determine the dimension of the X-axis.
        self.x_dim = len(x)

        # Compute the differences between the x-coordinates:
        #   https://www.pythonpool.com/numpy-diff/
        x_diff = np.diff(x)

        # Compute coefficient d:
        self.d = np.array(y)

        # Compute the difference between d coefficients:
        d_diff = np.diff(self.d)

        # Compute coefficient b:
        self.b = np.linalg.solve(
            self.__calc_matrix_a(x_diff), self.__calc_matrix_b(x_diff)
        )

        # Compute the difference between b coefficients:
        b_diff = np.diff(self.b)

        # Compute coefficient c:
        self.c = np.array(
            [
                (d_diff[i]) / x_diff[i]
                - x_diff[i] * (self.b[i + 1] + 2.0 * self.b[i]) / 3.0
                for i in range(self.x_dim - 1)
            ]
        )

        # Compute coefficient a:
        self.a = [b_diff[i] / (3.0 * x_diff[i]) for i in range(self.x_dim - 1)]

    def position(self, x):
        """Computes the image of a given x-value in a spline section.

        Notes:
        ------
        - The form of the function is: f(x) = a*x^3 + b*x^2 + c*x + d.
        - If x is outside of the X-range, the output is None.
        """

        # Out of bounds handling:
        if not self.x[0] <= x <= self.x[-1]:
            return None

        i = self.__search_index(x)
        dx = x - self.x[i]

        return (
            self.a[i] * dx**3.0
            + self.b[i] * dx**2.0
            + self.c[i] * dx
            + self.d[i]
        )

    def first_derivative(self, x):
        """Computes the first derivative image

        Notes:
        ------
        - The first derivative is a polynomial function of the form
            f'(x) = 3*a*x^2 + 2*b*x + c.
        - If x is outside of the X-range, the output is None.
        """

        # Out of bounds handling:
        if not self.x[0] <= x <= self.x[-1]:
            return None

        i = self.__search_index(x)
        dx = x - self.x[i]

        return (
            3.0 * self.a[i] * dx**2.0
            + 2.0 * self.b[i] * dx
            + self.c[i]
        )

    def second_derivative(self, x):
        """Computes the first derivative of a given spline section.

        Notes:
        ------
        - The second derivative is a polynomial function of the form
            f''(x) = 6*a*x + 2*b.
        - If x is outside of the X-range, the output is None.
        """

        # Out of bounds handling:
        if not self.x[0] <= x <= self.x[-1]:
            return None

        i = self.__search_index(x)
        dx = x - self.x[i]

        return (
            6.0 * self.a[i] * dx
            + 2.0 * self.b[i]
        )

    def __calc_matrix_a(self, diff):
        """Computes the A matrix for the spline coefficient b."""

        matrix = np.zeros((self.x_dim, self.x_dim))
        matrix[0, 0] = 1.0

        for i in range(self.x_dim - 1):
            if i != (self.x_dim - 2):
                matrix[i + 1, i + 1] = 2.0 * (diff[i] + diff[i + 1])

            matrix[i + 1, i] = diff[i]
            matrix[i, i + 1] = diff[i]

        matrix[0, 1] = 0.0
        matrix[self.x_dim - 1, self.x_dim - 2] = 0.0
        matrix[self.x_dim - 1, self.x_dim - 1] = 1.0

        return matrix

    def __calc_matrix_b(self, diff):
        """Computes the B matrix for the spline coefficient b."""

        matrix = np.zeros(self.x_dim)

        for i in range(self.x_dim - 2):
            matrix[i + 1] = (
                3.0 * (self.d[i + 2] - self.d[i + 1]) / diff[i + 1]
                - 3.0 * (self.d[i + 1] - self.d[i]) / diff[i]
            )

        return matrix

    def __search_index(self, x):
        """Searches the index of the spline section that contains the given
        x-value.
        """

        return bisect.bisect(self.x, x) - 1


class Spline2DBase:
    """Container class for Spline2D class base structure.

    Provides a base structure for the Spline2D class, allowing separate
    definition of its class constants and getter and setter methods, as well
    as double underscore or magic methods.
    """

    # Class-wide constants:

    STD_SHAPES = {
        "point": 'x',
        "line": '-'
    }

    STD_STYLES = {
        "color": "black",
        "lw": 1.5
    }

    # Getter and setter methods:

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, (list, tuple, np.array)):
            raise TypeError("x must be a list, tuple or numpy array.")
        elif not all(isinstance(val, (int, float)) for val in value):
            raise TypeError("x must contain only numbers.")
        else:
            self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, (list, tuple, np.array)):
            raise TypeError("y must be a list, tuple or numpy array.")
        elif not all(isinstance(val, (int, float)) for val in value):
            raise TypeError("y must contain only numbers.")
        else:
            self._y = value

    @property
    def generation_step(self):
        return self._generation_step

    @generation_step.setter
    def generation_step(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("generation_step must be a number.")
        elif value <= 0:
            raise ValueError("generation_step must be greater than 0.")
        else:
            self._generation_step = value

    @property
    def knots(self):
        return self._knots

    @property
    def positions(self):
        return self._positions

    @property
    def curvature(self):
        return self._curvature

    @property
    def yaw(self):
        return self._yaw

    # Double underscore (magic) methods:

    def __str__(self):
        return f"""
Spline2D(
    x = {self.x},
    y = {self.y},
    generation_step = {self.generation_step},
)
"""

    def __len__(self):
        return len(self.positions)


class Spline2D(Spline2DBase):
    """Represents a two-dimensional cubic spline.

    Parameters:
    -----------
    - x: 1D array
        The x-coordinates of the spline.
    - y: 1D array
        The y-coordinates of the spline.
    - generation_step: float
        The step size used to generate the spline.

    Notes:
    ------
    - The number of x and y values must be the same.
    - The value used for the generation step must not be negative not zero.
    """

    def __init__(self, x, y, generation_step=.1):
        self._x, self._y = x, y
        self._knots = self._compute_knots(x, y)
        self._spline_x = Spline(self._knots, x)
        self._spline_y = Spline(self._knots, y)
        self._generation_step = generation_step
        self._positions, self._curvature, self._yaw = self._compute_results()

    def _compute_knots(self, x, y):
        """Computes the knots of the spline."""

        return [0] + list(np.cumsum(np.hypot(np.diff(x), np.diff(y))))

    def _compute_position(self, i):
        """Computes the image of a given x-value in a spline section.

        Notes:
        ------
        - If x is outside of the X-range, the output is None.
        """

        return self._spline_x.position(i), self._spline_y.position(i)

    def _compute_curvature(self, i):
        """Computes the curvature of a given spline section.

        Notes:
        ------
        - If x is outside of the X-range, the output is None.
        """

        # This dictionary allows fast value checking:
        derivatives = {
            'x1': self._spline_x.first_derivative(i),
            'x2': self._spline_x.second_derivative(i),
            'y1': self._spline_y.first_derivative(i),
            'y2': self._spline_y.second_derivative(i)
        }

        return (
            derivatives["y2"] * derivatives["x1"]
            - derivatives["x2"] * derivatives["y1"]
        ) / ((derivatives["x1"]**2 + derivatives["y1"]**2) ** (3 / 2))

    def _compute_yaw(self, i):
        """Computes the yaw of a given spline section.

        Notes:
        ------
        - If x is outside of the X-range, the output is None.
        """

        return math.atan2(
            self._spline_y.first_derivative(i),
            self._spline_x.first_derivative(i)
        )

    def _compute_results(self):
        """Computes the coordinates, curvature and yaw of the spline."""

        positions, curvature, yaw = [], [], []

        for i in np.arange(self._knots[0], self._knots[-1], self._generation_step):
            positions.append(Coordinate(*self._compute_position(i)))
            curvature.append(self._compute_curvature(i))
            yaw.append(self._compute_yaw(i))

        return positions, curvature, yaw

    def plot_input(self, *args, ax=None, **kwargs):
        """Plots the input of the spline."""

        styles = self.STD_STYLES.copy()
        styles.update({"label": "Input"})
        styles.update(kwargs)
        shape = args[0] if args else self.STD_SHAPES["point"]

        ax = plt.gca() if ax is None else ax

        title = ax.get_title()
        x_label = "X [m]"
        x_label = "Undefined" if x_label != ax.get_xlabel() != '' else x_label
        y_label = "Y [m]"
        y_label = "Undefined" if y_label != ax.get_ylabel() != '' else y_label

        ax.set_title(f"{(title + ', ') if title else ''}Input data")
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        ax.plot(self._x, self._y, shape, **styles)

    def plot_positions(self, *args, ax=None, **kwargs):
        """Plots the spline."""

        styles = self.STD_STYLES.copy()
        styles.update({"label": "Spline"})
        styles.update(kwargs)
        shape = args[0] if args else self.STD_SHAPES["line"]

        ax = plt.gca() if ax is None else ax

        title = ax.get_title()
        x_label = "X [m]"
        x_label = "Undefined" if x_label != ax.get_xlabel() != '' else x_label
        y_label = "Y [m]"
        y_label = "Undefined" if y_label != ax.get_ylabel() != '' else y_label

        ax.set_title(f"{(title + ', ') if title else ''}Spline interpolation")
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        ax.plot(*zip(*self._positions), shape, **styles)

    def plot_curvature(self, *args, ax=None, **kwargs):
        """Plots the curvature function of the spline."""

        styles = self.STD_STYLES.copy()
        styles.update({"label": "Curvature"})
        styles.update(kwargs)
        shape = args[0] if args else self.STD_SHAPES["line"]

        ax = plt.gca() if ax is None else ax

        title = ax.get_title()
        x_label = "Line length [m]"
        x_label = "Undefined" if x_label != ax.get_xlabel() != '' else x_label
        y_label = "Curvature [1/m]"
        y_label = "Undefined" if y_label != ax.get_ylabel() != '' else y_label

        ax.set_title(f"{(title + ', ') if title else ''}Spline curvature")
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        ax.plot(
            np.arange(self._knots[0],
                      self._knots[-1],
                      self._generation_step
                      ),
            self._curvature, shape, **styles
        )

    def plot_yaw(self, *args, ax=None, **kwargs):
        """Plots the YAW function of the spline."""

        styles = self.STD_STYLES.copy()
        styles.update({"label": "YAW"})
        styles.update(kwargs)
        shape = args[0] if args else self.STD_SHAPES["line"]

        ax = plt.gca() if ax is None else ax

        title = ax.get_title()
        x_label = "Line length [m]"
        x_label = "Undefined" if x_label != ax.get_xlabel() != '' else x_label
        y_label = "YAW angle [deg]"
        y_label = "Undefined" if y_label != ax.get_ylabel() != '' else y_label

        ax.set_title(f"{(title + ', ') if title else ''}Spline YAW")
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        ax.plot(
            np.arange(self._knots[0],
                      self._knots[-1],
                      self._generation_step
                      ),
            self._yaw, shape, **styles
        )
