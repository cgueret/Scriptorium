project(
  'scriptorium',
  version: '0.3.0',
  meson_version: '>= 1.0.0',
  default_options: [
    'warning_level=2',
    'werror=false',
  ],
  license: 'GPL-3.0-only',
)

i18n = import('i18n')
gnome = import('gnome')

subdir('data')
subdir('scriptorium')
subdir('po')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
