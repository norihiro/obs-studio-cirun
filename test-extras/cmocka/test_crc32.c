#include <stdarg.h>
#include <stdint.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>
#include <util/crc32.h>

static void crc32_test(void **state)
{
	UNUSED_PARAMETER(state);

	const char *buf = "string to test";
	uint32_t crc1 = 0x91342591;
	uint32_t crc2 = 0x91342591;

	crc1 = calc_crc32(crc1, buf, 7);
	crc1 = calc_crc32(crc1, buf + 7, 7);

	crc2 = calc_crc32(crc2, buf, 14);

	assert_int_equal(crc1, crc2);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(crc32_test),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
