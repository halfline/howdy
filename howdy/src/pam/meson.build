project('pam_howdy', 'cpp', version: '0.1.0', default_options: ['cpp_std=c++14'])

inih_cpp = dependency('INIReader', fallback: ['inih', 'INIReader_dep'])
libevdev = dependency('libevdev')
libpam = meson.get_compiler('cpp').find_library('pam')
threads = dependency('threads')

# Translations
subdir('po')

pam_module_dir = (get_option('pam-module-dir') != '')? get_option('pam-module-dir') : get_option('prefix') / get_option('libdir') / 'security'

shared_library(
	'pam_howdy',
	'main.cc',
	'enter_device.cc',
	dependencies: [
		libpam,
		inih_cpp,
		threads,
		libevdev,
	],
	install: true,
	install_dir: pam_module_dir,
	name_prefix: ''
)
