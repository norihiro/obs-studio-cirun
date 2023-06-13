#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <util/bmem.h>

void os_breakpoint()
{
}

int main(int argc, char **argv)
{
	void *ptr;

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
	base_set_allocator(NULL); // do nothing
#pragma GCC diagnostic pop

	for (int i = 1; i < argc; i++) {
		char *ai = argv[i];
		if (strcmp(ai, "bmalloc-0") == 0) {
			ptr = bmalloc(0);
			assert(ptr != NULL);
		} else if (strcmp(ai, "bmalloc-large") == 0) {
			ptr = bmalloc(1024ULL * 1024 * 1024 * 1024);
		} else if (strcmp(ai, "brealloc-0") == 0) {
			ptr = brealloc(NULL, 0);
			assert(ptr != NULL);
		} else if (strcmp(ai, "brealloc-large") == 0) {
			ptr = brealloc(NULL, 1024ULL * 1024 * 1024 * 1024);
		}
	}

	return 0;
}
