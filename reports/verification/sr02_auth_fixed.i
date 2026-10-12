             
             
#pragma pack(push,_CRT_PACKING)
  typedef __builtin_va_list __gnuc_va_list;
  typedef __gnuc_va_list va_list;
#pragma pack(pop)
void __attribute__((__cdecl__)) __debugbreak(void);
extern __inline__ __attribute__((__always_inline__,__gnu_inline__)) void __attribute__((__cdecl__)) __debugbreak(void)
{
  __asm__ __volatile__("int {$}3":);
}
const char *__mingw_get_crt_info (void);
#pragma pack(push,_CRT_PACKING)
__extension__ typedef unsigned long long size_t;
__extension__ typedef long long ssize_t;
typedef size_t rsize_t;
__extension__ typedef long long intptr_t;
__extension__ typedef unsigned long long uintptr_t;
__extension__ typedef long long ptrdiff_t;
typedef unsigned short wchar_t;
typedef unsigned short wint_t;
typedef unsigned short wctype_t;
typedef int errno_t;
typedef long __time32_t;
__extension__ typedef long long __time64_t;
typedef __time64_t time_t;
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
  void __attribute__((__cdecl__)) __attribute__ ((__nothrow__)) exit(int _Code) __attribute__ ((__noreturn__));
  void __attribute__((__cdecl__)) __attribute__ ((__nothrow__)) _exit(int _Code) __attribute__ ((__noreturn__));
  void __attribute__((__cdecl__)) _Exit(int) __attribute__ ((__noreturn__));
       
  void __attribute__((__cdecl__)) __attribute__ ((__noreturn__)) abort(void);
       
extern void __attribute__((__cdecl__))
_wassert(const wchar_t *_Message,const wchar_t *_File,unsigned _Line);
extern void __attribute__((__cdecl__))
_assert (const char *_Message, const char *_File, unsigned _Line);
int main(void) {
    int connected;
    int authenticated;
    int charging;
    __CPROVER_assume(connected == 0 || connected == 1);
    __CPROVER_assume(authenticated == 0 || authenticated == 1);
    charging = connected && authenticated;
    (void) ((!!(!charging || authenticated)) || (_assert("!charging || authenticated","E:\\smart-ev-charging-safety\\formal\\bmc\\sr02_auth_fixed.c",14),0));
    return 0;
}
