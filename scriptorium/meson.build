pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'scriptorium'
gnome = import('gnome')
python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
	input: 'scriptorium.in',
	output: 'scriptorium',
	configuration: conf,
	install: true,
	install_dir: get_option('bindir'),
	install_mode: 'r-xr-xr-x',
)

scriptorium_sources = [
	'__init__.py',
	'main.py',
	'application.py',
	'window.py',
	'globals.py',
	'language_tool.py',
]
install_data(scriptorium_sources, install_dir: moduledir)



blueprints = custom_target(
	'blueprints',
	input: files(
		'window.blp',

		'dialogs/dialog_add.blp',
		'dialogs/select_scenes.blp',
		'dialogs/select_entities.blp',
		'dialogs/preferences.blp',

		'views/library.blp',
		'views/library_item.blp',
		'views/editor.blp',

		'views/plan/page.blp',
		'views/plan/editor_entities.blp',
		'views/plan/editor_entities_details.blp',
		'views/plan/editor_scenes.blp',
		'views/plan/editor_scenes_details.blp',
		'views/plan/editor_manuscript.blp',
		'views/plan/editor_overview.blp',
		'views/plan/editor_overview_item.blp',
		'views/plan/editor_images.blp',
		'views/plan/editor_images_item.blp',

		'views/write/page.blp',
		'views/write/navigation.blp',
		'views/write/navigation_item.blp',

		'views/publish/page.blp',

		'widgets/chapter_column.blp',
		'widgets/scene.blp',
		'widgets/chapter.blp',
		'widgets/entity_card.blp',
		'widgets/multiline_entry_row.blp',
		'widgets/cards_list.blp',
		'widgets/theme_selector.blp',
		'widgets/annotation.blp',
		'widgets/text_view.blp',
	),
	output: '.',
	command: [
		find_program('blueprint-compiler'),
		'batch-compile',
		'@OUTPUT@',
		'@CURRENT_SOURCE_DIR@',
		'@INPUT@',
	],
)

gnome.compile_resources(
	'scriptorium',
	'scriptorium.gresource.xml',
	gresource_bundle: true,
	install: true,
	install_dir: pkgdatadir,
	dependencies: blueprints,
)

subdir('models')
subdir('dialogs')
subdir('widgets')
subdir('views')
subdir('utils')


