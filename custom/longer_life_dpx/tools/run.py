#!/usr/bin/python3
"""
Workflow for Run Whole Process in x86
"""

import os, argparse, logging, coloredlogs
import datetime, time, re, shutil
import signal, subprocess, psutil
from pathlib import Path
import json, yaml, pickle
from enum import Enum
from typing import Tuple, List, Dict, Union

try:
    import matplotlib.pyplot as plt

    enable_plot = True
except ImportError:
    logging.error('disable plot because cannot found matplotlib, try to install using "pip3 install matplotlib"')
    enable_plot = False


class ModuleType(Enum):
    BolePack = 1
    Mapping = 2
    Loc = 3


class ModuleConfig:
    def __init__(
        self, type: ModuleType, app: str, real_app: str, arguments: List[str] = [], work_folder: Path = None
    ) -> None:
        """
        NOTE: please note the difference between app and real app. Real app is the real, and truth application which do
        the process or work, while app is the application to start the program, it could be the same as real app, but
        at the most time, it is some script to load the library path and setting environment before starting program.
        For example, the app is `ndm_envmodel_run.sh`, while app is `ndm_envmodel`,
        """
        self.type: ModuleType = None  # module type
        self.app: str = app  # app name
        self.real_app: str = real_app  # real app name
        self.arguments: List[str] = arguments  # arguments
        self.work_folder: Path = work_folder.resolve()  # work folder


class PackType(Enum):
    ADAS = 1
    IMU = 2
    GNSS = 3
    ODO = 4
    MAPREC = 5
    PERREC = 6
    ODO3D = 7

    def type(self) -> str:
        """get the message type"""
        if self in (self.ADAS, self.MAPREC, self.PERREC):
            return 'frame'
        else:
            return 'msgs'

    def participant(self) -> int:
        """get the participant ID for communication"""
        return self.value - 1


class PackFillBackConfig:
    """config for bolepack to send pack data"""

    def __init__(
        self,
        pack_type: PackType,
        prefix_end_candidates: List[Tuple[str, str]],
        domain_id: int = -1,
        msg: List = [],
        mode: int = 0,
        ts_type: int = 0,
    ) -> None:
        self.pack_type: PackType = pack_type  # pack type
        # candidates list of prefix and ends for pack file
        self.prefix_end_candidates: List[Tuple[str, str]] = prefix_end_candidates

        # fglobal.json setting
        self.prefix: str = None  # prefix
        self.participant: int = self.pack_type.participant()  # communication participant
        self.channel: int = None  # channel'
        self.domain_id: int = domain_id  # domain ID
        self.type: str = self.pack_type.type()  # frame/msgs
        self.msgs: List = msg  # msg
        self.mode: int = mode  # mode, 0: pub/sub, 1: req/rep
        self.ts_type: int = ts_type  # ts type, 0: gen ts, 1: done ts

    def __str__(self) -> str:
        return (
            f'type: {self.pack_type.name:<8}, prefix: {self.prefix:<8}, channel: {self.channel:<3}'
            f', participant: {self.participant:<3}'
        )

    def is_valid(self) -> bool:
        return self.prefix is not None and self.channel is not None

    def target_options(self) -> Dict:
        return {
            'prefix': self.prefix,
            'participant': self.participant,
            'channel': self.channel,
            'domain_id': self.domain_id,
            'type': self.type,
            'msgs': self.msgs,
            'mode_comment': '0-pubsub, 1-reqrep',
            'mode': self.mode,
            'ts_type_comment': '0-GenTS, 1-DoneTs',
            'ts_type': self.ts_type,
        }

    def set_prefix_channel(self, data_folder: Path) -> bool:
        """
        set the prefix and channel for this pack

        Args:
            data_folder (Path): data folder

        Returns:
            bool: True if find correct prefix and channel, otherwise return false
        """
        for prefix, ends in self.prefix_end_candidates:
            for file in data_folder.iterdir():
                if file.is_file() and file.name.startswith(prefix + '_') and file.name.endswith(ends):
                    self.prefix = prefix
                    self.channel = int(re.search(r'_(\d+)\.pack$', file.name).group(1))
                    return True
        return False


