#include <stdlib.h>
#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

#include <obs.h>
#include <media-io/video-frame.h>
#include <media-io/video-scaler.h>
#include <media-io/format-conversion.h>
#include <media-io/media-remux.h>
#include <media-io/audio-io.h>

static void video_frame_test(void **state)
{
	UNUSED_PARAMETER(state);

	const enum video_format formats[] = {
		VIDEO_FORMAT_I420, /* three-plane */
		VIDEO_FORMAT_NV12, /* two-plane, luma and packed chroma */

		/* packed 4:2:2 formats */
		VIDEO_FORMAT_YVYU,
		VIDEO_FORMAT_YUY2, /* YUYV */
		VIDEO_FORMAT_UYVY,

		/* packed uncompressed formats */
		VIDEO_FORMAT_RGBA,
		VIDEO_FORMAT_BGRA,
		VIDEO_FORMAT_BGRX,
		VIDEO_FORMAT_Y800, /* grayscale */

		/* planar 4:4:4 */
		VIDEO_FORMAT_I444,

		/* more packed uncompressed formats */
		VIDEO_FORMAT_BGR3,

		/* planar 4:2:2 */
		VIDEO_FORMAT_I422,

		/* planar 4:2:0 with alpha */
		VIDEO_FORMAT_I40A,

		/* planar 4:2:2 with alpha */
		VIDEO_FORMAT_I42A,

		/* planar 4:4:4 with alpha */
		VIDEO_FORMAT_YUVA,

		/* packed 4:4:4 with alpha */
		VIDEO_FORMAT_AYUV,

		/* planar 4:2:0 format, 10 bpp */
		VIDEO_FORMAT_I010, /* three-plane */
		VIDEO_FORMAT_P010, /* two-plane, luma and packed chroma */

		/* planar 4:2:2 format, 10 bpp */
		VIDEO_FORMAT_I210,

		/* planar 4:4:4 format, 12 bpp */
		VIDEO_FORMAT_I412,

		/* planar 4:4:4:4 format, 12 bpp */
		VIDEO_FORMAT_YA2L,

		/* planar 4:2:2 format, 16 bpp */
		VIDEO_FORMAT_P216, /* two-plane, luma and packed chroma */

		/* planar 4:4:4 format, 16 bpp */
		VIDEO_FORMAT_P416, /* two-plane, luma and packed chroma */

		/* packed 4:2:2 format, 10 bpp */
		VIDEO_FORMAT_V210,
	};

	for (size_t i = 0; i < sizeof(formats) / sizeof(*formats); i++) {
		const enum video_format format = formats[i];
		const int width = 320;
		const int height = 180;

		struct video_frame *frame1 = video_frame_create(format, width, height);

		struct video_frame frame2;
		video_frame_init(&frame2, format, width, height);

		video_frame_copy(&frame2, frame1, format, height);

		video_frame_destroy(frame1);
		video_frame_free(&frame2);
	}

	assert_int_equal(bnum_allocs(), 0);
}

static void remux_errors(void **state)
{
	UNUSED_PARAMETER(state);

	assert_int_equal(media_remux_job_create(NULL, NULL, NULL), false);
	assert_int_equal(media_remux_job_process(NULL, NULL, NULL), false);
	media_remux_job_destroy(NULL);

	media_remux_job_t job = NULL;
	assert_int_equal(media_remux_job_create(&job, NULL, NULL), NULL);
	assert_ptr_equal(job, NULL);
	assert_int_equal(media_remux_job_create(&job, "a.mkv", NULL), NULL);
	assert_ptr_equal(job, NULL);
	assert_int_equal(media_remux_job_create(&job, "", ""), NULL);
	assert_ptr_equal(job, NULL);

	assert_int_equal(bnum_allocs(), 0);
}

static void videoscaler_errors(void **state)
{
	UNUSED_PARAMETER(state);

	struct video_scale_info src = {.format = VIDEO_FORMAT_NONE}, dst = {.format = VIDEO_FORMAT_NONE};
	assert_int_equal(video_scaler_create(NULL, &src, &dst, 0), VIDEO_SCALER_FAILED);

	assert_int_equal(bnum_allocs(), 0);
}

