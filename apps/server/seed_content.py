import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.models.database import SessionLocal
from app.models.entities import Space, Topic, Knowledge, KnowledgeVersion, Tag, KnowledgeTag, User
from datetime import datetime, timezone

db = SessionLocal()
try:
    admin = db.query(User).filter(User.role.in_(['owner', 'admin'])).first() or db.query(User).first()
    owner_id = admin.id if admin else 1

    subway = db.query(Space).filter(Space.name == '地铁', Space.is_deleted == False).first()
    train = db.query(Space).filter(Space.name == '火车', Space.is_deleted == False).first()

    subway_topics = {t.name: t.id for t in db.query(Topic).filter(Topic.space_id == subway.id, Topic.is_deleted == False).all()} if subway else {}
    train_topics = {t.name: t.id for t in db.query(Topic).filter(Topic.space_id == train.id, Topic.is_deleted == False).all()} if train else {}

    docs = [
        # --- 火车空间 (Railway / High-Speed Rail) ---
        {
            'space_id': train.id,
            'topic_id': train_topics.get('泰中高铁 MMS 维保体系'),
            'title': '泰中高铁 MMS 总体设计与六大子系统架构规范 (Contract 2.3)',
            'summary': '涵盖曼谷-呵叻一期 252.2km 维保管理系统总体设计提纲、与 DMIS 调度系统接口规范及作业闭环流程。',
            'tags': ['泰中高铁', 'MMS', 'Contract2.3', '系统架构'],
            'content': """# 泰中高铁 MMS 总体设计与六大子系统架构规范

## 1. 项目工程背景
- **项目名称**：泰国高速铁路合作项目（曼谷 - 呵叻段）合同 2.3。
- **业主**：泰国国家铁路局 (SRT)。
- **总承包商**：IRCON INTERNATIONAL LIMITED。
- **线路里程**：Phase 1 标段全长约 252.2 km。

## 2. MMS 六大核心子系统
1. **设备资产管理 (Equipment Management)**：固定与移动设备全生命周期履历追溯。
2. **作业与分析管理 (Work Management)**：检测数据对接、状态修维修建议模型。
3. **运行与调度管理 (Operation Management)**：作业令签发、与 DMIS 调度联动及天窗修审批。
4. **物资仓储管理 (Material Management)**：应急备品备件库存阈值预警。
5. **综合与标准管理 (Comprehensive Management)**：中泰标准映射、图纸规程沉淀。
6. **系统权限管理 (System Management)**：≥5 级 RBAC 细粒度安全鉴权。
"""
        },
        {
            'space_id': train.id,
            'topic_id': train_topics.get('无砟轨道与线路平顺度'),
            'title': 'TB10621 高速铁路无砟轨道几何状态评定与日常养护标准',
            'summary': '阐述高速铁路无砟轨道静态与动态平顺度检查周期、轨距/水平/高低限度指标及扣件扭矩维护标准。',
            'tags': ['无砟轨道', 'TB10621', '平顺度', '工务养护'],
            'content': """# TB10621 高速铁路无砟轨道几何状态评定与日常养护标准

## 1. 轨道平顺性控制指标 (静态限度)
- **轨距 (Gauge)**：标准值 1435 mm，作业验收容许偏差 ±1 mm，经常保养容许偏差 ±2 mm。
- **水平 (Level)**：作业验收容许偏差 1 mm，经常保养容许偏差 2 mm。
- **高低与轨向 (Profile & Alignment)**：10m 弦测基长下，高低容许偏差 ≤ 2 mm。

## 2. 扣件系统维护
- 弹性分开式扣件扭矩须稳定维持在 **80 ~ 120 N·m**。
- 绝缘轨距块磨损超过 1 mm 须立即更换，确保绝缘电阻满足电务轨道电路要求。
"""
        },
        {
            'space_id': train.id,
            'topic_id': train_topics.get('动车组 (EMU) 运用检修'),
            'title': '高速动车组一级检修作业指导书 (转向架与受电弓专篇)',
            'summary': '规定高速动车组动车段一/二级日常巡检流程、受电弓碳滑板残厚限度及车轮踏面擦伤测定规范。',
            'tags': ['动车组', 'EMU', '一级修', '受电弓', '转向架'],
            'content': """# 高速动车组一级检修作业指导书 (转向架与受电弓专篇)

## 1. 受电弓高压部件巡检
- **碳滑板残厚**：工作面剩余厚度不得小于 **5.0 mm**，表面裂纹宽度超过 0.5 mm 需成组更换。
- **静态接触压力**：升弓至 2.0m 工作高度时，接触压力应维持在 **70 ± 5 N** 范围内。

## 2. 走行部转向架探伤与检测
- 轮对踏面剥离长度单处不得大于 20 mm；两处各不得大于 15 mm。
- 空气弹簧橡胶囊外观无鼓包、无裂纹，左右高度差不得超过 3 mm。
"""
        },
        {
            'space_id': train.id,
            'topic_id': train_topics.get('列控系统与四电集成'),
            'title': 'CTCS-3 级列车运行控制系统车载与地面设备维护手册',
            'summary': '解析车载 ATP、应答器传输模块 (BTM)、无线闭塞中心 (RBC) 越区切换与临时限速 (TSR) 下发机制。',
            'tags': ['列控系统', 'CTCS-3', 'ATP', 'RBC', '四电集成'],
            'content': """# CTCS-3 级列车运行控制系统车载与地面设备维护手册

## 1. 车载子系统 (ATP/ATO)
- **BTM 传输天线**：感应高度距离轨顶标高 **130 ± 10 mm**，天线防护罩无划痕破损。
- **DMI 司机人机界面**：制动模式曲线计算正常，主备系热备冗余自动切换时间小于 0.2 秒。

## 2. 地面 RBC 与临时限速服务器 (TSRS)
- GSM-R / LTE-R 无线链路超时门限设置为 5.0 秒。
- 临时限速指令须经双人调度终端复核后，方可由 TSRS 注入 RBC 生成行车许可 (MA)。
"""
        },
        # --- 地铁空间 (Subway / Metro) ---
        {
            'space_id': subway.id,
            'topic_id': subway_topics.get('车辆与转向架维保'),
            'title': '地铁 B 型车基础制动装置与踏面清扫器检修作业标准',
            'summary': '阐述地铁车辆制动夹钳单元、闸瓦间隙自动调整器日常检查流程及制动管路保压试验规范。',
            'tags': ['地铁车辆', '转向架', '基础制动', 'B型车'],
            'content': """# 地铁 B 型车基础制动装置与踏面清扫器检修作业标准

## 1. 基础制动夹钳单元检修
- **闸瓦有效厚度**：标准厚度 24 mm，检修极限磨耗厚度为 **7 mm**。
- **缓解间隙**：闸瓦与车轮踏面工作间隙标准为 **3 ~ 5 mm**。

## 2. 风管路气密性与保压试验
- 主风缸管路充气至 900 kPa，保压 5 min 压力降不得超过 **10 kPa**。
"""
        },
        {
            'space_id': subway.id,
            'topic_id': subway_topics.get('通信信号与 ATC 系统'),
            'title': 'CBTC 移动闭塞信号系统车地无线通信与联锁排故指南',
            'summary': '针对基于通信的列车控制系统无线丢包、轨旁 AP 漫游切换异常及计算机联锁 (CBI) 故障处理。',
            'tags': ['CBTC', '信号系统', 'ATC', '车地通信', 'CBI联锁'],
            'content': """# CBTC 移动闭塞信号系统车地无线通信与联锁排故指南

## 1. 轨旁 AP 无线通信维护
- 隧道内定向天线驻波比 (VSWR) 应小于 **1.5**。
- 列车通过 AP 重叠覆盖区时，无缝漫游切换延时应小于 50 ms，丢包率小于 0.1%。

## 2. 联锁机双机热备
- A/B 控计算机采用三取二容错架构，故障切换不影响进路锁闭状态。
"""
        },
        {
            'space_id': subway.id,
            'topic_id': subway_topics.get('供电与接触轨/网'),
            'title': 'DC1500V 刚性接触网悬挂装置与汇流排巡检作业规范',
            'summary': '规定地下隧道刚性接触网汇流排接头电阻、接触线磨耗残厚、拉出值及膨胀接头日常检测流程。',
            'tags': ['刚性接触网', 'DC1500V', '汇流排', '牵引供电'],
            'content': """# DC1500V 刚性接触网悬挂装置与汇流排巡检作业规范

## 1. 接触线导高与拉出值
- **导高标称值**：轨顶面至接触线工作面高度 4050 mm，偏差不得超过 ±10 mm。
- **拉出值**：沿汇流排呈正弦波布置，最大拉出值标准为 **±200 mm**。

## 2. 汇流排接头电阻测试
- 测量接头处接触电阻，其值不得大于相同长度汇流排本体电阻的 **1.1 倍**。
"""
        },
        {
            'space_id': subway.id,
            'topic_id': subway_topics.get('工务线路与站务设备'),
            'title': '地铁地下站台门 (PSD) 门机驱动与安全回路维护指导',
            'summary': '全面梳理滑动门驱动电机、同步带张紧度、DCU 控制器参数及关闭锁紧信号互锁回路排故方法。',
            'tags': ['站台门', 'PSD', '屏蔽门', '门机驱动', '安全回路'],
            'content': """# 地铁地下站台门 (PSD) 门机驱动与安全回路维护指导

## 1. 门机机械传动检测
- **同步带张力**：使用张力计测定，中段下垂量施加 10N 压力时形变量不得大于 5 mm。
- **防夹安全检测**：门扇关闭过程中遇 5mm×30mm 矩形测试块必须在 0.3s 内触发重开门机制。

## 2. 安全互锁回路
- 所有滑动门闭锁行程开关串联接入信号安全回路，任何一扇门未闭锁，禁止向列车发出发车信号。
"""
        }
    ]

    for item in docs:
        k = Knowledge(
            space_id=item['space_id'],
            topic_id=item['topic_id'],
            title=item['title'],
            summary=item['summary'],
            content=item['content'],
            content_type='markdown',
            knowledge_type='article',
            source_type='manual',
            owner_id=owner_id,
            status='published',
            visibility='space',
            is_deleted=False,
            current_version_id=1,
            published_at=datetime.now(timezone.utc)
        )
        db.add(k)
        db.flush()

        v = KnowledgeVersion(
            knowledge_id=k.id,
            version_number=1,
            title=k.title,
            content=k.content,
            change_summary='初始技术标准版本录入',
            created_by=owner_id
        )
        db.add(v)

        for tag_name in item['tags']:
            t = db.query(Tag).filter(Tag.name == tag_name).first()
            if not t:
                t = Tag(name=tag_name)
                db.add(t)
                db.flush()
            db.add(KnowledgeTag(knowledge_id=k.id, tag_id=t.id))

    db.commit()
    print(f'SUCCESS: Imported {len(docs)} technical documents.')
except Exception as e:
    db.rollback()
    print(f'ERROR: {e}')
    sys.exit(1)
finally:
    db.close()
