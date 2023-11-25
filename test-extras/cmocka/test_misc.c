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
	assert_int_equal(obs_obj_is_private(obs_scene_get_source(scene1)), false);

	obs_scene_t *scene;

	assert_ptr_equal(obs_get_scene_by_name(""), NULL);
	assert_ptr_equal(scene = obs_get_scene_by_name("scene1"), scene1);
	obs_scene_release(scene);

	assert_ptr_equal(obs_group_or_scene_from_source(NULL), NULL);

	obs_reset_source_uuids();
	assert_ptr_equal(scene = obs_get_scene_by_name("scene1"), scene1);
	obs_scene_release(scene);

	obs_scene_release(scene1);

	assert_string_equal(obs_source_get_display_name("scene"), "Scene");
	assert_string_equal(obs_source_get_display_name("group"), "Group");

	obs_shutdown();
	assert_int_equal(bnum_allocs(), 0);
}

static void set_get_locale(void **state)
{
	UNUSED_PARAMETER(state);

	assert_int_equal(obs_initialized(), false);
	obs_startup("C", NULL, NULL);
	assert_int_equal(obs_initialized(), true);

	assert_string_equal(obs_get_locale(), "C");
	obs_set_locale("en-US");
	assert_string_equal(obs_get_locale(), "en-US");

	obs_shutdown();
	assert_int_equal(obs_initialized(), false);

	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(obs_h),
		cmocka_unit_test(set_get_locale),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