static void frame_rate(void **state)
{
	UNUSED_PARAMETER(state);

	struct media_frames_per_second fps = {30000, 1001};

	assert_float_equal(media_frames_per_second_to_frame_interval(fps), 0.033366, 1e-4);
	assert_float_equal(media_frames_per_second_to_fps(fps), 29.97, 0.01);
	assert_int_equal(media_frames_per_second_is_valid(fps), true);

	assert_int_equal(bnum_allocs(), 0);
}

static void audio_io_test(void **state)
{
	UNUSED_PARAMETER(state);

	assert_int_equal(get_audio_bytes_per_channel(AUDIO_FORMAT_U8BIT), 1);
	assert_int_equal(get_audio_bytes_per_channel(AUDIO_FORMAT_16BIT), 2);
	assert_int_equal(get_audio_bytes_per_channel(AUDIO_FORMAT_32BIT), 4);
	assert_int_equal(get_audio_bytes_per_channel(AUDIO_FORMAT_FLOAT), 4);
	assert_int_equal(get_audio_bytes_per_channel(AUDIO_FORMAT_U8BIT_PLANAR), 1);
	assert_int_equal(get_audio_bytes_per_channel(AUDIO_FORMAT_16BIT_PLANAR), 2);
	assert_int_equal(get_audio_bytes_per_channel(AUDIO_FORMAT_32BIT_PLANAR), 4);
	assert_int_equal(get_audio_bytes_per_channel(AUDIO_FORMAT_FLOAT_PLANAR), 4);
	assert_int_equal(get_audio_bytes_per_channel(AUDIO_FORMAT_UNKNOWN), 0);
	assert_int_equal(get_audio_bytes_per_channel(-1), 0);

	assert_int_equal(is_audio_planar(AUDIO_FORMAT_U8BIT), false);
	assert_int_equal(is_audio_planar(AUDIO_FORMAT_16BIT), false);
	assert_int_equal(is_audio_planar(AUDIO_FORMAT_32BIT), false);
	assert_int_equal(is_audio_planar(AUDIO_FORMAT_FLOAT), false);
	assert_int_equal(is_audio_planar(AUDIO_FORMAT_U8BIT_PLANAR), true);
	assert_int_equal(is_audio_planar(AUDIO_FORMAT_16BIT_PLANAR), true);
	assert_int_equal(is_audio_planar(AUDIO_FORMAT_32BIT_PLANAR), true);
	assert_int_equal(is_audio_planar(AUDIO_FORMAT_FLOAT_PLANAR), true);
	assert_int_equal(is_audio_planar(AUDIO_FORMAT_UNKNOWN), false);
	assert_int_equal(is_audio_planar(-1), false);

	assert_int_equal(get_audio_channels(SPEAKERS_UNKNOWN), 0);
	assert_int_equal(get_audio_channels(-1), 0);
	assert_int_equal(get_total_audio_size(AUDIO_FORMAT_FLOAT_PLANAR, SPEAKERS_MONO, 1024), 4 * 1 * 1024);
	assert_int_equal(get_total_audio_size(AUDIO_FORMAT_FLOAT_PLANAR, SPEAKERS_STEREO, 1024), 4 * 2 * 1024);
	assert_int_equal(get_total_audio_size(AUDIO_FORMAT_FLOAT_PLANAR, SPEAKERS_2POINT1, 1024), 4 * 3 * 1024);
	assert_int_equal(get_total_audio_size(AUDIO_FORMAT_FLOAT_PLANAR, SPEAKERS_4POINT0, 1024), 4 * 4 * 1024);
	assert_int_equal(get_total_audio_size(AUDIO_FORMAT_FLOAT_PLANAR, SPEAKERS_4POINT1, 1024), 4 * 5 * 1024);
	assert_int_equal(get_total_audio_size(AUDIO_FORMAT_FLOAT_PLANAR, SPEAKERS_5POINT1, 1024), 4 * 6 * 1024);
	assert_int_equal(get_total_audio_size(AUDIO_FORMAT_FLOAT_PLANAR, SPEAKERS_7POINT1, 1024), 4 * 8 * 1024);

	assert_int_equal(bnum_allocs(), 0);
}

static void rand_data(uint8_t *data, size_t size)
{
	for (size_t i = 0; i < size; i++)
		data[i] = rand() / (RAND_MAX / 256);
}

