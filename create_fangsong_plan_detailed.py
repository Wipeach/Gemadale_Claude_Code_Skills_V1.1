# -*- coding: utf-8 -*-
"""
上海方松项目单体楼栋开发计划编制脚本（详细版）

基于技术变量标准周期进行任务调整
参考: scheduling_vars.md
"""

import sys
import os
import datetime
import traceback

# 添加MSProject_rev2.py所在路径
skill_path = r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\skills\project-planning'
sys.path.insert(0, skill_path)

from MSProject_rev2 import MSProject

# ============================================================
# 技术变量标准周期配置（来自scheduling_vars.md）
# ============================================================

STANDARD_DURATIONS = {
    # 基础工程（scheduling_vars.md 二、技术变量 -> 地下 -> 7）
    'foundation_natural_raft': 15,      # 天然筏板地基 15天
    'foundation_natural_independent': 35,  # 天然独立基础 35天
    'foundation_prefab_pile': 45,       # 预应力管桩 45天
    'foundation_roulette_cfg': 60,      # 旋挖桩和CFG桩 60天
    'foundation_punch_hole': 75,        # 冲孔桩和钻孔灌注桩 75天

    # 地下室施工（根据层数调整）
    'basement_1_floor': 60,             # 地下1层参考周期
    'basement_2_floors': 100,           # 地下2层参考周期
    'basement_3_floors': 140,           # 地下3层参考周期

    # 主体结构（每层约5-7天）
    'structure_per_floor': 6,           # 每层6天（标准）
    'structure_per_floor_fast': 5,      # 每层5天（快节奏）
    'structure_per_floor_slow': 7,      # 每层7天（慢节奏）

    # 土方及支护（scheduling_vars.md 二、技术变量 -> 地下 -> 5）
    'earthwork_basement_1': 25,         # 地下1层土方
    'earthwork_basement_2': 35,         # 地下2层土方
    'earthwork_basement_3': 50,         # 地下3层土方

    # 支护工程
    'supporting_simple': 30,            # 简单支护（放坡、喷锚）
    'supporting_medium': 50,            # 中等支护（支护桩锚索）
    'supporting_complex': 70,           # 复杂支护（内环梁、地连墙）

    # 降水工程
    'dewatering_short': 45,             # 短期降水
    'dewatering_long': 60,              # 长期降水
}

# ============================================================
# 项目配置
# ============================================================

PROJECT_CONFIG = {
    'name': '上海方松项目',
    'building': {
        'type': '高层',
        'floors': 18,
        'basement_floors': 2,
    },
    'foundation': {
        'type': '预制管桩+筏板基础',
        'duration': STANDARD_DURATIONS['foundation_prefab_pile'],  # 45天
    },
    'geology': {
        'condition': '正常',
        'groundwater': '正常',
        'surrounding': '无特殊',
    },
    'earthwork': {
        'method': '常规开挖',
        'duration': STANDARD_DURATIONS['earthwork_basement_2'],  # 35天（地下2层）
    },
    'supporting': {
        'type': '常规支护',
        'duration': STANDARD_DURATIONS['supporting_medium'],  # 50天
    },
    'start_date': '2024/06/01',
}

# ============================================================
# 任务调整规则
# ============================================================

