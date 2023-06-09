#include <stdio.h>
#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

#include <util/config-file.h>
#include <util/bmem.h>

static void config_test(void **state)
{
	UNUSED_PARAMETER(state);

	config_t *cfg = config_create("test_config.ini");
	config_set_double(cfg, "section", "double-value", 12.5);
	config_save(cfg);
	config_close(cfg);
	cfg = NULL;

	config_open(&cfg, "test_config.ini", CONFIG_OPEN_EXISTING);
	assert_float_equal(config_get_double(cfg, "section", "double-value"), 12.5, 0.01);

	config_open_defaults(cfg, "test_config.ini");
	config_close(cfg);


	config_open(&cfg, "no-such-file.ini", CONFIG_OPEN_ALWAYS);
	config_close(cfg);

	assert_int_equal(bnum_allocs(), 0);
}

static void config_escape_test(void **state)
{
	config_t *cfg;
	config_open_string(&cfg, "[s]\nvalue=a\\nb\\rc\\\\d\n# this is a comment.");
	assert_string_equal(config_get_string(cfg, "s", "value"), "a\nb\rc\\d");

	config_close(cfg);

	assert_int_equal(bnum_allocs(), 0);
}

static void config_default_test(void **state)
{
	config_t *cfg;
	config_open_string(&cfg, "");

	config_set_default_string(cfg, "section", "string", "default");
	assert_string_equal(config_get_default_string(cfg, "section", "string"), "default");

	config_set_default_int(cfg, "section", "int", -1151);
	assert_int_equal(config_get_default_int(cfg, "section", "int"), -1151);

	config_set_default_uint(cfg, "section", "uint", 151);
	assert_int_equal(config_get_default_uint(cfg, "section", "uint"), 151);

	config_set_default_bool(cfg, "section", "bool", true);
	assert_int_equal(config_get_default_bool(cfg, "section", "bool"), true);

	config_set_default_double(cfg, "section", "double", 0.91);
	assert_float_equal(config_get_default_double(cfg, "section", "double"), 0.91, 0.001);

	assert_int_equal(config_has_default_value(cfg, "section", "double"), true);

	assert_ptr_equal(config_get_default_string(cfg, "section", "none"), NULL);
	assert_int_equal(config_get_default_int(cfg, "section", "none"), 0);
	assert_int_equal(config_get_default_uint(cfg, "section", "none"), 0);
	assert_int_equal(config_get_default_bool(cfg, "section", "none"), false);
	assert_float_equal(config_get_default_double(cfg, "section", "none"), 0.0, 0.001);

	config_set_default_string(cfg, "section", "int_hex", "0x10");
	assert_int_equal(config_get_default_int(cfg, "section", "int_hex"), 16);
	assert_int_equal(config_get_default_uint(cfg, "section", "int_hex"), 16);

	config_set_default_string(cfg, "section", "empty", NULL);
	assert_int_equal(config_get_default_int(cfg, "section", "empty"), 0);
	assert_int_equal(config_get_default_uint(cfg, "section", "empty"), 0);

	assert_int_equal(config_get_default_int(cfg, "none", "none"), 0);

	config_close(cfg);

	assert_int_equal(bnum_allocs(), 0);
}

static void config_error_test(void **state)
{
	config_t *cfg;

	config_open_string(&cfg, "[s]\nvalue\n");
	config_close(cfg);

	cfg = NULL;
	config_open_string(&cfg, "  a\n");
	config_close(cfg);

	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(config_test),
		cmocka_unit_test(config_escape_test),
		cmocka_unit_test(config_default_test),
		cmocka_unit_test(config_error_test),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
