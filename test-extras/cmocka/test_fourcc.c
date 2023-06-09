#include <stdarg.h>
#include <stdint.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>
#include <media-io/video-io.h>

static void fourcc_test(void **state)
{
	UNUSED_PARAMETER(state);

	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"UYVY"), VIDEO_FORMAT_UYVY);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"HDYC"), VIDEO_FORMAT_UYVY);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"UYNY"), VIDEO_FORMAT_UYVY);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"uyv1"), VIDEO_FORMAT_UYVY);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"2vuy"), VIDEO_FORMAT_UYVY);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"2Vuy"), VIDEO_FORMAT_UYVY);

	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"YUY2"), VIDEO_FORMAT_YUY2);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"Y422"), VIDEO_FORMAT_YUY2);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"V422"), VIDEO_FORMAT_YUY2);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"VYUY"), VIDEO_FORMAT_YUY2);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"yuv2"), VIDEO_FORMAT_YUY2);
	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"yuvs"), VIDEO_FORMAT_YUY2);

	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"YVYU"), VIDEO_FORMAT_YVYU);

	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"Y800"), VIDEO_FORMAT_Y800);

	assert_int_equal(video_format_from_fourcc(*(uint32_t *)"none"), VIDEO_FORMAT_NONE);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(fourcc_test),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
