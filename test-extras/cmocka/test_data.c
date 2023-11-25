#include <stdio.h>
#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

#include <util/bmem.h>
#include <obs-data.h>

static void data_basic_test(void **state)
{
	UNUSED_PARAMETER(state);

	obs_data_t *data = obs_data_create();
	obs_data_t *data1;
	obs_data_array_t *array;
	obs_data_array_t *array1;

	array = obs_data_array_create();
	data1 = obs_data_create();
	obs_data_set_int(data1, "array-item", -2);
	obs_data_array_push_back(array, data1);
	obs_data_release(data1);

	data1 = obs_data_create();
	obs_data_set_int(data1, "array-item", -1);
	obs_data_array_insert(array, 0, data1);
	obs_data_release(data1);

	data1 = obs_data_create();
	obs_data_set_int(data1, "array-item", -4);
	obs_data_array_insert(array, 0, data1);
	obs_data_release(data1);
	assert_int_equal(obs_data_array_count(array), 3);

	obs_data_array_erase(array, 0);
	assert_int_equal(obs_data_array_count(array), 2);

	obs_data_set_string(data, "string", "val");
	obs_data_set_int(data, "int", 1234);
	obs_data_set_double(data, "double", 34.12);
	obs_data_set_bool(data, "bool1", true);
	obs_data_set_bool(data, "bool0", false);
	data1 = obs_data_create();
	obs_data_set_int(data1, "key1", 1);
	obs_data_set_obj(data, "data", data1);
	obs_data_release(data1);
	obs_data_set_array(data, "array", array);

	obs_data_set_default_string(data, "string", "default");
	obs_data_set_default_int(data, "int", 12);
	obs_data_set_default_double(data, "double", 1.2);
	obs_data_set_default_bool(data, "bool1", false);
	obs_data_set_default_bool(data, "bool0", true);
	data1 = obs_data_create();
	obs_data_set_int(data1, "key2", 2);
	obs_data_set_default_obj(data, "data", data1);
	obs_data_release(data1);
	obs_data_set_default_array(data, "array-default", array);

	obs_data_set_autoselect_string(data, "string", "auto");
	obs_data_set_autoselect_int(data, "int", 10);
	obs_data_set_autoselect_double(data, "double", 1.05);
	obs_data_set_autoselect_bool(data, "bool1", false);
	obs_data_set_autoselect_bool(data, "bool0", false);
	data1 = obs_data_create();
	obs_data_set_int(data1, "key3", 3);
	obs_data_set_autoselect_obj(data, "data", data1);
	obs_data_set_autoselect_array(data, "array_as", array);
	obs_data_release(data1);

	obs_data_array_release(array);

	assert_string_equal(obs_data_get_string(data, "string"), "val");
	assert_int_equal(obs_data_get_int(data, "int"), 1234);
	assert_float_equal(obs_data_get_double(data, "double"), 34.12, 1e-4);
	assert_int_equal(obs_data_get_bool(data, "bool1"), true);
	assert_int_equal(obs_data_get_bool(data, "bool0"), false);

	assert_string_equal(obs_data_get_default_string(data, "string"), "default");
	assert_int_equal(obs_data_get_default_int(data, "int"), 12);
	assert_float_equal(obs_data_get_default_double(data, "double"), 1.2, 1e-4);
	assert_int_equal(obs_data_get_default_bool(data, "bool1"), false);
	assert_int_equal(obs_data_get_default_bool(data, "bool0"), true);

	assert_string_equal(obs_data_get_autoselect_string(data, "string"), "auto");
	assert_int_equal(obs_data_get_autoselect_int(data, "int"), 10);
	assert_float_equal(obs_data_get_autoselect_double(data, "double"), 1.05, 1e-4);
	assert_int_equal(obs_data_get_autoselect_bool(data, "bool1"), false);
	assert_int_equal(obs_data_get_autoselect_bool(data, "bool0"), false);

	assert_int_equal(obs_data_has_default_value(data, "bool1"), true);
	assert_int_equal(obs_data_has_default_value(data, "bool2"), false);

	obs_data_set_autoselect_string(data, "move", "autoselect");
	obs_data_set_default_string(data, "move", "default");
	assert_string_equal(obs_data_get_string(data, "move"), "default");
	assert_string_equal(obs_data_get_autoselect_string(data, "move"), "autoselect");

	array1 = obs_data_get_autoselect_array(data, "array_as");
	assert_ptr_not_equal(array1, NULL);
	obs_data_array_release(array1);

	data1 = obs_data_get_defaults(data);
	assert_string_equal(obs_data_get_string(data1, "string"), "default");
	assert_int_equal(obs_data_get_int(data1, "int"), 12);
	assert_float_equal(obs_data_get_double(data1, "double"), 1.2, 1e-4);
	assert_int_equal(obs_data_get_bool(data1, "bool1"), false);
	assert_int_equal(obs_data_get_bool(data1, "bool0"), true);
	obs_data_release(data1);

	data1 = obs_data_get_autoselect_obj(data, "data");
	assert_ptr_not_equal(data1, NULL);
	obs_data_release(data1);

	// remove values and check it
	assert_int_equal(obs_data_get_bool(data, "bool0"), false);
	obs_data_unset_user_value(data, "bool0");
	assert_int_equal(obs_data_get_bool(data, "bool0"), true);
	obs_data_unset_default_value(data, "bool0");
	assert_int_equal(obs_data_get_bool(data, "bool0"), false);

	assert_int_equal(obs_data_has_autoselect_value(data, "bool0"), true);
	obs_data_unset_autoselect_value(data, "bool0");
	assert_int_equal(obs_data_has_autoselect_value(data, "bool0"), false);

	obs_data_release(data);

	assert_int_equal(bnum_allocs(), 0);
}

static void json_errors(void **state)
{
	UNUSED_PARAMETER(state);

	assert_ptr_equal(obs_data_create_from_json("[{[\"error\""), NULL);

	FILE *fp = fopen("json_errors.json", "w");
	fputs("{[\"error\"", fp);
	fclose(fp);

	fp = fopen("json_errors.json.bak", "w");
	fputs("{\"ok\": true}", fp);
	fclose(fp);

	obs_data_t *data = obs_data_create_from_json_file_safe("json_errors.json", ".bak");
	assert_ptr_not_equal(data, NULL);

	assert_int_equal(obs_data_save_json_pretty_safe(data, "json_saved.json", ".tmp", ".bak"), true);
	char line[64];
	fp = fopen("json_saved.json", "r");
	assert_string_equal(fgets(line, sizeof(line), fp), "{\n");
	assert_string_equal(fgets(line, sizeof(line), fp), "    \"ok\": true\n");
	assert_string_equal(fgets(line, sizeof(line), fp), "}");
	fclose(fp);

	assert_int_equal(obs_data_save_json(data, "json_saved.json"), true);
	fp = fopen("json_saved.json", "r");
	assert_string_equal(fgets(line, sizeof(line), fp), "{\"ok\":true}");
	fclose(fp);

	obs_data_release(data);

	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(data_basic_test),
		cmocka_unit_test(json_errors),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
