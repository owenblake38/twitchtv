from distutils.core import setup
import py2exe, os, sys

sys.argv.append('py2exe')

setup(
	console=['./src/TwitchTV_VOD_Catchup.py'],
	data_files=[('', ['./conf/settings.json'])],
	zipfile = None,
	options = {'py2exe': {'bundle_files': 1}},
	)