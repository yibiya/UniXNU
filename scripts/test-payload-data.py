#!/usr/bin/env python3
"""Prevent a RAM Data handoff from conflicting with installed UFS Data."""
import argparse
from pathlib import Path
import tempfile
import unittest

from unixnu.config import parse_config
from unixnu.payload import check_data_input
from unixnu.util import Error


class PayloadDataTest(unittest.TestCase):
    def test_persistent_ufs_requires_no_ram_seed(self):
        for configured in (False, True):
            with self.subTest(configured=configured), tempfile.TemporaryDirectory() as name:
                root = Path(name)
                (root / 'configs').mkdir()
                config_text = 'CONFIG_XNU_OWNER_DATA_MOUNT=y\nCONFIG_XNU_OWNER_DATA_UFS=y\n'
                (root / 'configs/boot_defconfig').write_text(config_text)
                config_path = root / '.config'
                if configured:
                    config_path.write_text(config_text)
                ctx = argparse.Namespace(config=parse_config(config_text) if configured else {},
                                         config_path=config_path, config_name='boot_defconfig', device=root)
                check_data_input(ctx, None)
                with self.assertRaisesRegex(Error, 'omit --data-ramdisk'):
                    check_data_input(ctx, root / 'seed.dbr')

    def test_memory_data_still_requires_seed(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            config_path = root / '.config'
            config_path.write_text('CONFIG_XNU_OWNER_DATA_MOUNT=y\n')
            ctx = argparse.Namespace(config=parse_config(config_path.read_text()), config_path=config_path,
                                     config_name=None, device=root)
            with self.assertRaisesRegex(Error, 'requires --data-ramdisk'):
                check_data_input(ctx, None)
            check_data_input(ctx, root / 'seed.dbr')


if __name__ == '__main__':
    unittest.main()