class BolePackConfigModifier:
    """
    Modifier for bole pack config(fglobal.json, etc)
    """

    def __init__(self, pack_folder: Path, app_folder: Path) -> None:
        self.pack_folder: Path = pack_folder  # pack folder
        self.app_folder: Path = app_folder.resolve()  # app folder

        # pack fill back config
        self.__pack_configs = [
            # PackFillBackConfig(PackType.ADAS, [("ADAS", '5.pack')], -1),
            PackFillBackConfig(PackType.IMU, [("ASM330#", ".pack"), ("IMU", ".pack"), ("IMU#", ".pack")], 0),
            PackFillBackConfig(
                PackType.GNSS, [("F9P#", ".pack"), ("UB482#", ".pack"), ("F9Kgnss#", ".pack"), ("gnss#", ".pack")], 0
            ),
            PackFillBackConfig(PackType.ODO, [("ODO#", ".pack")], 0),
            PackFillBackConfig(
                PackType.MAPREC, [("MAPREC", "2.pack"), ("MAPREC", ".pack"), ("MAPRECBEV", ".pack")], -1
            ),
            PackFillBackConfig(
                PackType.PERREC, [("PERREC", "2.pack"), ("PERREC", ".pack"), ("PERRECBEVBR", ".pack")], -1
            ),
            PackFillBackConfig(PackType.ODO3D, [("ODO3D#", ".pack")], 0),
        ]

    def modify(self, speed=1.0) -> bool:
        """
        check and modify the bolepack config

        Args:
            speed (float, optional): fill back speed. Defaults to 1.0.

        Returns:
            bool: True if modify correct, otherwise return False
        """
        # check pack folder exist
        if not self.pack_folder.exists():
            logging.error(f"input pack folder don't exist: {self.pack_folder}")
            return False

        # check config exist
        fglobal_path = self.app_folder / 'config/fglobal.json'
        if not fglobal_path.exists():
            logging.error(f"cannot find fglobal.json file: {fglobal_path}")
            return False

        # log input
        # logging.info(f'fill back pack folder: {self.pack_folder}')
        logging.info(f'fglobal.json file: {fglobal_path}')

        # modify fglobal.json
        return self.__modify_fglobal(fglobal_path, speed=speed)

    def __modify_fglobal(self, fglobal_path: Path, speed: float) -> bool:
        """
        modify fglobal.json file
        """
        # set prefix and channel for each pack config
        for v in self.__pack_configs.copy():
            ret = v.set_prefix_channel(self.pack_folder)
            if ret:
                logging.info(v)
            else:
                if v.pack_type != PackType.ADAS and v.pack_type != PackType.ODO3D:
                    logging.fatal(f'cannot found suitable pack for {v.pack_type}')
                    return False
                else:
                    logging.warning(f'cannot found suitable pack for {v.pack_type}')
                    self.__pack_configs.remove(v)

        # read data from fglobal.json file
        with open(fglobal_path, 'r') as fs:
            data = json.load(fs)

        # file path
        data['Fillback']['file_paths'] = [str(self.pack_folder)]

        # without loop
        data['Fillback']['Loop']['is_open'] = 0

        # set speed
        logging.info(f'fill back speed: {speed:.3f}')
        data['Fillback']['controller']['machineclock']['speed'] = speed

        # set target
        data['Fillback']['target_options'] = []

        # set target options
        data['Fillback']['target_options'] = [v.target_options() for v in self.__pack_configs]

        # save to file
        with open(fglobal_path, 'w') as fs:
            json.dump(data, fs, indent=2)

        return True


