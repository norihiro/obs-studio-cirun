#include <stdio.h>
#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
extern "C" {
#include <cmocka.h>
}

#include <util/bmem.h>
#include <obs.hpp>
#include <obs-data.h>

static void weak(void **state)
{
	UNUSED_PARAMETER(state);

	OBSGetStrongRef((obs_weak_output_t *)nullptr);
	OBSGetStrongRef((obs_weak_encoder_t *)nullptr);
	OBSGetStrongRef((obs_weak_service_t *)nullptr);

	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(weak),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
