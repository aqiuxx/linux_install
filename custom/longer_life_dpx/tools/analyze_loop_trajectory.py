"""
建图检测到回环, 根据保存的轨迹数据分析其原因
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import argparse, logging, coloredlogs, datetime, shutil
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d


class InfoOdo:
    def __init__(self) -> None:
        self.timestamp: np.ndarray = None  # timestamp, Nx1, [ms]
        self.pos: np.ndarray = None  # position, [x, y, z], Nx3, [m]
        self.angle: np.ndarray = None  # euler angle, [yaw, pitch, roll], Nx3, [rad]


class Analyzer:
    def __init__(self, odo_file: Path) -> None:
        self.odo_file: Path = odo_file.resolve()  # odo file
        self.odo: InfoOdo = None

        # plot settings
        self.__figsize = (15, 12)
        self.__colors = ['b', 'r', 'k', 'm']
        self.__labels = ['X', 'Y', 'Z', 'All']
        self.__angle_labels = ['Yaw', 'Pitch', 'Roll']

    def run(self) -> None:
        self.__load_odo()

        self.__plot_odo()

        plt.show(block=True)

    def __load_odo(self) -> None:
        """load odo data from file"""
        logging.info(f'load info odo from file: {self.odo_file}')
        raw = np.loadtxt(self.odo_file, delimiter=',', skiprows=1)
        self.odo = InfoOdo()
        self.odo.timestamp = raw[:, 0]  # ms
        self.odo.pos = raw[:, 1:4]  # m
        # NOTE without roll currently
        self.odo.angle = raw[:, 4:]  # rad

    def __plot_odo(self) -> None:
        # 3D trajectory
        fig = plt.figure(f'Trajectory', figsize=self.__figsize)
        ax = fig.add_subplot(projection='3d')
        ax.plot(self.odo.pos[:, 0], self.odo.pos[:, 1], self.odo.pos[:, 2], 'b.')
        ax.set_xlabel('X [m]')
        ax.set_ylabel('Y [m]')
        ax.set_zlabel('Z [m]')
        ax.set_title('Trajectory')
        ax.grid(True)
        # ax.set_box_aspect(aspect=(1, 1, 1)) # fail
        # ax.set_aspect('equal') # OK
        # set axis range, [1,1,5]
        z_scale = 5
        x_limits, y_limits, z_limits = ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()
        x_range, x_middle = abs(x_limits[1] - x_limits[0]), np.mean(x_limits)
        y_range, y_middle = abs(y_limits[1] - y_limits[0]), np.mean(y_limits)
        z_range, z_middle = abs(z_limits[1] - z_limits[0]), np.mean(z_limits)
        plot_range = 0.5 * max([x_range, y_range, z_scale * z_range])  # aspect [1,1,5]
        ax.set_xlim3d([x_middle - plot_range, x_middle + plot_range])
        ax.set_ylim3d([y_middle - plot_range, y_middle + plot_range])
        ax.set_zlim3d([z_middle - plot_range / z_scale, z_middle + plot_range / z_scale])
        fig.tight_layout()

        # position, t - pos
        fig = plt.figure('Position', figsize=self.__figsize)
        axes = fig.subplots(3, 2, sharex=True)
        axes1, axes2 = [v[0] for v in axes], [v[1] for v in axes]
        timestamp = self.odo.timestamp * 1e-3
        # pos
        for i in range(3):
            axes1[i].plot(timestamp, self.odo.pos[:, i], f'.-{self.__colors[i]}', label=self.__labels[i])
            axes1[i].set_xlabel('Timestamp [s]')
            axes1[i].set_ylabel('Position [m]')
            axes1[i].set_title(f'Position - {self.__labels[i]}')
            axes1[i].grid()
            axes1[i].legend()
        # euler angle
        for i in range(2):
            axes2[i].plot(
                timestamp, self.odo.angle[:, i] * 180 / np.pi, f'.-{self.__colors[i]}', label=self.__labels[i]
            )
            axes2[i].set_xlabel('Timestamp [s]')
            axes2[i].set_ylabel('Angle [deg]')
            axes2[i].set_title(f'Angle - {self.__angle_labels[i]}')
            axes2[i].grid()
            axes2[i].legend()

        fig.tight_layout()


if __name__ == '__main__':
    # argument parser
    parser = argparse.ArgumentParser(
        description='Loop Trajectory Analyzer',
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40, width=120),
    )
    parser.add_argument('odo_file', default='./InfoOdos.csv', help='Info odo file (default: %(default)s)')
    args = parser.parse_args()
    print(args)

    # config logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                f"/tmp/{Path(__file__).stem}.{datetime.datetime.now().strftime('%Y%m%d-%H%M%S.%f')}.log"
            ),
        ],
    )
    coloredlogs.install(fmt="[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s")

    analyzer = Analyzer(Path(args.odo_file))
    analyzer.run()
