from distutils.core import setup
import py2exe, os, sys

sys.argv.append('py2exe')

setup(
	console=['twitch2.py'],
	data_files=[('', ['settings.json'])],
	zipfile = None,
	options = {'py2exe': {'bundle_files': 1}},
	)