class MappingConfigModifier:
    """
    Modifier for mapping config(communication.json, config_park.yaml etc)
    """

    def __init__(self, app_folder: Path) -> None:
        self.app_folder: Path = app_folder.resolve()  # app folder

    def modify(
        self,
        use_internal_odo3d=True,
        use_maprec_line=True,
        auto_trigger_start=False,
        auto_trigger_save=True,
        auto_trigger_save_timestamp=0,
    ) -> bool:
        """
        check and modify the config

        Args:
            auto_trigger start (bool, optional): whether to auto trigger start command of loc map manager. Defaults to False.
            auto_trigger save (bool, optional): whether to auto trigger save command of loc map manager. Defaults to True.

        Returns:
            bool: True if modify correct, otherwise return False
        """
        # check config exist
        config_path = self.app_folder / 'config/config_full_pack.yaml'
        if not config_path.exists():
            logging.error(f"cannot find config file: {config_path}")
            return False
        logging.info(f'config file: {config_path}')

        # don't modify communication.json

        # modify config_park.yaml
        self.__modify_config(
            config_path,
            use_internal_odo3d=use_internal_odo3d,
            use_maprec_line=use_maprec_line,
            auto_trigger_start=auto_trigger_start,
            auto_trigger_save=auto_trigger_save,
            auto_trigger_save_timestamp=auto_trigger_save_timestamp,
        )

        return True

    def __modify_config(
        self,
        config_path: Path,
        use_internal_odo3d=True,
        use_maprec_line=True,
        auto_trigger_start=False,
        auto_trigger_save=True,
        auto_trigger_save_timestamp=0,
    ) -> None:
        # read data
        with open(config_path, 'r') as fs:
            data = yaml.safe_load(fs)

        # auto trigger
        logging.info(f'use internal 3D odo: {use_internal_odo3d}')
        logging.info(f'use line from maprec: {use_maprec_line}')
        logging.info(f'auto trigger start: {auto_trigger_start}')
        logging.info(f'auto trigger save: {auto_trigger_save}')
        logging.info(f'auto trigger save timestamp: {auto_trigger_save_timestamp}')
        data['use_internal_odo3d'] = use_internal_odo3d
        data['enable_fusion_mapping'] = not use_maprec_line
        data['use_maprec_line'] = use_maprec_line
        data['auto_trigger_start'] = auto_trigger_start
        data['auto_trigger_save'] = auto_trigger_save
        data['auto_trigger_save_timestamp'] = auto_trigger_save_timestamp
        data['auto_trigger_target_slot'] = auto_trigger_save

        # save
        with open(config_path, 'w') as fs:
            data = yaml.safe_dump(data, fs)


class Process:
    """
    Process information
    """

    def __init__(
        self, module_type: ModuleType = None, module_app: str = None, process: subprocess.Popen = None
    ) -> None:
        self.module_type: ModuleType = module_type  # module type
        self.module_app: str = module_app  # module app name
        self.process: subprocess.Popen = process  # process
        self.module_process: psutil.Process = None  # real module process

        # resource
        self.t: List[float] = []  # timestamp, [s]
        self.cpu: List[float] = []  # CPU percent [%]
        self.memory: List[float] = []  # memory, [MB]

        # find real module process
        self.__find_module_process()

    @property
    def name(self) -> str:
        return self.module_type.name

    @property
    def pid(self) -> Union[int, None]:
        if self.process is None:
            logging.error('cannot obtain PID from none process')
        else:
            return self.process.pid

    @property
    def module_pid(self) -> Union[int, None]:
        if self.module_process is None:
            logging.error('cannot obtain module PID from none process')
        else:
            return self.module_process.pid

    def stop(self) -> None:
        """stop current process"""
        logging.warning(f'stop process {self.module_type.name}')
        if self.process is None or not psutil.pid_exists(self.pid):
            self.process = None
            self.module_process = None
            return

        # stop and wait for 10s, if cannot stop this module, then kill this process
        os.killpg(os.getpgid(self.pid), signal.SIGINT)
        t0 = time.time()
        exit_normal = True
        while True:
            if not psutil.pid_exists(self.pid) or not self.process.poll() is None:
                break
            if time.time() - t0 > 10:
                exit_normal = False
                break
            time.sleep(1)

        if not exit_normal:
            logging.info(f'{self.name} ID = {self.pid} kill process')
            # if cannot stop by ctrl+C, then kill this process
            try:
                p = psutil.Process(self.pid)
                for proc in p.children(recursive=True):
                    proc.kill()
                p.kill()
            except psutil.NoSuchProcess:
                logging.warning(f'cannot found process of {self.name}')
        self.process = None
        self.module_process = None

    def monitor(self, with_resource=True) -> bool:
        """
        Monitor current process

        Args:
            with_resource (bool, optional): whether to monitor process resource. Defaults to True.
        Returns:
            bool: True for current process is running normally, otherwise return False
        """
        if self.process is None:
            return False

        exist = self.process.poll() is None

        if with_resource and exist:
            self.t.append(time.time())  # s

            # obtain CPU and memory
            if self.module_process is not None:
                self.cpu.append(self.module_process.cpu_percent())  # %
                self.memory.append(self.module_process.memory_info().rss / 1024 / 1024)  # MB

        return exist

    def __find_module_process(self):
        if self.process is None:
            return

        # find CPU process
        p = psutil.Process(self.process.pid)
        # try several times to wait process start correctly
        for n in range(5):
            for v in p.children(recursive=True):
                # logging.info(f'[{n}] {v.name()}, {v.pid}, {v.exe()}, {v.cmdline()}')
                if v.name() == self.module_app:
                    self.module_process = v
                    break
            if self.module_process is not None:
                break
            time.sleep(0.5)
        if self.module_process is None:
            logging.warning(
                f'cannot obtain real module process of {self.module_type.name} with name: {self.module_app}'
            )


