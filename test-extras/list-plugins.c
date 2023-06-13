#include <stdio.h>

#include <obs.h>
#include <obs-module.h>
#include <util/dstr.h>
#include <util/platform.h>

void get_plugin_info(const char *path, bool *is_obs_plugin, bool *can_load);
void free_module(struct obs_module *mod); // TODO: defined in obs-internal.h
bool module_has_qt(const char *path);

static void setup_module_paths()
{
	char base_module_dir[512];

	int ret = os_get_config_path(base_module_dir, sizeof(base_module_dir),
				"obs-studio/plugins/%module%");
	if (ret <= 0)
		return;

	printf("Info: base module directory: %s\n", base_module_dir);

	struct dstr path_bin = {0};
	struct dstr path_data = {0};
	dstr_printf(&path_bin, "%s/bin/64bit", base_module_dir);
	dstr_printf(&path_data, "%s/data", base_module_dir);
	obs_add_module_path(path_bin.array, path_data.array);

	dstr_free(&path_bin);
	dstr_free(&path_data);
}

static void load_module_cb(void *param, const struct obs_module_info2 *info)
{
	bool is_obs_plugin, can_load_obs_plugin;
	get_plugin_info(info->bin_path, &is_obs_plugin, &can_load_obs_plugin);

	bool has_qt = module_has_qt(info->bin_path);

	if (!is_obs_plugin || !can_load_obs_plugin || has_qt)
		return;

	obs_module_t *module;
	int code = obs_open_module(&module, info->bin_path, info->data_path);
	switch (code) {
	case MODULE_MISSING_EXPORTS:
		blog(LOG_DEBUG,
		     "Failed to load module file '%s', not an OBS plugin",
		     info->bin_path);
		return;
	case MODULE_FILE_NOT_FOUND:
		blog(LOG_DEBUG,
		     "Failed to load module file '%s', file not found",
		     info->bin_path);
		return;
	case MODULE_ERROR:
		blog(LOG_DEBUG, "Failed to load module file '%s'",
		     info->bin_path);
		return;
	case MODULE_INCOMPATIBLE_VER:
		blog(LOG_DEBUG,
		     "Failed to load module file '%s', incompatible version",
		     info->bin_path);
		return;
	case MODULE_HARDCODED_SKIP:
		return;
	}

	if (!obs_init_module(module))
		free_module(module);

	printf(
		"module: %s\n"
		"\tdescription: %s\n"
		"\tauthor: %s\n",
			info->name,
			obs_get_module_description(module),
			obs_get_module_author(module)
	      );
}

static void load_modules()
{
	obs_find_modules2(load_module_cb, NULL);
}

int main(int argc, char **argv)
{
	obs_startup("C", NULL, NULL);

	load_modules();

	obs_shutdown();
	blog(LOG_INFO, "Number of memory leaks: %ld", bnum_allocs());
	return 0;
}
