
#include <assert.h>

#ifdef _WIN32
#include "windows.h"
#else
#include <dlfcn.h>
#endif

int func_in_y();

int main()
{
#ifdef _WIN32
    HINSTANCE hDLL = hDLL = LoadLibrary("build\\example\\sharedlib-demo\\libx.dll");
    assert(hDLL);

    typedef int (*DLLPROC)();
    DLLPROC func_in_x = (DLLPROC)GetProcAddress(hDLL, "func_in_x");
    assert(func_in_x);
#else
    void* handle = dlopen("build/example/sharedlib-demo/libx.dll", RTLD_LAZY);
    assert(handle);

    typedef int (*FuncType)();
    FuncType func_in_x = (FuncType)dlsym(handle, "func_in_x");
    assert(func_in_x);
#endif

    func_in_x();
    func_in_y();
    return 0;
}