class Workflow:
    def __init__(
        self,
        pack_folder: Path,
        save_folder: Path,
        speed: int = 1.0,
        use_internal_odo3d: bool = True,
        use_maprec_line: bool = True,
        auto_trigger_start: bool = False,
        auto_trigger_save: bool = True,
        auto_trigger_save_timestamp: int = 0,
        bole_pack_folder: Path = None,
        mapping_folder: Path = None,
        loc_folder: Path = None,
        monitor_resource: bool = False,
    ) -> None:
        self.pack_root: Path = pack_folder.resolve()  # pack root folder
        self.save_root: Path = save_folder.resolve()  # data saving root folder
        self.monitor_resource: bool = monitor_resource  # = monitor_resource

        self.__workflow_log_path: Path = None  # workflow log file path
        self.__current_log_folder: Path = None  # current log folder
        self.__latest_log_path = self.save_root / 'latest'  # latest log link path

        self.__stop: bool = False  # stop flag
        self.__processes: List[Process] = []  # running process
        self.__monitor_count: int = 0  # monitor count

        # all module configs
        self.__module_configs = {
            ModuleType.BolePack: ModuleConfig(
                type=ModuleType.BolePack,
                app='./bolepack.sh',
                real_app='bolepack',
                arguments=['-fillback', './config/fglobal.json'],
                work_folder=bole_pack_folder.resolve(),
            ),
            ModuleType.Mapping: ModuleConfig(
                type=ModuleType.Mapping,
                app='./ndm_envmodel_run.sh',
                real_app='ndm_envmodel',
                arguments=[],
                work_folder=mapping_folder.resolve(),
            ),
            ModuleType.Loc: ModuleConfig(
                type=ModuleType.Loc,
                app='./run_localization_x86.sh',
                real_app='navinet_parking',
                arguments=[],
                work_folder=loc_folder.resolve(),
            ),
        }

        # bolepack config
        self.__bole_pack_speed: int = speed  # fill back speed
        # mapping config
        self.__mapping_use_inter_odo3d: bool = use_internal_odo3d  # whether to use internal 3D odo
        self.__mapping_use_maprec_line: bool = use_maprec_line  # whether to use line from maprec
        self.__mapping_auto_trigger_start: bool = auto_trigger_start  # whether to using auto trigger start
        self.__mapping_auto_trigger_save: bool = auto_trigger_save  # whether to using auto trigger save
        self.__mapping_auto_trigger_save_timestamp: int = (
            auto_trigger_save_timestamp  # auto trigger save timestamp [ms]
        )

    def run(self) -> None:
        # init workflow logger
        self.__init_logger()

        # find all pack folders
        pack_folders = self.__find_pack_folder(print=True)

        # run for each folder
        for n, pack_folder in enumerate(pack_folders):
            # print title
            title = f' [{n+1}/{len(pack_folders)}] {pack_folder.name} '
            logging.warning(f'{title:=^80}')
            logging.info(f'pack folder: {pack_folder} ...')

            self.__make_current_log_folder(pack_folder)
            self.__monitor_count = 0

            # check current pack folder and modify app configs
            if not self.__check_modify_config(pack_folder):
                continue

            # start modules
            modules = self.__modules()
            for v in modules:
                self.__processes.append(self.__start_module(v))
            logging.info('=' * 80)

            # monitor
            while True:
                # check stop
                if self.__stop:
                    logging.warning('stop workflow')
                    self.__post_process()
                    break

                # monitor process status
                running, bole_error = self.__monitor()
                if not running:
                    if bole_error:
                        logging.info('wait 3s for mapping module finish')
                        time.sleep(3)
                    self.__post_process()
                    # error occurs, or finish pack fill back
                    self.__stop_module()
                    break

            if self.__stop:
                break

    def stop(self) -> None:
        self.__stop = True
        self.__stop_module()

    def __find_pack_folder(self, print=False) -> List[Path]:
        """find all pack folders"""
        pack_folders: List[Path] = []

        # add current folder first
        for file in self.pack_root.iterdir():
            if file.suffix == '.pack':
                pack_folders.append(self.pack_root)
                break
        else:
            # recursive sub folder
            for folder in self.pack_root.rglob('*'):
                if folder.is_dir():
                    for file in folder.iterdir():
                        if file.suffix == '.pack':
                            pack_folders.append(folder)
                            break

        pack_folders = sorted(pack_folders)
        logging.info(f'found {len(pack_folders)} pack folders')

        # print
        if print:
            for n, v in enumerate(pack_folders):
                logging.info(f'[{n+1}/{len(pack_folders)}] {v}')

        return pack_folders

    def __init_logger(self) -> None:
        """init workflow logger"""
        # set logging path
        self.__make_current_log_folder()
        self.__workflow_log_path = self.__current_log_folder / 'workflow.log'

        # init logger
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
        handler = logging.FileHandler(self.__workflow_log_path)
        handler.setFormatter(logging.Formatter("[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s"))
        logger.addHandler(handler)

    def __check_modify_config(self, pack_folder: Path) -> bool:
        """modify app config based on pack folder, and check the pack folder is correct"""

        # modify bolepack config
        bolepack_modifier = BolePackConfigModifier(pack_folder, self.__module_configs[ModuleType.BolePack].work_folder)
        ret = bolepack_modifier.modify(speed=self.__bole_pack_speed)

        # modify mapping config
        if ret:
            mapping_modifier = MappingConfigModifier(self.__module_configs[ModuleType.Mapping].work_folder)
            ret = mapping_modifier.modify(
                use_internal_odo3d=self.__mapping_use_inter_odo3d,
                use_maprec_line=self.__mapping_use_maprec_line,
                auto_trigger_start=self.__mapping_auto_trigger_start,
                auto_trigger_save=self.__mapping_auto_trigger_save,
                auto_trigger_save_timestamp=self.__mapping_auto_trigger_save_timestamp,
            )

        return ret

    def __modules(self) -> List[ModuleType]:
        if self.__mapping_auto_trigger_start:
            return [ModuleType.Mapping, ModuleType.BolePack]
        else:
            return [ModuleType.Loc, ModuleType.Mapping, ModuleType.BolePack]

    def __start_module(self, module_type: ModuleType) -> Process:
        # get command str
        config = self.__module_configs[module_type]
        cmd = str(config.app) + ' ' + ' '.join(config.arguments)
        log_file = self.__current_log_folder / f'{module_type.name}.log'
        logging.info(f"{' ' + module_type.name + ' ':=^80}")
        logging.info(f'  command: {cmd}')
        if module_type != ModuleType.BolePack:
            logging.info(f'  version: {self.__obtain_version(module_type)}')
        logging.info(f'  work folder: {config.work_folder}')
        logging.info(f'  log file: {log_file}')
        log_file = open(log_file, 'w')
        process = Process(
            module_type,
            config.real_app,
            subprocess.Popen(
                cmd, shell=True, start_new_session=True, stdout=log_file, stderr=log_file, cwd=config.work_folder
            ),
        )
        logging.info(f'  PID: {process.pid}, module PID: {process.module_pid}')
        return process

    def __obtain_version(self, module_type: ModuleType) -> str:
        """obtain module version"""
        version = ''
        if module_type != ModuleType.BolePack:
            version_file = self.__module_configs[module_type].work_folder / 'version'
            if version_file.exists():
                with open(version_file, 'r') as fs:
                    if module_type == ModuleType.Mapping:
                        fs.readline()
                        version = fs.readline().replace('commit id: ', '').strip()
                    elif module_type == ModuleType.Loc:
                        version = fs.readline().strip()
        return version

    def __stop_module(self) -> None:
        logging.info('stop all modules')
        for v in reversed(self.__processes):
            v.stop()

        # save monitor resource
        self.__save_monitor_resource(self.__current_log_folder)

        # clear process
        self.__processes.clear()

        logging.info('finish stop all modules')

    def __post_process(self) -> None:
        """some post process after this running is finished"""

        # copy map data to current folder
        src_map_folders = [
            (self.__module_configs[ModuleType.Mapping].work_folder / '../map').resolve(),
            (self.__module_configs[ModuleType.Mapping].work_folder / 'map').resolve(),
            (self.__module_configs[ModuleType.Loc].work_folder / '../map').resolve(),
        ]
        src_failed_map_folder = (self.__module_configs[ModuleType.Mapping].work_folder / 'map' / 'failed').resolve()

        # dst folder
        dst_map_folder = self.__current_log_folder / 'map'
        dst_failed_map_folder = self.__current_log_folder / 'failed'

        # copy folder to dst
        if src_failed_map_folder.exists():
            logging.info(f'copy failed map: {src_failed_map_folder} => {dst_failed_map_folder}')
            shutil.move(src_failed_map_folder, dst_failed_map_folder)
            shutil.rmtree(src_failed_map_folder.parent)
        for v in src_map_folders:
            if v.exists():
                logging.info(f'copy map: {v} => {dst_map_folder}')
                shutil.move(v, dst_map_folder)
                break

        # list map file
        for v in self.__current_log_folder.rglob('*.ndm'):
            if v.is_file() and v.suffix == '.ndm':
                logging.info(f'map file: {v}')
                if 'failed' in str(v):
                    logging.error(f'mapping failed')
                else:
                    logging.warning(f'mapping success')

    def __monitor(self) -> Tuple[bool, bool]:
        """
        monitor module status

        Returns:
            Tuple[bool, bool]: 1. True if running correct, otherwise return False
                               2. True if bolepack running finish, otherwise return False
        """

        """
        monitor module status

        Returns:
            bool: True if running correct, otherwise return False
        """
        status = ''  # status info
        has_error, bole_error = False, False
        for v in reversed(self.__processes):
            status += f'{v.name}: '
            if v.monitor(self.monitor_resource):
                status += "OK  "
            else:
                status += "Error  "
                has_error = True
                if v.module_type == ModuleType.BolePack:
                    bole_error = True

        if has_error:
            logging.warning(status)
            return False, bole_error
        else:
            if self.__monitor_count % 20 == 0:
                self.__monitor_count = 0
                logging.info(status)
            self.__monitor_count += 1
            time.sleep(1)
            return True, bole_error

    def __save_monitor_resource(self, save_folder: Path) -> None:
        """save monitor resource to file"""
        if self.monitor_resource:
            save_file = save_folder / 'Resource.bin'
            logging.info(f'save monitor resource data to file: {save_file}')
            with open(save_file, 'wb') as fs:
                pickle.dump(self.__processes, fs)

    def __make_current_log_folder(self, pack_folder: Path = None) -> None:
        """make current log path"""
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        if pack_folder is None:
            self.__current_log_folder = self.save_root / now
        else:
            self.__current_log_folder = self.save_root / f'{now}_{pack_folder.parent.name}_{pack_folder.name}'
        self.__current_log_folder.mkdir(parents=True, exist_ok=True)
        if self.__latest_log_path.exists():
            self.__latest_log_path.unlink()
        self.__latest_log_path.symlink_to(self.__current_log_folder)
        logging.info(f'save module log to "{self.__current_log_folder}"')

        # symlink workflow log file to current folder
        if self.__workflow_log_path is not None:
            workflow_log_link_path = self.__current_log_folder / 'workflow.log'
            if workflow_log_link_path != self.__workflow_log_path:
                workflow_log_link_path.symlink_to(self.__workflow_log_path)


