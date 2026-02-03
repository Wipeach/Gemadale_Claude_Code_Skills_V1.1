"""
上海方松项目单体楼栋开发计划编制脚本

项目信息:
- 项目名称: 上海方松项目
- 楼栋类型: 18层高层
- 地下室: 地下2层
- 基础形式: 预制管桩 + 筏板基础
- 地质条件: 无特殊情况
"""

import sys
import os
import datetime
import traceback

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加MSProject_rev2.py所在路径到系统路径
skill_path = r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\skills\project-planning'
sys.path.insert(0, skill_path)

from MSProject_rev2 import MSProject

# ============================================================
# 项目技术变量配置
# ============================================================

PROJECT_CONFIG = {
    # 项目基本信息
    'project_name': '上海方松项目',
    'building_type': '18层高层',
    'basement_floors': 2,  # 地下2层
    'foundation_type': '预制管桩+筏板基础',  # 预应力管桩 + 45天
    'geology': '正常',  # 无特殊情况

    # 标准周期配置（来自scheduling_vars.md）
    'standard_durations': {
        # 基础工程标准周期
        'foundation_prefab_pile': 45,  # 预应力管桩45天
        'foundation_raft': 15,  # 天然筏板地基15天

        # 地下室施工（按层数）
        # 地下2层的标准周期约为地下1层的1.8-2倍
        'basement_1_floor': 60,  # 地下1层参考周期
        'basement_2_floors': 100,  # 地下2层参考周期

        # 主体结构（18层高层）
        # 每层约5-7天，18层约90-126天
        'structure_per_floor': 6,  # 每层6天
        'structure_18_floors': 108,  # 18层主体结构

        # 其他关键任务周期
        'earthwork': 30,  # 土方开挖
        'supporting': 40,  # 支护工程
        'waterproofing': 20,  # 防水工程
    }
}

# ============================================================
# 任务调整规则
# ============================================================

TASK_ADJUSTMENT_RULES = {
    # 基础工程任务关键词及调整
    'foundation_keywords': ['基础', '管桩', '桩基', '筏板', '承台'],
    'foundation_duration': 45,  # 预制管桩+筏板基础

    # 地下室任务关键词及调整
    'basement_keywords': ['地下室', '地下结构', '底板', '地库'],
    'basement_floors': 2,  # 地下2层

    # 主体结构任务关键词
    'structure_keywords': ['主体结构', '标准层', '结构施工', '封顶'],
    'structure_floors': 18,

    # 土方和支护
    'earthwork_keywords': ['土方', '开挖', '支护', '降水'],
}


def find_tasks_by_keywords(msp, keywords):
    """
    根据关键词查找任务

    Args:
        msp: MSProject实例
        keywords: 关键词列表

    Returns:
        匹配的任务ID列表
    """
    matching_tasks = []

    try:
        for i in range(1, msp.Project.Tasks.Count + 1):
            try:
                task = msp.Project.Tasks.Item(i)
                task_name = task.Name

                # 检查任务名称是否包含任一关键词
                for keyword in keywords:
                    if keyword in task_name:
                        matching_tasks.append({
                            'id': task.ID,
                            'name': task_name,
                            'duration': task.Duration,
                            'start': task.Start,
                            'finish': task.Finish
                        })
                        break
            except:
                continue

        return matching_tasks

    except Exception as e:
        print(f"查找任务时出错: {e}")
        return []


def adjust_foundation_tasks(msp):
    """调整基础工程任务周期"""
    print("\n=== 调整基础工程任务 ===")

    keywords = TASK_ADJUSTMENT_RULES['foundation_keywords']
    tasks = find_tasks_by_keywords(msp, keywords)

    adjusted_count = 0
    for task_info in tasks:
        try:
            task = msp.Project.Tasks.Item(task_info['id'])

            # 如果任务名称包含"管桩"或"桩基"，设置为45天
            if '管桩' in task_info['name'] or '桩基' in task_info['name']:
                # 设置为45天（45天 * 8小时 * 60分钟 = 21600分钟）
                duration = 45 * 8 * 60
                task.Duration = duration
                print(f"  [OK] 调整任务: {task_info['name']} -> 45天")
                adjusted_count += 1

            # 如果任务名称包含"筏板"
            elif '筏板' in task_info['name']:
                # 筏板基础施工约15天
                duration = 15 * 8 * 60
                task.Duration = duration
                print(f"  [OK] 调整任务: {task_info['name']} -> 15天")
                adjusted_count += 1

        except Exception as e:
            print(f"  [FAIL] 调整任务失败 {task_info['name']}: {e}")

    print(f"基础工程任务调整完成，共调整 {adjusted_count} 个任务")
    return adjusted_count