static void replace_vuyx_with_uyvx(struct video_frame *frame, size_t height)
{
	const size_t width = frame->linesize[0] / 4;
	for (size_t y = 0; y < height; y++) {
		uint32_t *data = (uint32_t *)(frame->data[0] + y * frame->linesize[0]);
		for (size_t x = 0; x < width; x++) {
			uint32_t xyuv = data[x];
			uint32_t xvyu = ((xyuv & 0xFF0000) >> 8) | ((xyuv & 0xFF) << 16) | ((xyuv & 0xFF00) >> 8);
			data[x] = xvyu;
		}
	}
}

static void replace_yuvx_with_uyvx(struct video_frame *frame, size_t height)
{
	const size_t width = frame->linesize[0] / 4;
	for (size_t y = 0; y < height; y++) {
		uint32_t *data = (uint32_t *)(frame->data[0] + y * frame->linesize[0]);
		for (size_t x = 0; x < width; x++) {
			uint32_t xvuy = data[x];
			uint32_t xvyu = ((xvuy & 0xFF) << 8) | ((xvuy & 0xFF00) >> 8) | ((xvuy & 0xFF0000));
			data[x] = xvyu;
		}
	}
}

static bool comp_data(const uint8_t *data1, const uint8_t *data2, size_t size)
{
	int diff_max = 0;
	for (size_t i = 0; i < size; i++) {
		int diff = (int)data1[i] - data2[i];
		// printf("comp_data i=%d data1=%x dat2=%x diff=%d\n", i, data1[i], data2[i], diff);
		if (diff > diff_max)
			diff_max = diff;
		else if (-diff > diff_max)
			diff_max = -diff;
	}
	return diff_max < 2;
}

static void frame_format_conversion_test_420(void **state)
{
	UNUSED_PARAMETER(state);

	const size_t width = 64;
	const size_t height = 48;

	struct video_frame frame0, frame1, frame2;
	size_t size;

	video_frame_init(&frame0, VIDEO_FORMAT_I420, width, height);
	video_frame_init(&frame1, VIDEO_FORMAT_AYUV, width, height);
	video_frame_init(&frame2, VIDEO_FORMAT_I420, width, height);
	size = width * height * (4 + 1 + 1) / 4;
	rand_data(frame0.data[0], size);

	// I420 -> VUYX
	// TODO: the output format is not documented.
	decompress_420((const uint8_t *const *)frame0.data, frame0.linesize, 0, height, frame1.data[0],
		       frame1.linesize[0]);

	replace_vuyx_with_uyvx(&frame1, height);

	compress_uyvx_to_i420(frame1.data[0], frame1.linesize[0], 0, height, frame2.data, frame2.linesize);

	assert_true(comp_data(frame0.data[0], frame2.data[0], size));

	video_frame_free(&frame2);
	video_frame_free(&frame1);
	video_frame_free(&frame0);

	assert_int_equal(bnum_allocs(), 0);
}

static void frame_format_conversion_test_nv12(void **state)
{
	UNUSED_PARAMETER(state);

	const size_t width = 64;
	const size_t height = 48;

	struct video_frame frame0, frame1, frame2;
	size_t size;

	video_frame_init(&frame0, VIDEO_FORMAT_NV12, width, height);
	video_frame_init(&frame1, VIDEO_FORMAT_AYUV, width, height);
	video_frame_init(&frame2, VIDEO_FORMAT_NV12, width, height);
	size = width * height * (2 + 1) / 2;
	rand_data(frame0.data[0], size);

	// NV12 -> YUVX
	// TODO: the output format is not documented.
	decompress_nv12((const uint8_t *const *)frame0.data, frame0.linesize, 0, height, frame1.data[0],
			frame1.linesize[0]);

	replace_yuvx_with_uyvx(&frame1, height);

	compress_uyvx_to_nv12(frame1.data[0], frame1.linesize[0], 0, height, frame2.data, frame2.linesize);

	assert_true(comp_data(frame0.data[0], frame2.data[0], size));

	video_frame_free(&frame2);
	video_frame_free(&frame1);
	video_frame_free(&frame0);

	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(video_frame_test),
		cmocka_unit_test(remux_errors),
		cmocka_unit_test(videoscaler_errors),
		cmocka_unit_test(frame_rate),
		cmocka_unit_test(audio_io_test),
		cmocka_unit_test(frame_format_conversion_test_420),
		cmocka_unit_test(frame_format_conversion_test_nv12),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
