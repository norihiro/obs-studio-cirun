#include <stdio.h>
#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

#include <util/bmem.h>
#include <graphics/quat.h>
#include <graphics/axisang.h>

static void axisang_test(void **state)
{
	UNUSED_PARAMETER(state);

	struct axisang a, a1;
	struct quat q;

	axisang_zero(&a);
	assert_float_equal(a.x, 0.0, 1e-7);
	assert_float_equal(a.y, 0.0, 1e-7);
	assert_float_equal(a.z, 0.0, 1e-7);
	assert_float_equal(a.w, 0.0, 1e-7);

	q.x = 0.0f;
	q.y = 0.0f;
	q.z = 0.0f;
	q.w = 0.0f;
	axisang_from_quat(&a, &q);
	assert_float_equal(a.x, 0.0, 1e-7);
	assert_float_equal(a.y, 0.0, 1e-7);
	assert_float_equal(a.z, 0.0, 1e-7);
	assert_float_equal(a.w, 0.0, 1e-7);

	q.x = +1.0f;
	q.y = +1.0f;
	q.z = 0.0f;
	q.w = 0.0f;
	axisang_from_quat(&a, &q);
	assert_float_equal(a.x * a.x + a.y * a.y + a.z * a.z, 1.0, 1e-4);

	axisang_copy(&a1, &a);
	assert_memory_equal(&a1, &a, sizeof(struct axisang));

	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(axisang_test),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
