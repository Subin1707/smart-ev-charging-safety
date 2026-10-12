# 1 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c"


# 1 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/assert.h" 1 3
# 15 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/assert.h" 3
# 1 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 1 3
# 10 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 3
# 1 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 1 3
# 12 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 3
# 1 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw_mac.h" 1 3
# 98 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw_mac.h" 3
             
# 107 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw_mac.h" 3
             
# 13 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 2 3
# 1 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw_secapi.h" 1 3
# 14 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 2 3
# 282 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 3
# 1 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/vadefs.h" 1 3
# 9 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/vadefs.h" 3
# 1 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 1 3
# 578 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 3
# 1 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/sdks/_mingw_directx.h" 1 3
# 579 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 2 3
# 1 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/sdks/_mingw_ddk.h" 1 3
# 580 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 2 3
# 10 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/vadefs.h" 2 3




#pragma pack(push,_CRT_PACKING)
# 24 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/vadefs.h" 3
  
# 24 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/vadefs.h" 3
 typedef __builtin_va_list __gnuc_va_list;






  typedef __gnuc_va_list va_list;
# 103 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/vadefs.h" 3
#pragma pack(pop)
# 283 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 2 3
# 552 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/_mingw.h" 3
void __attribute__((__cdecl__)) __debugbreak(void);
extern __inline__ __attribute__((__always_inline__,__gnu_inline__)) void __attribute__((__cdecl__)) __debugbreak(void)
{
  __asm__ __volatile__("int {$}3":);
}




const char *__mingw_get_crt_info (void);
# 11 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 2 3




#pragma pack(push,_CRT_PACKING)
# 35 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 3
__extension__ typedef unsigned long long size_t;
# 45 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 3
__extension__ typedef long long ssize_t;






typedef size_t rsize_t;
# 62 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 3
__extension__ typedef long long intptr_t;
# 75 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 3
__extension__ typedef unsigned long long uintptr_t;
# 88 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 3
__extension__ typedef long long ptrdiff_t;
# 98 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 3
typedef unsigned short wchar_t;







typedef unsigned short wint_t;
typedef unsigned short wctype_t;





typedef int errno_t;




typedef long __time32_t;




__extension__ typedef long long __time64_t;
# 138 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 3
typedef __time64_t time_t;
# 422 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/crtdefs.h" 3
struct threadlocaleinfostruct;
struct threadmbcinfostruct;
typedef struct threadlocaleinfostruct *pthreadlocinfo;
typedef struct threadmbcinfostruct *pthreadmbcinfo;
struct __lc_time_data;

typedef struct localeinfo_struct {
  pthreadlocinfo locinfo;
  pthreadmbcinfo mbcinfo;
} _locale_tstruct,*_locale_t;



typedef struct tagLC_ID {
  unsigned short wLanguage;
  unsigned short wCountry;
  unsigned short wCodePage;
} LC_ID,*LPLC_ID;




typedef struct threadlocaleinfostruct {
  int refcount;
  unsigned int lc_codepage;
  unsigned int lc_collate_cp;
  unsigned long lc_handle[6];
  LC_ID lc_id[6];
  struct {
    char *locale;
    wchar_t *wlocale;
    int *refcount;
    int *wrefcount;
  } lc_category[6];
  int lc_clike;
  int mb_cur_max;
  int *lconv_intl_refcount;
  int *lconv_num_refcount;
  int *lconv_mon_refcount;
  struct lconv *lconv;
  int *ctype1_refcount;
  unsigned short *ctype1;
  const unsigned short *pctype;
  const unsigned char *pclmap;
  const unsigned char *pcumap;
  struct __lc_time_data *lc_time_curr;
} threadlocinfo;







#pragma pack(pop)
# 16 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/assert.h" 2 3
# 26 "C:/Program Files/CodeBlocks/MinGW/x86_64-w64-mingw32/include/assert.h" 3
  void __attribute__((__cdecl__)) __attribute__ ((__nothrow__)) exit(int _Code) __attribute__ ((__noreturn__));
  void __attribute__((__cdecl__)) __attribute__ ((__nothrow__)) _exit(int _Code) __attribute__ ((__noreturn__));



  void __attribute__((__cdecl__)) _Exit(int) __attribute__ ((__noreturn__));






       

  void __attribute__((__cdecl__)) __attribute__ ((__noreturn__)) abort(void);
       



extern void __attribute__((__cdecl__))
_wassert(const wchar_t *_Message,const wchar_t *_File,unsigned _Line);
extern void __attribute__((__cdecl__))
_assert (const char *_Message, const char *_File, unsigned _Line);
# 4 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c" 2


# 5 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c"
extern float nondet_float(void);


int main(void)
{
    float soc = nondet_float();

    __CPROVER_assume(soc >= 0.0f);

    
# 14 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c" 3
   (void) ((!!(
# 14 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c"
   (soc >= 0.0f && soc <= 100.0f)
# 14 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c" 3
   )) || (_assert(
# 14 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c"
   "(soc >= 0.0f && soc <= 100.0f)"
# 14 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c" 3
   ,"E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c",14),0))
# 14 "E:\\smart-ev-charging-safety\\generated\\static\\SR09_cbmc.c"
                                         ;

    return 0;
}
