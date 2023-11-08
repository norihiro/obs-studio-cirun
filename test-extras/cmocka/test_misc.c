#include <stdio.h>
#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

#include <util/bmem.h>
#include <obs.h>

static void obs_h(void **state)
{
	UNUSED_PARAMETER(state);

	obs_startup("C", NULL, NULL);

	obs_scene_t *scene1 = obs_scene_create("scene1");
	obs_scene_t *scene;

	assert_ptr_equal(obs_get_scene_by_name(""), NULL);
	assert_ptr_equal(scene = obs_get_scene_by_name("scene1"), scene1);
	obs_scene_release(scene);

	assert_ptr_equal(obs_group_or_scene_from_source(NULL), NULL);

	obs_scene_release(scene1);

	obs_shutdown();
	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(obs_h),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
