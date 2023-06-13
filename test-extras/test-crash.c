#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <util/base.h>

static void crash_handler(const char *fmt, va_list va, void *param)
{
	assert(crash_handler == param);
	printf("In crash_handler: %s", fmt);
}

static void crash_crash(const char *fmt, va_list va, void *param)
{
	bcrash("nested");
}

int main(int argc, char **argv)
{
	log_handler_t handler;
	void *param;
	base_get_log_handler(&handler, &param);
	assert(param == NULL);

	if (argc > 1 && strcmp(argv[1], "base_set_crash_handler") == 0)
		base_set_crash_handler(crash_handler, crash_handler);
	else if (argc > 1 && strcmp(argv[1], "crash-crash") == 0)
		base_set_crash_handler(crash_crash, NULL);

	bcrash("Testing bcrash.\n");
}
