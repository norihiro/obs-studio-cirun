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

static void circlebuf_check_internal_data(void **state)
{
	UNUSED_PARAMETER(state);

	char buf[6];
	struct circlebuf cb = {0};

	circlebuf_push_front(&cb, "ab", 2);
	assert_memory_equal(cb.data, "ab", 2);
	assert_int_equal(cb.size, 2);
	assert_int_equal(cb.start_pos, 0);
	assert_int_equal(cb.end_pos, 2);
	assert_int_equal(cb.capacity, 2);

	circlebuf_push_back(&cb, "cd", 2);
	assert_memory_equal(cb.data, "abcd", 4);
	assert_int_equal(cb.size, 4);
	assert_int_equal(cb.start_pos, 0);
	assert_int_equal(cb.end_pos, 4);
	assert_int_equal(cb.capacity, 4);

	circlebuf_push_front(&cb, "ef", 2);
	// contents: "efabcd", internal: "abcd..ef"
	assert_memory_equal(cb.data, "abcd", 4);
	assert_memory_equal(cb.data + 6, "ef", 2);
	assert_int_equal(cb.size, 6);
	assert_int_equal(cb.start_pos, 6);
	assert_int_equal(cb.end_pos, 4);
	assert_int_equal(cb.capacity, 8);

	// Cover `if (back_size < size)`
	circlebuf_peek_back(&cb, buf, 6);
	assert_memory_equal(buf, "efabcd", 6);

	// Cover `if (offset >= cb->capacity)`
	assert_ptr_equal(circlebuf_data(&cb, 2), cb.data);

	// Cover `if (idx >= cb->size)`
	assert_ptr_equal(circlebuf_data(&cb, 6), NULL);

	circlebuf_place(&cb, 1, "FA", 2);
	// contents: "eFAbcd", internal: "Abcd..eF"
	assert_memory_equal(cb.data, "Abcd", 4);
	assert_memory_equal(cb.data + 6, "eF", 2);
	assert_int_equal(cb.size, 6);
	assert_int_equal(cb.start_pos, 6);
	assert_int_equal(cb.end_pos, 4);
	assert_int_equal(cb.capacity, 8);

	circlebuf_pop_front(&cb, NULL, 4);
	// contents: "cd", internal: "..cd...."
	assert_memory_equal(cb.data + 2, "cd", 2);
	assert_int_equal(cb.size, 2);
	assert_int_equal(cb.start_pos, 2);
	assert_int_equal(cb.end_pos, 4);
	assert_int_equal(cb.capacity, 8);

	// Cover `if (new_end_pos > cb->capacity) if (back_size)`
	circlebuf_push_back_zero(&cb, 6);
	// contents: "cd000000", internal: "00cd0000"
	assert_memory_equal(cb.data, "\0\0cd\0\0\0\0", 8);
	assert_int_equal(cb.size, 8);
	assert_int_equal(cb.start_pos, 2);
	assert_int_equal(cb.end_pos, 2);
	assert_int_equal(cb.capacity, 8);

	circlebuf_pop_back(&cb, NULL, 6);
	// contents: "cd", internal: "..cd...."
	assert_memory_equal(cb.data + 2, "cd", 2);
	assert_int_equal(cb.size, 2);
	assert_int_equal(cb.start_pos, 2);
	assert_int_equal(cb.end_pos, 4);
	assert_int_equal(cb.capacity, 8);

	// Cover `if (cb->start_pos < size) if (cb->start_pos)`
	circlebuf_push_front(&cb, "ghij", 4);
	// contents: "ghijcd", internal: "ijcd..gh"
	assert_memory_equal(cb.data, "ijcd", 4);
	assert_memory_equal(cb.data + 6, "gh", 2);
	assert_int_equal(cb.size, 6);
	assert_int_equal(cb.start_pos, 6);
	assert_int_equal(cb.end_pos, 4);
	assert_int_equal(cb.capacity, 8);

	// Cover `if (size <= cb->size)`
	circlebuf_upsize(&cb, 1);
	assert_int_equal(cb.size, 6);
	assert_int_equal(cb.start_pos, 6);
	assert_int_equal(cb.end_pos, 4);
	assert_int_equal(cb.capacity, 8);

	circlebuf_free(&cb);
	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(circlebuf_basic),
		cmocka_unit_test(circlebuf_check_internal_data),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
