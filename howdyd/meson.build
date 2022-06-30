project('howdyd', 'c', version: '2.99.20220426')

python = import('python')
i18n = import('i18n')

package_sources = [
                   'package/__init__.py',
                   'package/caller.py',
                   'package/device.py',
                   'package/error.py',
                   'package/manager.py',
                   'package/models.py',
                   'package/scan.py'
                  ]

python_installation = python.find_installation('python3')
python_installation.install_sources(package_sources, subdir: meson.project_name())

prefix = get_option('prefix')
datadir = get_option('datadir')
libexecdir = get_option('libexecdir')

entry_script = 'howdyd'
install_data(entry_script,
             install_dir: libexecdir)

systemd_dep = dependency('systemd')

if systemd_dep.found()
    systemd_unitdir = systemd_dep.get_pkgconfig_variable('systemdsystemunitdir',
                                                         define_variable: ['prefix', prefix])

    systemd_units = [ 'systemd/howdyd.service' ]
    install_data(systemd_units, install_dir: systemd_unitdir)
endif

dbus_dep = dependency('dbus-1', required: true)

dbus_servicedir = dbus_dep.get_pkgconfig_variable('system_bus_services_dir',
                                                  define_variable: ['datadir', datadir])
dbus_services = [ 'dbus/nl.boltgolt.Howdy.service' ]

install_data(dbus_services, install_dir: dbus_servicedir)

dbus_policydir = join_paths(dbus_servicedir, '../system.d')
dbus_policies = [ 'dbus/nl.boltgolt.Howdy.conf' ]

install_data(dbus_policies, install_dir: dbus_policydir)

dbus_interfacedir = dbus_dep.get_pkgconfig_variable('interfaces_dir',
                                                    define_variable: ['datadir', datadir])
dbus_interfaces = [
                    'dbus/nl.boltgolt.Howdy.Device.xml',
                    'dbus/nl.boltgolt.Howdy.Manager.xml',
                    'dbus/nl.boltgolt.Howdy.Scan.xml',
                  ]

install_data(dbus_interfaces, install_dir: dbus_interfacedir)

polkit_dep = dependency('polkit-gobject-1')
polkit_policy_dir = polkit_dep.get_pkgconfig_variable('policydir',
                                                      define_variable: ['prefix', prefix])

polkit_policy = 'nl.boltgolt.Howdy.policy'
i18n.merge_file(
  input: 'polkit/' + polkit_policy + '.in',
  output: polkit_policy,
  po_dir: 'po/',
  install: true,
  install_dir: polkit_policy_dir,
)
