#define _GNU_SOURCE
#include <string.h>
#include <link.h>
#include <dlfcn.h>
#include <unistd.h>
#include <sys/wait.h>

#include <util/platform.h>

static int module_has_qt_child(const char *path)
{
	void *mod = os_dlopen(path);
	if (mod == NULL) {
		return 1;
	}

	struct link_map *list = NULL;
	if (dlinfo(mod, RTLD_DI_LINKMAP, &list) == 0) {
		for (struct link_map *ptr = list; ptr; ptr = ptr->l_next) {
			if (strstr(ptr->l_name, "libQt") != NULL) {
				return 0;
			}
		}
	}

	return 1;
}

bool module_has_qt(const char *path)
{
	pid_t pid = fork();
	if (pid == 0) {
		_exit(module_has_qt_child(path));
	}
	if (pid < 0) {
		return false;
	}
	int status;
	if (waitpid(pid, &status, 0) < 0) {
		return false;
	}
	return WIFEXITED(status) && WEXITSTATUS(status) == 0;
}
