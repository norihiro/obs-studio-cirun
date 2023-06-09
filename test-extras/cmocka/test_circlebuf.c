#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

#include <util/circlebuf.h>

static void circlebuf_basic(void **state)
{
	UNUSED_PARAMETER(state);

	struct circlebuf cb = {0};
	char data[8] = {0};

	circlebuf_push_front(&cb, NULL, 0);

	circlebuf_push_front(&cb, "abcd", 4);

	circlebuf_push_front(&cb, "ef", 2);

	circlebuf_pop_back(&cb, data, 4);
	assert_memory_equal(data, "abcd", 4);

	circlebuf_push_back_zero(&cb, 2);
	circlebuf_push_back_zero(&cb, 4);

	circlebuf_pop_back(&cb, data, 6);
	assert_memory_equal(data, "\0\0\0\0\0\0", 6);

	circlebuf_pop_back(&cb, data, 2);
	assert_memory_equal(data, "ef", 2);

	circlebuf_free(&cb);
	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(circlebuf_basic),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