class Plotter:
    @staticmethod
    def load_plot_monitor_resource(resource_folder: Path) -> None:
        """load monitor resource data from file and the plot"""
        resource_file = resource_folder / 'Resource.bin'
        if not resource_file.exists():
            logging.warning(f'cannot found any monitor resource file from folder "{resource_folder}"')
            return
        logging.info(f'load resource data from file {resource_file}')
        with open(resource_file, 'rb') as fs:
            processes: List[Process] = pickle.load(fs)

        # plot
        Plotter.__plot_monitor_resource(processes, name=resource_folder.stem)
        plt.show(block=True)

    @staticmethod
    def __plot_monitor_resource(processes: List[Process], name: str = None) -> None:
        figsize = (12, 8)

        # CPU resource
        fig = plt.figure(f'Process CPU Resource - {name}', figsize=figsize)
        ax1, ax2 = fig.subplots(2, 1, sharex=True)
        for v in processes:
            if len(v.cpu) == 0:
                continue
            ax1.plot(v.t, v.cpu, label=v.name)
            ax2.plot(v.t, v.memory, label=v.name)
        ax1.set_xlabel('Timestamp [s]')
        ax1.set_ylabel('CPU Percent')
        ax1.set_title(f'CPU - {name}')
        ax1.grid()
        ax1.legend()
        ax2.set_xlabel('Timestamp [s]')
        ax2.set_ylabel('Memory [MB]')
        ax2.set_title(f'Memory - {name}')
        ax2.grid()
        ax2.legend()
        plt.tight_layout()