class TaskAdjuster:
    """任务调整器"""

    def __init__(self, msp, config):
        self.msp = msp
        self.config = config
        self.adjusted_tasks = []

    def adjust_all(self):
        """执行所有调整"""
        print("\n[任务调整]")

        # 1. 基础工程
        self.adjust_foundation()

        # 2. 土方工程
        self.adjust_earthwork()

        # 3. 支护工程
        self.adjust_supporting()

        # 4. 降水工程
        self.adjust_dewatering()

        # 5. 地下室结构
        self.adjust_basement()

        # 6. 主体结构
        self.adjust_structure()

        # 打印汇总
        self.print_summary()

    def adjust_foundation(self):
        """调整基础工程任务"""
        print("  [1/6] 基础工程")

        foundation_duration = self.config['foundation']['duration']

        for i in range(1, self.msp.Project.Tasks.Count + 1):
            try:
                task = self.msp.Project.Tasks.Item(i)
                name = task.Name

                # 预制管桩
                if '管桩' in name or '桩基' in name:
                    if '基础' in name or '工程' in name:
                        task.Duration = foundation_duration * 8 * 60
                        self.adjusted_tasks.append({
                            'name': name,
                            'duration': foundation_duration,
                            'reason': '预制管桩基础'
                        })
                        print(f"    - {name[:40]}: {foundation_duration}天")

                # 筏板基础
                elif '筏板' in name:
                    task.Duration = STANDARD_DURATIONS['foundation_natural_raft'] * 8 * 60
                    self.adjusted_tasks.append({
                        'name': name,
                        'duration': STANDARD_DURATIONS['foundation_natural_raft'],
                        'reason': '筏板基础'
                    })
                    print(f"    - {name[:40]}: {STANDARD_DURATIONS['foundation_natural_raft']}天")

            except:
                continue

    def adjust_earthwork(self):
        """调整土方工程"""
        print("  [2/6] 土方工程")

        duration = self.config['earthwork']['duration']

        for i in range(1, self.msp.Project.Tasks.Count + 1):
            try:
                task = self.msp.Project.Tasks.Item(i)
                name = task.Name

                if '土方' in name and '开挖' in name:
                    task.Duration = duration * 8 * 60
                    self.adjusted_tasks.append({
                        'name': name,
                        'duration': duration,
                        'reason': f'地下{self.config["building"]["basement_floors"]}层土方'
                    })
                    print(f"    - {name[:40]}: {duration}天")

            except:
                continue

    def adjust_supporting(self):
        """调整支护工程"""
        print("  [3/6] 支护工程")

        duration = self.config['supporting']['duration']

        for i in range(1, self.msp.Project.Tasks.Count + 1):
            try:
                task = self.msp.Project.Tasks.Item(i)
                name = task.Name

                if '支护' in name:
                    task.Duration = duration * 8 * 60
                    self.adjusted_tasks.append({
                        'name': name,
                        'duration': duration,
                        'reason': f'地下{self.config["building"]["basement_floors"]}层支护'
                    })
                    print(f"    - {name[:40]}: {duration}天")

            except:
                continue

    def adjust_dewatering(self):
        """调整降水工程"""
        print("  [4/6] 降水工程")

        duration = STANDARD_DURATIONS['dewatering_long']

        for i in range(1, self.msp.Project.Tasks.Count + 1):
            try:
                task = self.msp.Project.Tasks.Item(i)
                name = task.Name

                if '降水' in name:
                    task.Duration = duration * 8 * 60
                    self.adjusted_tasks.append({
                        'name': name,
                        'duration': duration,
                        'reason': '长期降水（贯穿地下室施工）'
                    })
                    print(f"    - {name[:40]}: {duration}天")

            except:
                continue

    def adjust_basement(self):
        """调整地下室结构"""
        print("  [5/6] 地下室结构")

        basement_floors = self.config['building']['basement_floors']

        # 地下2层结构总周期
        if basement_floors == 2:
            total_duration = STANDARD_DURATIONS['basement_2_floors']
            slab_duration = 20  # 底板
            structure_duration = 80  # 结构

        for i in range(1, self.msp.Project.Tasks.Count + 1):
            try:
                task = self.msp.Project.Tasks.Item(i)
                name = task.Name

                # 底板
                if '底板' in name and ('地下' in name or '地下室' in name):
                    task.Duration = slab_duration * 8 * 60
                    self.adjusted_tasks.append({
                        'name': name,
                        'duration': slab_duration,
                        'reason': f'地下{basement_floors}层底板'
                    })
                    print(f"    - {name[:40]}: {slab_duration}天")

                # 地下室结构
                elif '地下' in name and ('结构' in name or '施工' in name):
                    if str(basement_floors) in name or ('二层' in name or '2层' in name):
                        task.Duration = structure_duration * 8 * 60
                        self.adjusted_tasks.append({
                            'name': name,
                            'duration': structure_duration,
                            'reason': f'地下{basement_floors}层结构'
                        })
                        print(f"    - {name[:40]}: {structure_duration}天")

            except:
                continue

    def adjust_structure(self):
        """调整主体结构"""
        print("  [6/6] 主体结构")

        floors = self.config['building']['floors']
        per_floor = STANDARD_DURATIONS['structure_per_floor']
        total_duration = floors * per_floor

        for i in range(1, self.msp.Project.Tasks.Count + 1):
            try:
                task = self.msp.Project.Tasks.Item(i)
                name = task.Name

                # 主体结构
                if '主体结构' in name:
                    if str(floors) in name:
                        task.Duration = total_duration * 8 * 60
                        self.adjusted_tasks.append({
                            'name': name,
                            'duration': total_duration,
                            'reason': f'{floors}层主体结构（每层{per_floor}天）'
                        })
                        print(f"    - {name[:40]}: {total_duration}天 ({floors}层x{per_floor}天)")

                # 封顶
                elif '封顶' in name:
                    task.Duration = 2 * 8 * 60
                    self.adjusted_tasks.append({
                        'name': name,
                        'duration': 2,
                        'reason': '封顶仪式/验收'
                    })
                    print(f"    - {name[:40]}: 2天")

            except:
                continue

    def print_summary(self):
        """打印调整汇总"""
        print(f"\n  调整汇总: 共调整 {len(self.adjusted_tasks)} 个任务")


