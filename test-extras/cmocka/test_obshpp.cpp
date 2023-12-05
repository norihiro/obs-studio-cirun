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

typedef unsigned int ULONG;
#include <util/windows/ComPtr.hpp>

static void weak(void **state)
{
	UNUSED_PARAMETER(state);

	OBSGetStrongRef((obs_weak_output_t *)nullptr);
	OBSGetStrongRef((obs_weak_encoder_t *)nullptr);
	OBSGetStrongRef((obs_weak_service_t *)nullptr);

	assert_int_equal(bnum_allocs(), 0);
}

struct Obj {
	void *ptr;
	int refcnt = 0;
	int addcnt = 0;
	Obj()
	{
		printf("Obj [%p] created refcnt=%d\n", this, refcnt);
		ptr = bmalloc(1);
	}
	virtual ~Obj()
	{
		printf("Obj [%p] destroyed refcnt=%d\n", this, refcnt);
		assert_int_equal(refcnt, -1);
		bfree(ptr);
	}

	void AddRef()
	{
		assert_true(refcnt >= 0);
		refcnt++;
		addcnt++;
	}

	ULONG Release()
	{
		assert_true(refcnt >= 0);
		ULONG ret = (ULONG)refcnt;
		if (refcnt-- == 0)
			delete this;
		return ret;
	}
};

struct Obj1 : public Obj {};

static ComPtr<Obj> create_object()
{
	ComPtr<Obj> o(new Obj);
	o->Release();
	return o;
}

static ComPtr<Obj1> create_object1()
{
	ComPtr<Obj1> o(new Obj1);
	o->Release();
	return o;
}

static void comptr(void **)
{
	{
		ComPtr<Obj> ptr1;
		assert_ptr_equal(ptr1.Get(), nullptr);
	}

	{
		ComPtr<Obj> ptr1(new Obj);
		ptr1.Get()->Release();
		assert_int_equal(ptr1.Get()->refcnt, 0);
	}

	{
		ComPtr<Obj> ptr1(new Obj);
		ptr1.Get()->Release();

		ComPtr<Obj> ptr2(ptr1);
		assert_int_equal(ptr1.Get()->refcnt, 1);
		assert_int_equal(ptr1.Get()->addcnt, 2);
		assert_ptr_equal(ptr1.Get(), ptr2.Get());
	}

	{
		// ComPtr(ComPtr<T> &&c) noexcept
		ComPtr<Obj> ptr1(create_object());
		assert_int_equal(ptr1.Get()->refcnt, 0);
		assert_int_equal(ptr1.Get()->addcnt, 1);
	}

	{
		// template<class U> ComPtr(ComPtr<U> &&c) noexcept
		ComPtr<Obj> ptr1(create_object1());
		assert_int_equal(ptr1.Get()->refcnt, 0);
		assert_int_equal(ptr1.Get()->addcnt, 1);
	}

	{
		// ComPtr<T> &operator=(ComPtr<T> &&c) noexcept
		ComPtr<Obj> ptr1;
		ptr1 = ptr1 = create_object();
		assert_int_equal(ptr1.Get()->refcnt, 0);
		assert_int_equal(ptr1.Get()->addcnt, 1);
	}

	{
		// template<class U> ComPtr<T> &operator=(ComPtr<U> &&c) noexcept
		ComPtr<Obj> ptr1;
		ptr1 = ptr1 = create_object1();
		assert_int_equal(ptr1.Get()->refcnt, 0);
		assert_int_equal(ptr1.Get()->addcnt, 1);
	}

	{
		ComPtr<Obj> ptr1(new Obj);
		ptr1.Get()->Release();
		Obj *p;
		ptr1.CopyTo(&p);
		assert_ptr_equal(ptr1.Get(), p);
		assert_int_equal(p->refcnt, 1);
		assert_int_equal(p->addcnt, 2);
		p->Release();
	}

	{
		ComPtr<Obj> ptr1(new Obj);
		ptr1.Get()->Release();
		assert_int_equal(ptr1.Release(), 0);
		assert_int_equal(ptr1.Release(), 0);
		assert_ptr_equal(ptr1.Get(), nullptr);
	}

	assert_int_equal(bnum_allocs(), 0);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(weak),
		cmocka_unit_test(comptr),
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
