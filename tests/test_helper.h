#ifndef TEST_HELPER_H
#define TEST_HELPER_H

#include <stdio.h>
#include <math.h>

static int g_tests_run = 0;
static int g_tests_passed = 0;
static int g_tests_failed = 0;

#define ASSERT_TRUE(cond, msg) do { \
    g_tests_run++; \
    if (cond) { \
        g_tests_passed++; \
        printf("  [PASS] %s\n", msg); \
    } else { \
        g_tests_failed++; \
        printf("  [FAIL] %s (Line %d)\n", msg, __LINE__); \
    } \
} while (0)

#define ASSERT_FALSE(cond, msg) ASSERT_TRUE(!(cond), msg)

#define ASSERT_EQ(a, b, msg) ASSERT_TRUE((a) == (b), msg)

#define ASSERT_FLOAT_EQ(a, b, eps, msg) ASSERT_TRUE(fabs((a) - (b)) <= (eps), msg)

#define PRINT_TEST_RESULT(test_name) do { \
    printf("--------------------------------------------------\n"); \
    printf("TEST SUITE: %s\n", test_name); \
    printf("Total: %d | Passed: %d | Failed: %d | Status: %s\n", \
           g_tests_run, g_tests_passed, g_tests_failed, \
           (g_tests_failed == 0) ? "SUCCESS" : "FAILURE"); \
    printf("--------------------------------------------------\n\n"); \
} while (0)

#endif /* TEST_HELPER_H */
