
#include <stdio.h>

#ifdef _WIN32
extern "C" __declspec(dllexport) int func_in_x();
#else
extern "C" int func_in_x();
#endif

int func_in_x()
{
    printf("test shredlib-demo\n");
    return 0;
}