def adjust_basement_tasks(msp):
    """调整地下室施工任务周期（地下2层）"""
    print("\n=== 调整地下室施工任务（地下2层）===")

    keywords = TASK_ADJUSTMENT_RULES['basement_keywords']
    tasks = find_tasks_by_keywords(msp, keywords)

    adjusted_count = 0
    basement_floors = TASK_ADJUSTMENT_RULES['basement_floors']

    for task_info in tasks:
        try:
            task = msp.Project.Tasks.Item(task_info['id'])

            # 地下2层的总施工周期约为100天
            # 根据任务名称判断具体调整
            if '底板' in task_info['name']:
                # 地下室底板施工：约20天
                duration = 20 * 8 * 60
                task.Duration = duration
                print(f"  ✓ 调整任务: {task_info['name']} -> 20天")
                adjusted_count += 1

            elif '地下结构' in task_info['name'] or '地下室' in task_info['name']:
                # 地下室结构总周期（2层）：约80天
                if '2层' in task_info['name'] or '二层' in task_info['name']:
                    duration = 80 * 8 * 60
                    task.Duration = duration
                    print(f"  ✓ 调整任务: {task_info['name']} -> 80天（地下2层）")
                    adjusted_count += 1

        except Exception as e:
            print(f"  ✗ 调整任务失败 {task_info['name']}: {e}")

    print(f"地下室任务调整完成，共调整 {adjusted_count} 个任务")
    return adjusted_count


def adjust_structure_tasks(msp):
    """调整主体结构任务周期（18层）"""
    print("\n=== 调整主体结构任务（18层）===")

    keywords = TASK_ADJUSTMENT_RULES['structure_keywords']
    tasks = find_tasks_by_keywords(msp, keywords)

    adjusted_count = 0
    structure_floors = TASK_ADJUSTMENT_RULES['structure_floors']

    for task_info in tasks:
        try:
            task = msp.Project.Tasks.Item(task_info['id'])

            # 18层主体结构总周期：约108天（每层6天）
            if '主体结构' in task_info['name']:
                if '18' in task_info['name'] or '十八' in task_info['name']:
                    duration = 108 * 8 * 60
                    task.Duration = duration
                    print(f"  ✓ 调整任务: {task_info['name']} -> 108天（18层×6天）")
                    adjusted_count += 1
                elif '封顶' in task_info['name']:
                    # 封顶任务与主体结构完成同步
                    duration = 2 * 8 * 60  # 封顶仪式/验收约2天
                    task.Duration = duration
                    print(f"  ✓ 调整任务: {task_info['name']} -> 2天")
                    adjusted_count += 1

        except Exception as e:
            print(f"  ✗ 调整任务失败 {task_info['name']}: {e}")

    print(f"主体结构任务调整完成，共调整 {adjusted_count} 个任务")
    return adjusted_count


def adjust_earthwork_tasks(msp):
    """调整土方和支护任务"""
    print("\n=== 调整土方和支护任务 ===")

    keywords = TASK_ADJUSTMENT_RULES['earthwork_keywords']
    tasks = find_tasks_by_keywords(msp, keywords)

    adjusted_count = 0

    for task_info in tasks:
        try:
            task = msp.Project.Tasks.Item(task_info['id'])

            # 根据地下2层调整土方开挖深度和周期
            if '土方' in task_info['name'] and '开挖' in task_info['name']:
                # 地下2层的土方开挖：约35天
                duration = 35 * 8 * 60
                task.Duration = duration
                print(f"  ✓ 调整任务: {task_info['name']} -> 35天（地下2层）")
                adjusted_count += 1

            elif '支护' in task_info['name']:
                # 地下2层的支护工程：约50天
                duration = 50 * 8 * 60
                task.Duration = duration
                print(f"  ✓ 调整任务: {task_info['name']} -> 50天（地下2层）")
                adjusted_count += 1

            elif '降水' in task_info['name']:
                # 降水工程：约60天（贯穿地下室施工全过程）
                duration = 60 * 8 * 60
                task.Duration = duration
                print(f"  ✓ 调整任务: {task_info['name']} -> 60天")
                adjusted_count += 1

        except Exception as e:
            print(f"  ✗ 调整任务失败 {task_info['name']}: {e}")

    print(f"土方和支护任务调整完成，共调整 {adjusted_count} 个任务")
    return adjusted_count


