# -*- coding: utf-8 -*-
"""
上海方松项目单体楼栋开发计划编制脚本
"""

import sys
import os
import datetime
import traceback

# 添加MSProject_rev2.py所在路径
skill_path = r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\skills\project-planning'
sys.path.insert(0, skill_path)

from MSProject_rev2 import MSProject

def main():
    print("="*60)
    print("上海方松项目单体楼栋开发计划编制")
    print("="*60)

    # 文件路径
    template_path = os.path.join(skill_path, 'template.mpp')
    output_dir = r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\Test_result'
    output_file = '上海方松项目_单体楼栋计划_18层_地2层.mpp'
    output_path = os.path.join(output_dir, output_file)

    print(f"\n模板文件: {template_path}")
    print(f"输出文件: {output_path}")

    # 项目技术参数
    print(f"\n项目技术参数:")
    print(f"  - 楼栋类型: 18层高层")
    print(f"  - 地下室: 地下2层")
    print(f"  - 基础形式: 预制管桩+筏板基础(45天)")
    print(f"  - 地质条件: 正常")

    try:
        # 创建MSProject实例
        print("\n[1/5] 初始化MS Project...")
        msp = MSProject()

        # 加载模板
        print("[2/5] 加载模板文件...")
        if not msp.load(template_path):
            print("[ERROR] 无法加载模板文件!")
            return False

        print(f"       模板加载成功，共 {msp.Project.Tasks.Count} 个任务")

        # 设置项目开始日期
        print("[3/5] 设置项目开始日期...")
        start_date = datetime.datetime(2024, 6, 1)
        try:
            if msp.Project.Tasks.Count > 0:
                first_task = msp.Project.Tasks.Item(1)
                first_task.Start = start_date
                print(f"       项目开始日期: 2024-06-01")
        except Exception as e:
            print(f"       [WARN] 设置开始日期失败: {e}")

        # 调整任务周期
        print("[4/5] 根据技术参数调整任务周期...")

        adjusted_count = 0

        # 遍历所有任务，根据关键词调整周期
        for i in range(1, msp.Project.Tasks.Count + 1):
            try:
                task = msp.Project.Tasks.Item(i)
                task_name = task.Name

                # 基础工程: 预制管桩+筏板基础 45天
                if ('管桩' in task_name or '桩基' in task_name) and '基础' in task_name:
                    task.Duration = 45 * 8 * 60  # 45天
                    print(f"       - {task_name[:40]}: 45天 (预制管桩)")
                    adjusted_count += 1

                elif '筏板' in task_name and '基础' in task_name:
                    task.Duration = 15 * 8 * 60  # 15天
                    print(f"       - {task_name[:40]}: 15天 (筏板基础)")
                    adjusted_count += 1

                # 地下室: 地下2层
                elif '地下室' in task_name or '底板' in task_name:
                    if '底板' in task_name:
                        task.Duration = 20 * 8 * 60  # 20天
                        print(f"       - {task_name[:40]}: 20天 (地下2层底板)")
                        adjusted_count += 1
                    elif '2层' in task_name or '二层' in task_name:
                        task.Duration = 80 * 8 * 60  # 80天
                        print(f"       - {task_name[:40]}: 80天 (地下2层结构)")
                        adjusted_count += 1

                # 土方开挖: 地下2层需更深开挖
                elif '土方' in task_name and '开挖' in task_name:
                    task.Duration = 35 * 8 * 60  # 35天
                    print(f"       - {task_name[:40]}: 35天 (地下2层)")
                    adjusted_count += 1

                # 支护工程: 地下2层
                elif '支护' in task_name:
                    task.Duration = 50 * 8 * 60  # 50天
                    print(f"       - {task_name[:40]}: 50天 (地下2层)")
                    adjusted_count += 1

                # 降水工程
                elif '降水' in task_name:
                    task.Duration = 60 * 8 * 60  # 60天
                    print(f"       - {task_name[:40]}: 60天")
                    adjusted_count += 1

                # 主体结构: 18层
                elif '主体结构' in task_name:
                    if '18' in task_name or '十八' in task_name:
                        task.Duration = 108 * 8 * 60  # 108天 (18层x6天)
                        print(f"       - {task_name[:40]}: 108天 (18层)")
                        adjusted_count += 1

                elif '封顶' in task_name:
                    task.Duration = 2 * 8 * 60  # 2天
                    print(f"       - {task_name[:40]}: 2天")
                    adjusted_count += 1

            except Exception as e:
                continue

        print(f"\n       共调整 {adjusted_count} 个任务")

        # 保存文件
        print("[5/5] 保存计划文件...")
        if msp.save(output_path):
            print(f"       文件已保存: {output_path}")
        else:
            print("[ERROR] 保存文件失败")
            msp.saveAndClose()
            return False

        # 关闭MS Project
        print("\n正在关闭MS Project...")
        msp.saveAndClose()

        print("\n" + "="*60)
        print("计划编制完成!")
        print("="*60)
        print(f"\n生成的文件: {output_path}")
        print(f"\n技术参数汇总:")
        print(f"  - 18层主体结构: 108天 (每层6天)")
        print(f"  - 地下2层结构: 80天")
        print(f"  - 预制管桩基础: 45天")
        print(f"  - 土方开挖(地2层): 35天")
        print(f"  - 支护工程(地2层): 50天")

        return True

    except Exception as e:
        print(f"\n[ERROR] 执行过程中发生错误:")
        print(str(e))
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
