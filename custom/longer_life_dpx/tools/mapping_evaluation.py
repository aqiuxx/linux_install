"""
Mapping Evaluation 建图评测
1. 根据之前的地图生成一份真值(是否能正常建图)用于评测, 主要评测是否建图成功
2. 导入真值数据, 并评测当前建图是否成功
3. 合计当前建图结果到真值数据中
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import argparse, logging, coloredlogs, datetime
import re
import numpy as np
from pathlib import Path

# from typing import List
# import util


class MapInfo:
    """
    Pack relative path example:
        ./dataset_name/record_name/case_name/***.pack
    """

    def __init__(self, pack_path: Path, relative_path: Path) -> None:
        self.pack_path: Path = pack_path  # pack folder path
        self.relative_path: Path = relative_path  # relative pack folder path
        self.dataset_name: str = None  # dataset name
        self.short_pack_name: str = None  # short pack name, used in workflow log
        self.could_mapping_intra_odo3d: bool = False  # whether this pack could mapping success using intra odo3d
        self.could_mapping_extra_odo3d: bool = False  # whether this pack could mapping success using extra odo3d

        # whether could mapping variable is changed in curring running, used for ground truth comparison
        self.could_mapping_intra_odo3d_change: bool = False
        self.could_mapping_extra_odo3d_change: bool = False

        # current running option
        self.has_run: bool = False  # whether this pack has running for mapping
        self.run_using_extra_odo3d: bool = False  # whether this pack is run using extra odo3d
        self.map_file: Path = None  # map file path

        # calculate dataset name and short pack name
        self.__calculate_dataset_short_pack_name()

    @property
    def has_map(self) -> bool:
        return self.map_file is not None

    @property
    def mapping_success(self) -> bool:
        """Whether this pack is mapping success"""
        return self.map_file is not None and 'failed' not in str(self.map_file)

    def __calculate_dataset_short_pack_name(self) -> str:
        """calculate dataset and short pack name"""
        # dataset_name/record_name/case_name
        record_name = None
        case_name: str = str(self.relative_path.stem)
        parent = self.relative_path.parent
        parent_parent = self.relative_path.parent.parent
        if str(parent_parent) == '.':
            self.dataset_name = str(parent)
        else:
            self.dataset_name = str(parent_parent)
            record_name = str(parent.relative_to(parent_parent))

        if record_name is None:
            self.short_pack_name = f'{self.dataset_name}_{case_name}'
        else:
            self.short_pack_name = f'{record_name}_{case_name}'


class Analyzer:
    def __init__(
        self,
        pack_folders: List[str],
        run_folder: Path,
        save_folder: Path,
        ground_truth_file: Path,
        use_extra_odo3d=False,
    ) -> None:
        self.pack_roots: List[Path] = [Path(v).resolve() for v in pack_folders]  # pack root folders
        self.run_folder: Path = run_folder.resolve()  # workflow running folder
        self.ground_truth_file: Path = ground_truth_file.resolve()  # last ground truth file
        self.save_folder: Path = save_folder.resolve()  # save folder
        self.use_extra_odo3d: bool = use_extra_odo3d  # whether current running is using extra 3D odo

        self.__map_infos: List[MapInfo] = []

    def run(self) -> None:
        logging.info(f'using 3D odo in current running: {self.use_extra_odo3d}')

        self.__find_pack()

        # load could mapping info from ground truth
        if self.ground_truth_file.exists():
            self.__load_from_ground_truth(self.ground_truth_file)

        self.__find_mapping_map()

        # save for ground truth
        self.__merge_save_for_ground_truth()

        # list all map info
        self.__print_map_info(only_run=True, with_detail=False)
        # statistics
        self.__statistics()

    def __find_pack(self) -> None:
        """find all pack folders"""
        for pack_root in self.pack_roots:
            for folder in pack_root.rglob('*'):
                if folder.is_dir():
                    for file in folder.iterdir():
                        if file.suffix == '.pack':
                            relative_path = file.parent.relative_to(pack_root)
                            self.__map_infos.append(MapInfo(file.parent, relative_path))
                            break
        # sort
        self.__map_infos.sort(key=lambda v: v.relative_path)
        logging.info(f'found {len(self.__map_infos)} pack folders')

    def __find_mapping_map(self) -> None:
        for folder in self.run_folder.iterdir():
            if folder.is_dir() and len(folder.stem) > 14:
                # find correspond map info
                log_name = folder.stem[15:]
                info_index = None
                info: MapInfo = None
                for n, v in enumerate(self.__map_infos):
                    if v.short_pack_name == log_name:
                        info_index, info = n, v
                        break
                if info is None:
                    logging.error(f'cannot found corresponding map info for {folder.stem}')
                    continue

                info.has_run = True

                # check current map with extra odo3d
                info.run_using_extra_odo3d = self.__check_running_with_extra_odo3d(folder)

                # find .ndm file in map
                for v in folder.rglob('*'):
                    if v.is_file() and v.suffix == '.ndm':
                        if info.map_file is None:
                            info.map_file = v
                        else:
                            logging.error(f'found multiple .ndm file in {folder}')
                            info.map_file = None
                            break

                self.__map_infos[info_index] = info

    def __check_running_with_extra_odo3d(self, current_run_folder: Path) -> bool:
        """check current running is with extra odo3d"""
        found = False
        mapping_log = current_run_folder / 'Mapping.log'
        if mapping_log.exists():
            with open(mapping_log, 'r') as fs:
                for line in fs.readlines():
                    ret = re.search(r'.*use internal 3D odo: (.*)\n', line)
                    if ret:
                        return ret.group(1).lower() == 'false'

        if not found:
            logging.warning(
                f'cannot check current running is with extra odo3d, use argument input: {self.use_extra_odo3d}'
            )
            return self.use_extra_odo3d

    def __load_from_ground_truth(self, ground_truth_file: Path) -> None:
        """load `could_mapping` info from ground truth file"""
        logging.info(f'load could mapping info for ground truth file: {ground_truth_file}')
        with open(ground_truth_file, 'r') as fs:
            fs.readline()  # skip first header line
            for line in fs.readlines():
                # VersionName,Dataset,Relative Path,Could Mapping using Intra 3D Odo,Could Mapping using Extra 3D Odo
                tokens = line.strip().split(',')
                relative_path = tokens[2]
                could_mapping_intra_odo3d = self.str_to_bool(tokens[3].lower())
                could_mapping_extra_odo3d = self.str_to_bool(tokens[4].lower())

                # find correspond map info
                info_index = None
                info: MapInfo = None
                for n, v in enumerate(self.__map_infos):
                    if str(v.relative_path) == relative_path:
                        info_index, info = n, v
                        break
                if info is None:
                    logging.error(f'cannot found corresponding map info for {relative_path}')
                    continue

                # set `could_mapping` info
                if could_mapping_intra_odo3d:
                    info.could_mapping_intra_odo3d = True
                if could_mapping_extra_odo3d:
                    info.could_mapping_extra_odo3d = True

                self.__map_infos[info_index] = info

    def __merge_save_for_ground_truth(self) -> None:
        """merge current result and save mapping info as ground truth"""
        current_name = self.run_folder.stem
        save_file = self.save_folder / f'{current_name}.csv'
        save_file.parent.mkdir(exist_ok=True, parents=True)
        logging.info(f'save current mapping info for ground truth, file: {save_file}')
        with open(save_file, 'w') as fs:
            fs.write('版本,数据集,数据路径,内部3DOdo能建图成功,外部3DOdo能建图成功,内部3DOdo能建图成功改变,外部3DOdo能建图成功改变,运行,建图成功\n')
            for n, v in enumerate(self.__map_infos):
                if v.run_using_extra_odo3d:
                    could_mapping_extra_odo3d = v.could_mapping_extra_odo3d or v.mapping_success
                    # set `could_mapping` info
                    if v.could_mapping_extra_odo3d == could_mapping_extra_odo3d:
                        v.could_mapping_extra_odo3d = could_mapping_extra_odo3d
                        v.could_mapping_extra_odo3d_change = True
                else:
                    could_mapping_intra_odo3d = v.could_mapping_intra_odo3d or v.mapping_success
                    # set `could_mapping` info
                    if v.could_mapping_intra_odo3d != could_mapping_intra_odo3d:
                        v.could_mapping_intra_odo3d = could_mapping_intra_odo3d
                        v.could_mapping_intra_odo3d_change = True

                self.__map_infos[n] = v
                fs.write(
                    f"{current_name},{v.dataset_name},{v.relative_path},{self.bool_to_str(v.could_mapping_intra_odo3d)}"
                    f",{self.bool_to_str(v.could_mapping_extra_odo3d)}"
                    f",{self.bool_to_str(v.could_mapping_intra_odo3d_change)}"
                    f",{self.bool_to_str(v.could_mapping_extra_odo3d_change)}"
                )
                if v.has_run:
                    fs.write(f',{self.bool_to_str(v.has_run)},{self.bool_to_str(v.mapping_success)}\n')
                else:
                    fs.write(f'\n')

    @staticmethod
    def bool_to_str(value: bool) -> str:
        return '是' if value else '否'

    @staticmethod
    def str_to_bool(str: str) -> bool:
        return str.lower() == '是' or str.lower() == 'true'

    def __print_map_info(self, only_run=False, with_detail=False) -> None:
        """
        Print map info

        Args:
            only_run (bool, optional): Only print info which is running in current workflow
            with_detail (bool, optional): Whether print detail info
        """
        # logging.info(util.Section('Map Info', False))
        total = len([True for v in self.__map_infos if v.has_run]) if only_run else len(self.__map_infos)
        n = 0
        for _, info in enumerate(self.__map_infos):
            if only_run and not info.has_run:
                continue
            n += 1
            could_mapping = (
                info.could_mapping_extra_odo3d if info.run_using_extra_odo3d else info.could_mapping_intra_odo3d
            )
            title = f'[{n}/{total}] {info.mapping_success}/{could_mapping} {info.relative_path}'
            if info.mapping_success:
                logging.info(title)
            else:
                logging.warning(title)
            if with_detail:
                logging.info(f'\tpack: {info.pack_path}')
                logging.info(f'\trelative pack path: {info.relative_path}')
                logging.info(f'\tshort pack name: {info.short_pack_name}')
                logging.info(f'\tcould mapping using extra odo3d: {info.could_mapping_extra_odo3d}')
                logging.info(f'\tcould mapping using intra odo3d: {info.could_mapping_intra_odo3d}')
                logging.info(f'\thas run: {info.has_run}')
                logging.info(f'\trunning using extra odo3d: {info.run_using_extra_odo3d}')
                logging.info(f'\tmap file: {info.map_file}')
                logging.info(f'\tmapping success/could mapping: {info.mapping_success}/{could_mapping}')

    def __statistics(self) -> None:
        # logging.info(util.Section('Statistics', False))
        # pack num, could mapping num, could mapping in curring running
        pack_num, could_mapping_num, current_could_mapping_num = 0, 0, 0
        could_mapping_intra_odo3d_change_num, could_mapping_extra_odo3d_change_num = 0, 0
        run_num, map_num, success_map_num = 0, 0, 0  # running for mapping, has map, has success map

        for info in self.__map_infos:
            pack_num += 1
            if info.run_using_extra_odo3d and info.could_mapping_extra_odo3d:
                could_mapping_num += 1
            elif not info.run_using_extra_odo3d and info.could_mapping_intra_odo3d:
                could_mapping_num += 1
            if info.could_mapping_intra_odo3d_change:
                could_mapping_intra_odo3d_change_num += 1
            if info.could_mapping_extra_odo3d_change:
                could_mapping_extra_odo3d_change_num += 1

            if info.has_run:
                run_num += 1
                if info.run_using_extra_odo3d and info.could_mapping_extra_odo3d:
                    current_could_mapping_num += 1
                elif not info.run_using_extra_odo3d and info.could_mapping_intra_odo3d:
                    current_could_mapping_num += 1
            if info.has_map:
                map_num += 1
            if info.mapping_success:
                success_map_num += 1

        success_ratio = success_map_num / current_could_mapping_num
        fail_ratio = 1 - success_ratio
        fail_map_ratio = (map_num - success_map_num) / map_num

        logging.info(
            f'pack num: {pack_num}, could mapping num: {could_mapping_num}'
            f', current could mapping num: {current_could_mapping_num}'
        )
        logging.info(
            f'could mapping num change using intra 3D odo: {could_mapping_intra_odo3d_change_num}'
            f', could mapping num change using extra 3D odo: {could_mapping_extra_odo3d_change_num}'
        )
        logging.info(f'run num: {run_num}, map num: {map_num}, success map num: {success_map_num}')
        logging.info(
            f'success ratio: {success_ratio * 100:.2f}%, fail ratio: {fail_ratio * 100:.2f}%'
            f', fail map ratio: {fail_map_ratio * 100:.2f}%'
        )


if __name__ == '__main__':
    # argument parser
    parser = argparse.ArgumentParser(
        description='Mapping Map Analyzer',
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40, width=120),
    )
    parser.add_argument(
        '--pack-folders',
        default=None,
        nargs='*',
        required=True,
        help='pack folder or pack root folder (default: %(default)s)',
    )
    parser.add_argument(
        '--run-folder', default='/opt/horizon/log', required=True, help='workflow running folder (default: %(default)s)'
    )
    parser.add_argument('--save-folder', default='./data/mapping_map', help='save folder (default: %(default)s)')
    parser.add_argument('--ground-truth', default='./ground_truth.csv', help='ground truth file (default: %(default)s)')
    parser.add_argument(
        '--use-extra-odo3d', action='store_true', help='whether current running is using 3D odo (default: %(default)s)'
    )
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

    analyzer = Analyzer(
        args.pack_folders,
        Path(args.run_folder),
        Path(args.save_folder),
        ground_truth_file=Path(args.ground_truth),
        use_extra_odo3d=args.use_extra_odo3d,
    )
    analyzer.run()
