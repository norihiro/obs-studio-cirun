#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

#include <util/platform.h>
#include <util/bmem.h>

static void utf8_file_open(void **state)
{
	UNUSED_PARAMETER(state);

	const char *filename = CMAKE_CURRENT_SOURCE_DIR "/test_utf8.txt";
	FILE *fp1 = os_fopen(filename, "r");

	wchar_t *filename_w;
	os_utf8_to_wcs_ptr(filename, 0, &filename_w);
	FILE *fp2 = os_wfopen(filename_w, "r");
	bfree(filename_w);

	assert_int_equal(os_fgetsize(fp1), os_fgetsize(fp2));
	assert_int_equal(os_fgetsize(fp1), os_get_file_size(filename));

	fclose(fp1);
	fclose(fp2);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(utf8_file_open),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
