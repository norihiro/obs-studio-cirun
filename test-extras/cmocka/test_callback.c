#include <stdio.h>
#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

#include <util/bmem.h>
#include <callback/calldata.h>
#include <callback/proc.h>
#include <callback/signal.h>

static void calldata_basic_test(void **state)
{
	UNUSED_PARAMETER(state);

	struct calldata *cd = calldata_create();

	assert_false(calldata_get_data(cd, "not-found", NULL, 0));

	calldata_set_string(cd, "string1", "1");
	calldata_set_string(cd, "string2", "2");

	calldata_free(cd);

	calldata_init(cd);
	calldata_set_string(cd, "string1", "short"); // 128 bytes will be allocated as the default.

	char data[512] = {0};
	calldata_set_data(cd, "data1", data, sizeof(data));

	assert_true(calldata_get_data(cd, "data1", data, sizeof(data)));
	assert_false(calldata_get_data(cd, "data1", data, sizeof(data) / 2));

	calldata_destroy(cd);

	assert_int_equal(bnum_allocs(), 0);
}

static void calldata_fixed_test(void **state)
{
	UNUSED_PARAMETER(state);

	struct calldata cd;
	uint8_t stack[16 + sizeof(size_t)* 3];
	const char *str;
	calldata_init_fixed(&cd, stack, sizeof(stack));

	assert_false(calldata_get_data(&cd, "not-found", NULL, 0));
	assert_false(calldata_get_string(&cd, "not-found", &str));

	calldata_set_string(&cd, "string", "value");
	assert_true(calldata_get_string(&cd, "string", &str));
	assert_string_equal(str, "value");

	// Expect error to write into the stack.
	calldata_set_string(&cd, "string1", "long string value");
	assert_true(calldata_get_string(&cd, "string", &str));
	assert_string_equal(str, "value");
	assert_false(calldata_get_string(&cd, "string1", &str));

	// Expect error so that the old string will be left.
	calldata_set_string(&cd, "string", "long string value");
	assert_true(calldata_get_string(&cd, "string", &str));
	assert_string_equal(str, "value");

	assert_false(calldata_get_string(&cd, "not-found", &str));

	assert_false(calldata_get_data(&cd, "", NULL, 0));

	assert_false(calldata_get_string(&cd, "", &str));

	assert_int_equal(bnum_allocs(), 0);
}

static void proc_failures(void **state)
{
	UNUSED_PARAMETER(state);

	proc_handler_destroy(NULL);
	proc_handler_add(NULL, NULL, NULL, NULL);
	assert_false(proc_handler_call(NULL, NULL, NULL));

	proc_handler_t *ph = proc_handler_create();

	// TODO: This will results crash:
	// proc_handler_add(ph, "", NULL, NULL);
	// proc_handler_call(ph, "f", NULL);

	proc_handler_add(ph, "a(", NULL, NULL);
	proc_handler_add(ph, "void a", NULL, NULL);
	proc_handler_add(ph, "void a(", NULL, NULL);
	proc_handler_add(ph, "void a(int", NULL, NULL);
	proc_handler_add(ph, "void void()", NULL, NULL);
	proc_handler_add(ph, "void a(x)", NULL, NULL);
	proc_handler_add(ph, "void a(in in x)", NULL, NULL);
	proc_handler_add(ph, "void a(out out x)", NULL, NULL);
	proc_handler_add(ph, "void a(int x, int x)", NULL, NULL);

	assert_false(proc_handler_call(ph, "b", NULL));

	proc_handler_add(ph, "void existing()", NULL, NULL);
	proc_handler_add(ph, "void existing()", NULL, NULL);

	proc_handler_destroy(ph);

	assert_int_equal(bnum_allocs(), 0);
}

static void remove_current(void *param, calldata_t *cd)
{
	UNUSED_PARAMETER(param);
	UNUSED_PARAMETER(cd);

	signal_handler_remove_current();
}

static void remove_current_global(void *param, const char *name, calldata_t *cd)
{
	UNUSED_PARAMETER(param);
	UNUSED_PARAMETER(name);
	UNUSED_PARAMETER(cd);

	signal_handler_remove_current();
}


static void signal_failures(void **state)
{
	UNUSED_PARAMETER(state);

	signal_handler_destroy(NULL);
	signal_handler_signal(NULL, NULL, NULL);

	signal_handler_t *sh = signal_handler_create();


	signal_handler_add(sh, "a(");

	signal_handler_signal(sh, "b", NULL);

	signal_handler_add(sh, "void existing()");
	signal_handler_add(sh, "void existing()");

	signal_handler_connect(sh, "existing", remove_current, NULL);
	signal_handler_connect_global(sh, remove_current_global, NULL);
	signal_handler_signal(sh, "existing", NULL);

	signal_handler_connect_global(sh, remove_current_global, NULL);
	signal_handler_disconnect_global(sh, remove_current_global, NULL);

	signal_handler_connect_global(NULL, NULL, NULL);
	signal_handler_disconnect_global(NULL, NULL, NULL);

	signal_handler_add_array(NULL, NULL);
	const char *bad_decls[] = {
		"void good()",
		"void",
		NULL
	};
	signal_handler_add_array(sh, bad_decls);

	signal_handler_destroy(sh);

	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(calldata_basic_test),
		cmocka_unit_test(calldata_fixed_test),
		cmocka_unit_test(proc_failures),
		cmocka_unit_test(signal_failures),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
