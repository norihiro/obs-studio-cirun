#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

#include <util/darray.h>

static void array_basic_test(void **state)
{
	UNUSED_PARAMETER(state);

	DARRAY(uint8_t) testarray;
	da_init(testarray);

	uint8_t t = 1;
	da_push_back_array(testarray, &t, 1);

	assert_int_equal(testarray.num, 1);
	assert_memory_equal(testarray.array, &t, 1);

	da_reserve(testarray, 2);
	assert_memory_equal(testarray.array, &t, 1);
	assert_int_equal(testarray.num, 1);
	assert_int_equal(testarray.capacity, 2);

	uint8_t *ptr = da_push_back_new(testarray);
	*ptr = 2;
	assert_int_equal(testarray.array[1], 2);

	ptr = da_insert_new(testarray, 1);
	*ptr = 3;
	assert_int_equal(testarray.array[0], 1);
	assert_int_equal(testarray.array[1], 3);
	assert_int_equal(testarray.array[2], 2);

	da_erase_range(testarray, 0, 3);
	assert_int_equal(testarray.num, 0);

	*(uint8_t *)da_push_back_new(testarray) = 1;
	*(uint8_t *)da_push_back_new(testarray) = 2;
	*(uint8_t *)da_push_back_new(testarray) = 3;
	*(uint8_t *)da_push_back_new(testarray) = 4;
	da_erase_range(testarray, 1, 3);
	assert_int_equal(testarray.num, 2);
	assert_int_equal(testarray.array[0], 1);
	assert_int_equal(testarray.array[1], 4);

	*(uint8_t *)darray_push_back_new(1, &testarray.da) = 5;
	assert_int_equal(testarray.array[2], 5);

	da_move_item(testarray, 1, 2);
	assert_int_equal(testarray.array[2], 4);
	assert_int_equal(testarray.array[1], 5);

	da_move_item(testarray, 1, 1);
	assert_int_equal(testarray.array[2], 4);
	assert_int_equal(testarray.array[1], 5);

	da_move_item(testarray, 2, 1);
	assert_int_equal(testarray.array[1], 4);
	assert_int_equal(testarray.array[2], 5);

	da_free(testarray);

	assert_int_equal(bnum_allocs(), 0);
}

static void array_error_test(void **state)
{
	assert_int_equal(darray_push_back_array(0, NULL, NULL, 0), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(array_basic_test),
		cmocka_unit_test(array_error_test),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
