import pytest
import os
import sys
from common.path_handler import get_allure_results_path, get_project_root
from common.log_handler import logger


def run_tests():
    """执行接口自动化用例"""
    # 1. 定义用例目录和报告目录（调用修正后的公共函数）
    try:
        project_root = get_project_root()
        # 修正：匹配实际目录名testcase（你的项目里是testcase，不是testcases）
        test_dir = os.path.join(project_root, "testcase")
        allure_results = get_allure_results_path()
        allure_report = os.path.join(project_root, "allure-report")

        # 校验用例目录（公共函数未覆盖的边界，补充判断）
        if not os.path.exists(test_dir):
            logger.error(f"测试用例目录不存在：{test_dir}")
            return 1
    except Exception as e:
        logger.error(f"公共函数调用失败（路径初始化）：{str(e)}")
        return 1

    # 2. 构建pytest执行参数（修正-n auto格式，解决多线程问题）
    pytest_args = [
        test_dir,
        "-v",
        "-s",
        "--alluredir", allure_results,
        "--clean-alluredir",
        "-n", "auto",  # 拆分参数 → 公共夹具多线程安全
        "--tb=short",
        # 新增：注册公共夹具目录（让用例能找到pytest_fixture.py）
        "-p", "common.pytest_fixture"
    ]

    # 3. 执行用例（调用公共logger）
    logger.info("开始执行接口自动化用例...")
    logger.info(f"执行参数：{pytest_args}")
    result = pytest.main(pytest_args)

    # 4. 生成Allure报告（公共函数路径兼容）
    if result == 0:
        logger.info("用例执行完成，开始生成Allure报告...")
        # 路径加引号，避免空格/特殊字符（公共函数未覆盖的细节）
        os.system(f"allure generate \"{allure_results}\" -o \"{allure_report}\" --clean")
        os.system(f"allure open \"{allure_report}\"")
    else:
        # 修正：pytest返回的是退出码，不是失败数量（公共函数日志逻辑）
        logger.error(f"用例执行完成，pytest退出码：{result}（0=通过，1=有失败，2=中断）")

    return result


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)  # 替换os._exit，确保公共函数的日志/资源正常释放