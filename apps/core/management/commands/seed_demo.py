from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from apps.core.models import Announcement, DashboardNote, ExpertKnowledge
from apps.monitoring.models import FillProcess, Sensor, SensorReading, VideoDevice, AlertEvent, EnvironmentMetric
from apps.lifecycle.models import FillProject, ProjectTask, Milestone, ProjectDocument, RiskRecord, AcceptanceRecord
from apps.equipment.models import Equipment, EquipmentSensorPlan, InspectionRecord, MaintenanceOrder, DiagnosisCase, ARSession
from apps.training.models import TrainingCourse, TrainingRecord
import random

class Command(BaseCommand):
    help = '初始化煤矿智能化充填平台演示数据'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')

        Announcement.objects.all().delete()
        DashboardNote.objects.all().delete()
        ExpertKnowledge.objects.all().delete()
        FillProcess.objects.all().delete()
        FillProject.objects.all().delete()
        Equipment.objects.all().delete()
        TrainingCourse.objects.all().delete()
        EnvironmentMetric.objects.all().delete()

        Announcement.objects.bulk_create([
            Announcement(title='平台上线通知', content='煤矿智能化充填综合操作平台演示版已部署，可用于功能展示与方案汇报。', level='info'),
            Announcement(title='安全预警提醒', content='请持续关注充填站压力、料位、环境参数以及关键设备振动温升变化。', level='warning'),
        ])

        for item in [
            ('在线传感器', '26', '采集振动、温度、压力、流量、料位、气体、湿度等数据'),
            ('在建项目', '3', '覆盖立项、设计、施工、调试、验收阶段'),
            ('设备健康优良率', '86%', '基于巡检与诊断结果自动评估'),
            ('远程诊断案例', '6', '支持后台专家与现场维修人员协作'),
            ('工艺覆盖类型', '3类', '膏体、尾砂、原矸'),
            ('培训课程', '4门', '面向现场运维、调度、管理、专家'),
        ]:
            DashboardNote.objects.create(title=item[0], value=item[1], description=item[2])

        for category, title, content in [
            ('充填工艺', '膏体充填关键监测点', '重点关注浓度、流量、压力、料位、泵站运行状态及回填节拍。'),
            ('充填工艺', '尾砂充填关键监测点', '重点关注尾砂浓度波动、脱水状态、输送压力与料浆稳定性。'),
            ('设备诊断', '振动与温升联合诊断', '针对泵、搅拌机、压滤机等设备，优先结合振动谱与轴承温升识别异常。'),
            ('AR协作', '远程专家协同要点', '现场人员佩戴AR眼镜后，后台专家可进行视频查看、语音指导、空间标注。'),
            ('项目管理', '全生命周期管理要点', '从立项到验收运维，需贯穿进度、质量、安全、成本、文档与风险闭环。'),
        ]:
            ExpertKnowledge.objects.create(category=category, title=title, content=content)

        processes = [
            FillProcess.objects.create(
                name='东翼膏体充填系统',
                process_type='paste',
                mine_name='新汶矿区一号井',
                status='运行中',
                design_capacity=180,
                current_flow=162,
                concentration=78,
                pipeline_pressure=4.6,
                data_quality=97,
                remark='适用于高浓度膏体输送与工作面精准回填。'
            ),
            FillProcess.objects.create(
                name='西区尾砂充填系统',
                process_type='tailings',
                mine_name='新汶矿区二号井',
                status='运行中',
                design_capacity=150,
                current_flow=136,
                concentration=66,
                pipeline_pressure=3.9,
                data_quality=95,
                remark='重点关注尾砂含水率与压力波动。'
            ),
            FillProcess.objects.create(
                name='北翼原矸充填系统',
                process_type='gangue',
                mine_name='鲁西矿区三号井',
                status='维护中',
                design_capacity=220,
                current_flow=98,
                concentration=58,
                pipeline_pressure=5.2,
                data_quality=91,
                remark='用于原矸运输、破碎和远程集控。'
            ),
        ]

        sensor_specs = [
            ('泵站振动传感器', 'vibration', 'mm/s', 1.8, 0, 4.5),
            ('泵站温度传感器', 'temperature', '℃', 58, 10, 75),
            ('主管路压力传感器', 'pressure', 'MPa', 4.2, 1, 5.8),
            ('主输送流量传感器', 'flow', 'm³/h', 132, 50, 210),
            ('工作面料位传感器', 'level', '%', 62, 10, 90),
        ]

        for p_index, process in enumerate(processes, start=1):
            for idx, spec in enumerate(sensor_specs, start=1):
                sensor = Sensor.objects.create(
                    process=process,
                    name=spec[0],
                    sensor_type=spec[1],
                    code=f'SN-{p_index:02d}-{idx:02d}',
                    location=f'{process.mine_name}-{process.name}-监测点{idx}',
                    unit=spec[2],
                    current_value=spec[3] + random.uniform(-1, 1),
                    threshold_low=spec[4],
                    threshold_high=spec[5],
                    is_online=True,
                )
                for _ in range(5):
                    SensorReading.objects.create(
                        sensor=sensor,
                        value=round(sensor.current_value + random.uniform(-1.5, 1.5), 2),
                        quality_score=random.randint(92, 100)
                    )

            VideoDevice.objects.create(
                process=process,
                name=f'{process.name}-工业视频终端',
                location=f'{process.mine_name}-主控室',
                stream_url='rtsp://demo.local/stream',
                status='在线'
            )

        for process in processes:
            AlertEvent.objects.create(
                process=process,
                sensor=process.sensors.first(),
                title=f'{process.name}压力波动预警',
                level='high' if process.process_type != 'tailings' else 'medium',
                description='系统检测到关键参数波动，请结合视频与现场巡检进一步确认。',
                resolved=False
            )

        EnvironmentMetric.objects.bulk_create([
            EnvironmentMetric(mine_name='新汶矿区一号井', gas_concentration=0.16, temperature=25.6, humidity=68, pressure=101.2, risk_level='低'),
            EnvironmentMetric(mine_name='新汶矿区二号井', gas_concentration=0.22, temperature=27.1, humidity=72, pressure=100.8, risk_level='中'),
            EnvironmentMetric(mine_name='鲁西矿区三号井', gas_concentration=0.18, temperature=24.9, humidity=65, pressure=101.0, risk_level='低'),
        ])

        project1 = FillProject.objects.create(
            name='新汶矿区膏体充填数字化建设项目',
            code='PRJ-2026-001',
            owner='张工',
            mine_name='新汶矿区一号井',
            stage='construction',
            budget=6800000,
            progress=62,
            start_date=date.today() - timedelta(days=90),
            end_date=date.today() + timedelta(days=120),
            description='建设覆盖工艺监测、设备健康、调度大屏、验收运维的一体化平台。'
        )
        project2 = FillProject.objects.create(
            name='尾砂充填项目全生命周期管理系统',
            code='PRJ-2026-002',
            owner='李工',
            mine_name='新汶矿区二号井',
            stage='design',
            budget=3200000,
            progress=35,
            start_date=date.today() - timedelta(days=45),
            end_date=date.today() + timedelta(days=150),
            description='重点建设项目立项、计划、风险、验收和运维闭环。'
        )
        project3 = FillProject.objects.create(
            name='原矸充填远程诊断与AR协作项目',
            code='PRJ-2026-003',
            owner='王工',
            mine_name='鲁西矿区三号井',
            stage='commissioning',
            budget=4500000,
            progress=78,
            start_date=date.today() - timedelta(days=120),
            end_date=date.today() + timedelta(days=40),
            description='结合工业AR眼镜，建设专家远程会诊与设备诊断能力。'
        )

        for prj in [project1, project2, project3]:
            ProjectTask.objects.bulk_create([
                ProjectTask(project=prj, title='需求调研与方案设计', owner='项目经理', stage='立项/设计', status='done', progress=100, start_date=prj.start_date, due_date=prj.start_date + timedelta(days=15), remark='完成现场调研和业务梳理'),
                ProjectTask(project=prj, title='系统开发与接口联调', owner='开发负责人', stage='开发', status='doing', progress=70, start_date=prj.start_date + timedelta(days=16), due_date=prj.start_date + timedelta(days=70), remark='完成核心功能，正在联调'),
                ProjectTask(project=prj, title='上线试运行与优化', owner='运维负责人', stage='调试/验收', status='todo', progress=15, start_date=prj.start_date + timedelta(days=71), due_date=prj.end_date, remark='计划结合试运行反馈优化'),
            ])
            Milestone.objects.bulk_create([
                Milestone(project=prj, title='立项批复', milestone_date=prj.start_date + timedelta(days=5), completed=True, description='已完成'),
                Milestone(project=prj, title='中期评审', milestone_date=prj.start_date + timedelta(days=60), completed=prj.progress >= 50, description='按计划推进'),
                Milestone(project=prj, title='最终验收', milestone_date=prj.end_date, completed=False, description='待完成'),
            ])
            ProjectDocument.objects.bulk_create([
                ProjectDocument(project=prj, title='项目立项申请书', category='立项文件', version='V1.0', file_note='用于项目立项审批'),
                ProjectDocument(project=prj, title='实施方案与技术路线', category='设计文件', version='V1.2', file_note='包括部署架构、接口与工艺逻辑'),
                ProjectDocument(project=prj, title='验收计划与测试清单', category='验收文件', version='V0.9', file_note='用于上线前测试'),
            ])
            RiskRecord.objects.create(project=prj, title='现场设备接入进度风险', level='中', status='监控中', strategy='加强现场协调，分阶段接入并同步调试。')

        AcceptanceRecord.objects.create(project=project3, acceptance_stage='阶段性联调验收', score=88, result='通过', summary='远程诊断、工单联动、AR协作功能满足阶段演示要求。', accepted_at=date.today() - timedelta(days=7))

        eq1 = Equipment.objects.create(name='高压输送泵', code='EQ-001', category='泵类设备', mine_name='新汶矿区一号井', location='泵房A区', health_status='good', health_score=87, runtime_hours=4200, next_maintenance_date=date.today() + timedelta(days=25))
        eq2 = Equipment.objects.create(name='膏体搅拌机', code='EQ-002', category='搅拌设备', mine_name='新汶矿区一号井', location='制浆车间', health_status='warning', health_score=73, runtime_hours=5100, next_maintenance_date=date.today() + timedelta(days=12))
        eq3 = Equipment.objects.create(name='压滤系统', code='EQ-003', category='过滤设备', mine_name='新汶矿区二号井', location='尾砂车间', health_status='excellent', health_score=92, runtime_hours=3000, next_maintenance_date=date.today() + timedelta(days=40))
        eq4 = Equipment.objects.create(name='原矸破碎机', code='EQ-004', category='破碎设备', mine_name='鲁西矿区三号井', location='破碎站', health_status='warning', health_score=70, runtime_hours=6100, next_maintenance_date=date.today() + timedelta(days=10))

        for eq in [eq1, eq2, eq3, eq4]:
            EquipmentSensorPlan.objects.bulk_create([
                EquipmentSensorPlan(equipment=eq, sensor_type='振动传感器', deploy_position='轴承座', purpose='监测机械振动与不平衡状态', status='已部署'),
                EquipmentSensorPlan(equipment=eq, sensor_type='温度传感器', deploy_position='电机与轴承区域', purpose='监测热异常与润滑状态', status='已部署'),
            ])
            InspectionRecord.objects.create(
                equipment=eq,
                inspector='赵工',
                result='正常' if eq.health_score >= 80 else '需重点关注',
                vibration_value=round(random.uniform(1.2, 4.8), 2),
                temperature_value=round(random.uniform(42, 76), 2),
                note='建议结合周趋势进行分析。'
            )
            MaintenanceOrder.objects.create(
                equipment=eq,
                title=f'{eq.name}例行维护工单',
                priority='高' if eq.health_status in ['warning', 'danger'] else '中',
                status='processing' if eq.health_status in ['warning', 'danger'] else 'open',
                assignee='维修班组A',
                summary='检查关键部件、润滑状态、紧固件、温升和振动情况。'
            )
            DiagnosisCase.objects.create(
                equipment=eq,
                title=f'{eq.name}远程诊断案例',
                symptom='设备运行中出现异常振动或温升波动。',
                diagnosis='结合振动、温度与运行时长，初步判断存在轴承磨损或联轴器偏移风险。',
                recommendation='安排停机窗口进行对中检查、润滑补充及轴承状态复核。',
                expert_name='远程专家组'
            )

        ARSession.objects.bulk_create([
            ARSession(equipment=eq2, session_code='AR-2026-001', glasses_model='工业AR眼镜-示例型号', field_engineer='现场维修员刘某', remote_expert='专家周工', status='指导中', interaction_note='后台专家已标注轴承检查位置，并指导拆检步骤。'),
            ARSession(equipment=eq4, session_code='AR-2026-002', glasses_model='工业AR眼镜-示例型号', field_engineer='现场维修员孙某', remote_expert='专家陈工', status='已完成', interaction_note='完成破碎机联轴器偏差复核与复位指导。'),
        ])

        course1 = TrainingCourse.objects.create(title='充填工艺全流程监测实操', category='工艺培训', teacher='韩老师', duration_hours=4, mode='线下实操', description='围绕膏体、尾砂、原矸三种工艺进行监测点与异常分析培训。')
        course2 = TrainingCourse.objects.create(title='设备健康诊断与AR远程协作', category='设备培训', teacher='刘老师', duration_hours=3, mode='线上+实训', description='讲解振动温升分析、工单闭环、AR协作。')
        course3 = TrainingCourse.objects.create(title='充填项目全生命周期管理', category='项目管理', teacher='王老师', duration_hours=2, mode='线上', description='覆盖立项、设计、采购、施工、验收、运维。')
        course4 = TrainingCourse.objects.create(title='煤矿安全环保参数监测', category='安全培训', teacher='张老师', duration_hours=2, mode='线上', description='重点讲解气体、温湿度、压力等风险识别。')

        for course, names in [
            (course1, ['李明', '王涛', '赵凯']),
            (course2, ['孙浩', '周林']),
            (course3, ['高峰', '徐磊']),
            (course4, ['陈宁', '于洋']),
        ]:
            for i, name in enumerate(names):
                TrainingRecord.objects.create(
                    course=course,
                    trainee=name,
                    department='充填事业部',
                    score=85 + i,
                    passed=True,
                    completed_at=date.today() - timedelta(days=random.randint(1, 20))
                )

        self.stdout.write(self.style.SUCCESS('演示数据初始化完成。管理员：admin / admin123456'))