if __name__ == '__main__':
    # argument parser
    parser = argparse.ArgumentParser(
        description='Workflow',
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40, width=120),
    )
    subparsers = parser.add_subparsers(dest='command', title='command', help='workflow command candidate')
    # run
    run_parser = subparsers.add_parser('run', help='run workflow')
    run_parser.add_argument(
        '--pack-folder', default='./data', help='pack folder or pack root folder (default: %(default)s)'
    )
    run_parser.add_argument(
        '--save-folder', default='/opt/horizon/log', help='data/log saving root folder (default: %(default)s)'
    )
    run_parser.add_argument('--monitor', action='store_true', help='whether to monitor process resource')
    run_parser.add_argument('--speed', default=1, type=float, help='speed to fill back pack (default: %(default)s)')
    run_parser.add_argument(
        '--use-extra-odo3d', action='store_true', help='whether to use external 3D odo (default: %(default)s)'
    )
    run_parser.add_argument(
        '--no-use-maprec-line', action='store_true', help='whether not to use line from maprec (default: %(default)s)'
    )
    run_parser.add_argument(
        '--auto-trigger-start',
        action='store_true',
        help='whether to auto trigger start of loc map manager (default: %(default)s)',
    )
    run_parser.add_argument(
        '--no-auto-trigger-save',
        action='store_true',
        help='whether not to auto trigger save of loc map manager (default: %(default)s)',
    )
    run_parser.add_argument(
        '--auto-save-timestamp', default=0, type=int, help='auto trigger save timestamp (ms) (default: %(default)s)'
    )
    run_parser.add_argument(
        '--bole-pack-folder',
        default='/home/jeffery/Programs/bolepack_linux',
        help='bole pack app folder (default: %(default)s)',
    )
    run_parser.add_argument(
        '--mapping-folder',
        default='/home/jeffery/Documents/Work/Code/ndm_envnav/output/ndm_envmodel',
        help='mapping app folder (default: %(default)s)',
    )
    run_parser.add_argument(
        '--loc-folder',
        default='/home/jeffery/Documents/Work/Code/navinet_superparking',
        help='loc map manager app folder (default: %(default)s)',
    )
    # plot monitor resource
    plot_monitor_parser = subparsers.add_parser('plot', help='load and plot monitor resource')
    plot_monitor_parser.add_argument('folder', help='folder contain monitored resource')

    # parse arguments
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

    if args.command == 'run':
        workflow = Workflow(
            Path(args.pack_folder),
            Path(args.save_folder),
            speed=int(args.speed),
            use_internal_odo3d=not args.use_extra_odo3d,
            use_maprec_line=not args.no_use_maprec_line,
            auto_trigger_start=args.auto_trigger_start,
            auto_trigger_save=not args.no_auto_trigger_save,
            auto_trigger_save_timestamp=int(args.auto_save_timestamp),
            bole_pack_folder=Path(args.bole_pack_folder),
            mapping_folder=Path(args.mapping_folder),
            loc_folder=Path(args.loc_folder),
            monitor_resource=args.monitor,
        )

        def stop_handler(signum, frame):
            # res = input('Ctrl+C was pressed, Do you really want to exist? y/n ')
            logging.warning('Ctrl+C was pressed, exit...')
            workflow.stop()

        # register Ctrl+C handler
        signal.signal(signal.SIGINT, stop_handler)

        # start and run
        workflow.run()
    elif args.command == 'plot':
        if not enable_plot:
            logging.critical(f'exit plot process because cannot import matplotlib')
        else:
            # load monitor resources and plot
            Plotter.load_plot_monitor_resource(Path(args.folder))
