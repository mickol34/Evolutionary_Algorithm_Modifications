import multiprocessing
import threading
import time
import typing

import numpy as np
from matplotlib import animation
import matplotlib.pyplot as plt



class DataVisualiser:
    # matplotlib components
    fig = None
    ax = None
    scatter = None
    x_axis, x_axis_temp = [], []
    y_axis, y_axis_temp = [], []
    z_axis, z_axis_temp = [], []

    # live plot components
    __anim: animation.FuncAnimation = None
    __process = None
    __process_started = threading.Event()
    __multiprocess = False
    __manager: multiprocessing.Manager = None
    __queue: multiprocessing.Queue = None
    __big_queue: multiprocessing.Queue = None
    __finished: threading.Event = threading.Event()
    __anim_sample_time = None
    __data_sample_time = None

    def __init__(self, plot_type="2D"):
        """
        Class to visualise 2D/3D data using matplotlib.
        Optionally, can be done dynamically (must be in separate process because of matplotlib limitations).

        Parameters
        ----------
        plot_type : str
            '2D' or '3D'
        """
        self.main_title = None
        self.x_limits = None
        self.y_limits = None
        self.z_limits = None
        self.data_color = None
        self.data_size = None
        self.plot_type = plot_type
        self.try_connect_scatter = False
        self.q_func = None

        if plot_type == "2D":
            self.projection = None  # plot mode (2D/3D)
        elif plot_type == "3D":
            self.projection = "3d"  # plot mode (2D/3D)
        else:
            raise Exception("Unknown plot type")

    def init_plot(self, main_title: str = "live_plot", q_func: typing.Callable = None,
                  q_domain: tuple[int, int] = (-100, 100), q_points: int = 50, q_alpha: float = 0.5,
                  x_limits: tuple = (None, None), y_limits: tuple = (None, None), z_limits: tuple = (None, None),
                  data: (list[tuple[float, float]] or list[tuple[float, float, float]] or dict[
                      tuple[float, float], float]) = None,
                  data_color: str="red", data_size: float = 1, try_connect_scatter=False, figsize: tuple = None):
        """
        Init matplotlib scatter plot (with optional pre-inserted data).

        Parameters
        ----------
        q_points
        q_domain
        q_func : TODO
        z_limits
        y_limits
        x_limits
        main_title
        data : list of 2D/3D tuples or dictionary with 2D tuple as keys and numeric as value, optional
            For 2D plotting, use list of 2D tuples.
            For 3D plotting, use list of 3D tuples or dict[(float, float) : float] for respecively x,y,z axis data.
            Plot of type 2D/3D raises an expception if user tries to add (opposite) 3D/2D data.

        Returns
        -------
        self
        """
        self.main_title = main_title
        self.x_limits = x_limits
        self.y_limits = y_limits
        self.z_limits = z_limits
        self.data_color = data_color
        self.data_size = data_size
        self.try_connect_scatter = try_connect_scatter
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(projection=self.projection)
        self.fig.canvas.mpl_connect('close_event', self.__on_exit)
        self.fig.suptitle(main_title, fontsize=14)

        # INITIALIZING WITH DATA (if given)
        self.__init_data(data)

        # SETTING AXES LIMITS (if given)
        self.__set_limits()

        # PLOTTING SURFACE (if given and if 3D plot)
        self.__surface_plot(function=q_func, domain=q_domain, points=q_points, alpha=q_alpha)

        # INITIALIZE LIVE PLOT (if chosen to)
        self.__init_live_plot()

        plt.show()
        return self

    def init_plot_multiprocess(self, anim_sample_time: float = 0.01, data_sample_time: float or None = 0.01, **kwargs):
        """
        Init matplotlib scatter plot (with optional pre-inserted data) in separate process.
        This allows user to later add new points to plot dynamically using `add_to_plot(...)` method.
        Keyword parameters are passed to `init_plot(...)` method!

        Parameters
        ----------
        anim_sample_time : float
            Sample time of animation.
        data_sample_time : float
            Sample time of checking multiprocess queue, None means instant.

        Returns
        -------
        self
        """

        if self.__process:  # not allowing to start multiprocess plot twice
            return None

        def __init__multiprocess():
            """
            Additional function to handle multiprocess communication. Run in separate thread!
            Waits for signal to cut off communication with separate plot process (see `join(...)` method)
            Reason for creating this function:
                - Queues work very bad without multiprocessing Manager.
                - multiprocess.Process must be handled by Context Manager because of being (non `picklable`) `weakref`
                                              (I don't know yet what that really means xd (but it works well so far))
            """
            with multiprocessing.Manager() as manager:
                self.__queue = manager.Queue()
                self.__big_queue = manager.Queue()
                self.__process = multiprocessing.Process(target=self.init_plot, kwargs={**kwargs})
                self.__process.start()  # starting process with multiprocess manager -> its joinable!
                self.__process_started.set()
                self.__finished.wait()  # waiting for signal to end communication with process

        self.__data_sample_time = data_sample_time
        self.__anim_sample_time = anim_sample_time
        threading.Thread(target=__init__multiprocess, daemon=False).start()
        time.sleep(2.0)
        self.__multiprocess = True
        return self

    def add_point(self, data_point: tuple[float, float] or tuple[float, float, float]):
        """
        Adds one 2D/3D point to plot.
        Method to be used with plot initialised in separate process (using `init_plot_multiprocess(...)` method).
        If plot was not initialised (as multiprocess), this method will do nothing.

        Parameters
        ----------
        data_point: 2D/3D tuple of floats representing 2D/3D point in space
            If plot was not previously initialised with data, its dimension will be now defined (2D/3D).
            If plot was previously initialised (is defined as 2D/3D plot), passing 2D data to 3D plot and vice versa
            will raise an Exception.
        """
        if self.__process:
            self.__queue.put(data_point)

    def set_data(self, data: (list[tuple[float, float]] or list[tuple[float, float, float]] or
                              dict[tuple[float, float], float]) = None):
        """
        Sets new data for the plot.
        Method to be used with plot initialised in separate process (using `init_plot_multiprocess(...)` method).
        If plot was not initialised (as multiprocess), this method will do nothing.

        Parameters
        ----------
        data : list of 2D/3D tuples or dictionary with 2D tuple as keys and numeric as value, optional
            For 2D plotting, use list of 2D tuples.
            For 3D plotting, use list of 3D tuples or dict[(float, float) : float] for respecively x,y,z axis data.
            Plot initialised as 2D/3D raises an expception if `data` arg is (opposite) 3D/2D data.
        """
        if self.__process:
            self.__queue.put("__set_data")  # signal to check big queue
            self.__big_queue.put(data)

    def join(self):
        """
        Method to be used with live plotting running in a separate process.
        Makes main thread wait for live plotting to finish (for user to close matplotplib window).
        Should be run at the end of algorithm.
        """
        if self.__multiprocess:
            if not self.__process_started.is_set():
                self.__process_started.wait()
        if self.__process:
            self.__process.join()
            self.__finished.set()


    def set_data_color(self, c: str = "red"):
        """
        Sets color of future data.

        Parameters
        ----------
        c: color value in format accepted by matplotlib
        """
        self.data_color = c

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.join()

    # PRIVATE METHODS
    def __surface_plot(self, function: typing.Callable, domain=(-100, 100), points=30, alpha=0.5):
        if not function:
            return None
        if self.plot_type != "3D":
            raise Exception("Surface plot can be added only to 3D plot type")
        if not self.ax:
            raise Exception("Plot not initialised!")

        xys = np.linspace(domain[0], domain[1], points)
        xys = np.transpose([np.tile(xys, len(xys)), np.repeat(xys, len(xys))])
        zs = np.zeros(points * points)

        for i in range(0, xys.shape[0]):
            zs[i] = function(xys[i])
        x = xys[:, 0].reshape((points, points))
        y = xys[:, 1].reshape((points, points))
        z = zs.reshape((points, points))

        self.ax.plot_surface(x, y, z, cmap='gist_ncar', edgecolor='none', alpha=alpha)

    def __verify_data_type(self, data: (list[tuple[float, float]] or list[tuple[float, float, float]] or
                                        dict[tuple[float, float], float])):

        if (isinstance(data, dict) or len(data[0]) == 3) and self.plot_type != "3D":
            raise Exception(f"Wrong type of data [3D] for a plot of type: [{self.plot_type}]")

        elif (isinstance(data, list) and len(data[0]) == 2) and self.plot_type != "2D":
            raise Exception(f"Wrong type of data [2D] for a plot of type: [{self.plot_type}]")

    def __verify_datapoint_type(self, data_point: tuple[float, float] or tuple[float, float, float]):

        if len(data_point) == 3 and self.plot_type != "3D":
            raise Exception(f"Wrong type of datapoint [3D] for a plot of type: [{self.plot_type}]")

        elif len(data_point) == 2 and self.plot_type != "2D":
            raise Exception(f"Wrong type of datapoint [2D] for a plot of type: [{self.plot_type}]")

    def __init_data(self, data: (list[tuple[float, float]] or list[tuple[float, float, float]] or
                                 dict[tuple[float, float], float]) = None):
        if data:
            self.__verify_data_type(data)
            for data_point in data:
                self.x_axis.append(data_point[0]), self.y_axis.append(data_point[1])
                if isinstance(data, dict):
                    self.z_axis.append(data[data_point])
                elif len(data_point) == 3:
                    self.z_axis.append(data_point[2])

        if self.z_axis:
            self.scatter = self.ax.scatter(self.x_axis, self.y_axis, self.z_axis, c=self.data_color, s=self.data_size)
        else:
            self.scatter = self.ax.scatter(self.x_axis, self.y_axis, c=self.data_color, s=self.data_size)
            if self.try_connect_scatter:
                self.ax.plot(self.x_axis, self.y_axis, c=self.data_color)

    def __set_limits(self):
        if self.x_limits[0] is not None and self.x_limits[1] is not None:
            self.ax.set_xlim(self.x_limits)
        if self.y_limits[0] is not None and self.y_limits[1] is not None:
            self.ax.set_ylim(self.y_limits)
        if self.z_limits[0] is not None and self.z_limits[1] is not None and self.plot_type == "3D":
            self.ax.set_zlim(self.z_limits)

    # PRIVATE METHODS - LIVE PLOTTING
    def __queue_handler(self):
        while not self.__finished.is_set():

            data = self.__queue.get()
            if not data:
                break
            elif data == "__set_data":
                big_data = self.__big_queue.get()
                self.__set_data(big_data)
            else:
                self.__add_to_data(data)
            if self.__data_sample_time:
                self.__finished.wait(self.__data_sample_time)
        plt.close()
        return

    def __set_data(self, data: (list[tuple[float, float]] or list[tuple[float, float, float]] or
                                dict[tuple[float, float], float] or None)):
        self.__verify_data_type(data)
        x_axis, y_axis, z_axis = [], [], []
        for data_point in data:
            if len(data_point) == 3:
                z_axis.append(data_point[2])
            else:
                if isinstance(data, dict):
                    z_axis.append(data[data_point])

            x_axis.append(data_point[0])
            y_axis.append(data_point[1])
        self.x_axis, self.y_axis, self.z_axis = x_axis, y_axis, z_axis

    def __add_to_data(self, data_point: tuple[float, float] or tuple[float, float, float]):
        self.__verify_datapoint_type(data_point)

        self.x_axis.append(data_point[0])
        self.y_axis.append(data_point[1])
        if len(data_point) == 3:
            self.z_axis.append(data_point[2])

    def __init_live_plot(self):
        if self.__process:
            self.__finished = threading.Event()
            self.__anim = animation.FuncAnimation(self.fig, self.__live_plot, blit=True,
                                                  interval=self.__anim_sample_time * 1000)
            thread = threading.Thread(target=self.__queue_handler, daemon=True)
            thread.start()

    def __live_plot(self, frame=None):
        if self.x_axis_temp != self.x_axis or self.y_axis_temp != self.y_axis or self.z_axis_temp != self.z_axis:
            if self.z_axis:
                self.scatter = self.ax.scatter(self.x_axis, self.y_axis, self.z_axis, c=self.data_color, s=self.data_size)
            else:
                self.scatter = self.ax.scatter(self.x_axis, self.y_axis, c=self.data_color, s=self.data_size)
            self.fig.canvas.draw()
            self.x_axis_temp, self.y_axis_temp, self.z_axis_temp = self.x_axis, self.y_axis, self.z_axis

        return self.scatter,

    def __on_exit(self, *args):
        if self.__process:
            self.__finished.set()


if __name__ == "__main__":
    pass