# ============================================================
# 主程序
# ============================================================

def main():
    """主函数"""
    print("="*70)
    print(" "*15 + "上海方松项目单体楼栋开发计划编制")
    print("="*70)

    # 文件路径
    template_path = os.path.join(skill_path, 'template.mpp')
    output_dir = r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\Test_result'
    output_file = '上海方松项目_单体楼栋计划_18层_地2层.mpp'
    output_path = os.path.join(output_dir, output_file)

    # 打印项目配置
    print("\n[项目信息]")
    print(f"  项目名称: {PROJECT_CONFIG['name']}")
    print(f"  楼栋类型: {PROJECT_CONFIG['building']['type']}")
    print(f"  楼层层数: {PROJECT_CONFIG['building']['floors']}层")
    print(f"  地下室: {PROJECT_CONFIG['building']['basement_floors']}层")
    print(f"  基础形式: {PROJECT_CONFIG['foundation']['type']}")
    print(f"  地质条件: {PROJECT_CONFIG['geology']['condition']}")
    print(f"  开工日期: {PROJECT_CONFIG['start_date']}")

    print(f"\n[文件路径]")
    print(f"  模板文件: {template_path}")
    print(f"  输出文件: {output_path}")

    try:
        # 创建MSProject实例
        print("\n[执行步骤]")
        print("  [1/5] 初始化MS Project...")
        msp = MSProject()

        # 加载模板
        print("  [2/5] 加载模板文件...")
        if not msp.load(template_path):
            print("  [ERROR] 无法加载模板文件!")
            return False

        print(f"        成功加载，共 {msp.Project.Tasks.Count} 个任务")

        # 设置项目开始日期
        print("  [3/5] 设置项目开始日期...")
        try:
            start_date = datetime.datetime.strptime(PROJECT_CONFIG['start_date'], '%Y/%m/%d')
            if msp.Project.Tasks.Count > 0:
                first_task = msp.Project.Tasks.Item(1)
                first_task.Start = start_date
                print(f"        开始日期: {PROJECT_CONFIG['start_date']}")
        except Exception as e:
            print(f"        [WARN] 设置开始日期失败: {e}")

        # 调整任务
        print("  [4/5] 根据技术参数调整任务周期...")
        adjuster = TaskAdjuster(msp, PROJECT_CONFIG)
        adjuster.adjust_all()

        # 保存文件
        print("  [5/5] 保存计划文件...")
        if msp.save(output_path):
            print(f"        文件已保存")
        else:
            print("  [ERROR] 保存文件失败")
            msp.saveAndClose()
            return False

        # 关闭
        print("\n[关闭] 正在关闭MS Project...")
        msp.saveAndClose()

        # 打印结果
        print("\n" + "="*70)
        print(" "*25 + "计划编制完成!")
        print("="*70)

        print(f"\n[生成文件]")
        print(f"  {output_path}")

        print(f"\n[技术参数汇总]")
        print(f"  楼栋类型: {PROJECT_CONFIG['building']['type']} {PROJECT_CONFIG['building']['floors']}层")
        print(f"  地下室: {PROJECT_CONFIG['building']['basement_floors']}层")
        print(f"  基础工程: {PROJECT_CONFIG['foundation']['duration']}天 ({PROJECT_CONFIG['foundation']['type']})")
        print(f"  主体结构: {PROJECT_CONFIG['building']['floors']} x {STANDARD_DURATIONS['structure_per_floor']} = {PROJECT_CONFIG['building']['floors'] * STANDARD_DURATIONS['structure_per_floor']}天")
        print(f"  土方开挖: {PROJECT_CONFIG['earthwork']['duration']}天 (地下{PROJECT_CONFIG['building']['basement_floors']}层)")
        print(f"  支护工程: {PROJECT_CONFIG['supporting']['duration']}天")

        print("\n[标准周期参考]")
        print(f"  预制管桩基础: {STANDARD_DURATIONS['foundation_prefab_pile']}天")
        print(f"  地下2层结构: {STANDARD_DURATIONS['basement_2_floors']}天")
        print(f"  每层主体结构: {STANDARD_DURATIONS['structure_per_floor']}天")

        return True

    except Exception as e:
        print(f"\n[ERROR] 执行失败: {e}")
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