def set_project_start_date(msp, start_date='2024/06/01'):
    """设置项目开始日期"""
    print(f"\n=== 设置项目开始日期: {start_date} ===")

    try:
        # 查找第一个任务（通常是项目开始任务）
        if msp.Project.Tasks.Count > 0:
            first_task = msp.Project.Tasks.Item(1)
            first_task.Start = datetime.datetime.strptime(start_date, '%Y/%m/%d')
            print(f"  ✓ 项目开始日期已设置为: {start_date}")
            return True
    except Exception as e:
        print(f"  ✗ 设置项目开始日期失败: {e}")

    return False


def main():
    """主函数：执行项目计划编制"""

    print("=" * 60)
    print("上海方松项目单体楼栋开发计划编制")
    print("=" * 60)
    print(f"\n项目配置:")
    print(f"  - 项目名称: {PROJECT_CONFIG['project_name']}")
    print(f"  - 楼栋类型: {PROJECT_CONFIG['building_type']}")
    print(f"  - 地下室: {PROJECT_CONFIG['basement_floors']}层")
    print(f"  - 基础形式: {PROJECT_CONFIG['foundation_type']}")
    print(f"  - 地质条件: {PROJECT_CONFIG['geology']}")

    # 文件路径
    template_path = os.path.join(skill_path, 'template.mpp')
    output_path = r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\Test_result\上海方松项目_单体楼栋计划_18层_地2层.mpp'

    print(f"\n模板文件: {template_path}")
    print(f"输出文件: {output_path}")

    # 创建MSProject实例
    print("\n正在初始化MS Project...")
    msp = MSProject()

    # 加载模板
    print("正在加载模板文件...")
    if not msp.load(template_path):
        print("错误: 无法加载模板文件!")
        return False

    print("✓ 模板加载成功")

    # 打印项目基本信息
    print(f"\n模板信息:")
    print(f"  - 任务总数: {msp.Project.Tasks.Count}")

    # 设置项目开始日期
    set_project_start_date(msp, '2024/06/01')

    # 根据技术变量调整任务
    total_adjusted = 0

    # 1. 调整基础工程（预制管桩+筏板基础）
    total_adjusted += adjust_foundation_tasks(msp)

    # 2. 调整地下室施工（地下2层）
    total_adjusted += adjust_basement_tasks(msp)

    # 3. 调整土方和支护（地下2层）
    total_adjusted += adjust_earthwork_tasks(msp)

    # 4. 调整主体结构（18层）
    total_adjusted += adjust_structure_tasks(msp)

    print(f"\n=== 任务调整汇总 ===")
    print(f"总共调整了 {total_adjusted} 个任务")

    # 保存文件
    print(f"\n正在保存计划文件...")
    if msp.save(output_path):
        print(f"✓ 计划文件已保存至: {output_path}")
    else:
        print("✗ 保存文件失败")
        msp.saveAndClose()
        return False

    # 关闭MS Project
    print("\n正在关闭MS Project...")
    msp.saveAndClose()

    print("\n" + "=" * 60)
    print("计划编制完成！")
    print("=" * 60)
    print(f"\n生成的文件: {output_path}")
    print(f"\n项目技术参数:")
    print(f"  - 18层高层主体结构周期: 约108天（每层6天）")
    print(f"  - 地下2层施工周期: 约100天")
    print(f"  - 预制管桩基础周期: 45天")
    print(f"  - 土方开挖周期（地2层）: 约35天")
    print(f"  - 支护工程周期（地2层）: 约50天")

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n执行过程中发生错误:")
        print(str(e))
        traceback.print_exc()
        sys.exit(1)
