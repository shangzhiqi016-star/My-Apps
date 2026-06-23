"""
待办清单应用 (Todo List App)
基于 Python + Streamlit 构建
适合新手阅读，所有代码均附带中文注释
"""

import streamlit as st
import datetime  # 用于处理日期和倒计时计算

# ============================================================
# 页面基础配置
# ============================================================
st.set_page_config(
    page_title="待办清单",
    page_icon="✅",
    layout="centered",  # 居中布局，在宽屏上也能舒适阅读
)

# ============================================================
# 初始化 session_state（会话状态）
# session_state 是 Streamlit 用来在多次刷新间保存数据的字典
# 类似于一个"记忆盒子"，页面重新运行时数据不会丢失
# ============================================================
if "tasks" not in st.session_state:
    # tasks 是一个列表，每个元素是一个字典：
    # {"id": 自增编号, "content": "任务内容", "deadline": date对象, "done": True/False}
    st.session_state.tasks = []

if "next_id" not in st.session_state:
    # 自增 ID 计数器，为每条任务生成唯一编号，解决排序后 key 错乱的问题
    st.session_state.next_id = 1


# ============================================================
# 辅助函数
# ============================================================
def add_task():
    """将输入框中的文字和截止日期添加为一条新任务"""
    new_task_text = st.session_state.input_box.strip()  # strip() 去掉首尾空格

    if new_task_text == "":
        # 空内容不添加，直接返回
        return

    # 从日期选择器读取截止日期（如果没有选，默认用今天）
    deadline = st.session_state.get("deadline_input", datetime.date.today())
    # 如果用户没有修改日期选择器，deadline_input 可能不存在，容错处理
    if deadline is None:
        deadline = datetime.date.today()

    # 向任务列表追加一条新任务
    st.session_state.tasks.append({
        "id": st.session_state.next_id,       # 唯一 ID
        "content": new_task_text,
        "deadline": deadline,
        "done": False,
    })

    # ID 计数器自增
    st.session_state.next_id += 1

    # 添加成功后清空输入框（通过修改 session_state 中 input_box 的值）
    st.session_state.input_box = ""


def toggle_task(task_id: int):
    """切换指定任务的完成状态（勾选 / 取消勾选）—— 通过任务 ID 查找"""
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            break


def delete_task(task_id: int):
    """删除指定 ID 的任务"""
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]


def calc_days_remaining(deadline: datetime.date) -> int:
    """计算距离截止日期还有多少天。
    返回值：正数=还有n天，0=今天到期，负数=已过期n天
    """
    today = datetime.date.today()
    return (deadline - today).days


def get_countdown_text(days: int) -> tuple[str, str]:
    """根据剩余天数返回 (显示文字, CSS类名)。
    CSS类名用于控制颜色：'urgent' 红色 / 'normal' 默认 / 'overdue' 深红
    """
    if days > 1:
        return f"还有{days}天", "normal"
    elif days == 1:
        return "还有1天", "normal"
    elif days == 0:
        return "今天到期", "urgent"
    else:
        return f"已过期{-days}天", "overdue"


def sort_key(task: dict):
    """排序依据：
    1. 未完成的任务排前面，已完成的任务排后面
    2. 未完成任务中，截止日期越近越靠前
    3. 已完成任务中，保持原有顺序（按 ID 排序）
    """
    if task["done"]:
        # 已完成：排在后面，large number + id 保持稳定
        return (1, 0, task["id"])
    else:
        # 未完成：按截止日期升序（近的在前），同一天按 ID 排序
        days = calc_days_remaining(task["deadline"])
        return (0, days, task["id"])  # days 越小（越紧急）越靠前


# ============================================================
# 自定义 CSS 样式 —— 打造现代简洁的卡片风格
# ============================================================
st.markdown("""
<style>
    /* ---------- 整体页面背景与字体 ---------- */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* ---------- 顶部标题 ---------- */
    .app-title {
        text-align: center;
        font-size: 36px !important;   /* 比"任务列表"(h3约20px)大3个字号，明显但不夸张 */
        font-weight: 700 !important;
        color: #2c3e50 !important;
        margin-bottom: 4px;
        letter-spacing: 1px;
        line-height: 1.3 !important;
    }
    /* 当前日期 */
    .current-date {
        text-align: center;
        font-size: 15px;          /* 小于标题 */
        color: #95a5a6;           /* 灰色字体 */
        margin-bottom: 4px;
    }
    .app-subtitle {
        text-align: center;
        font-size: 14px;
        color: #95a5a6;
        margin-bottom: 20px;
    }

    /* ---------- 统计栏样式 ---------- */
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 32px;
        padding: 20px 0 10px 0;
    }
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 16px 32px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        text-align: center;
        min-width: 160px;
    }
    .stat-number {
        font-size: 36px;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .stat-number.pending { color: #e67e22; }
    .stat-number.done    { color: #27ae60; }
    .stat-label {
        font-size: 13px;
        color: #888;
        margin: 4px 0 0 0;
    }

    /* ---------- 输入区域容器 ---------- */
    .input-container {
        background: white;
        border-radius: 20px;
        padding: 24px 28px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .input-row {
        display: flex;
        gap: 12px;
        align-items: center;
    }

    /* ---------- 单条任务卡片 ---------- */
    .task-card {
        background: white;
        border-radius: 14px;
        padding: 14px 20px;
        margin-bottom: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
        border-left: 5px solid #3498db;
    }
    /* 已完成的任务卡片：左侧色条变为绿色，整体微微变淡 */
    .task-card.done-card {
        border-left-color: #27ae60;
        background: #f9fdf9;
    }
    /* 今天到期的任务卡片：左侧色条变为红色 */
    .task-card.urgent-card {
        border-left-color: #e74c3c;
        background: #fff9f9;
    }
    .task-card:hover {
        box-shadow: 0 4px 18px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }

    /* ---------- 任务文字 ---------- */
    .task-content {
        font-size: 16px;
        color: #2c3e50;
        margin: 0;
    }
    /* 已完成的文字显示删除线 + 灰色 */
    .task-content.done-text {
        text-decoration: line-through;
        color: #bdc3c7;
    }

    /* ---------- 倒计时标签 ---------- */
    .countdown-badge {
        display: inline-block;
        font-size: 12px;
        font-weight: 600;
        border-radius: 8px;
        padding: 3px 10px;
        margin-left: 10px;
    }
    .countdown-badge.normal {
        background: #eaf7ee;
        color: #27ae60;
    }
    .countdown-badge.urgent {
        background: #ffeaea;
        color: #e74c3c;
    }
    .countdown-badge.overdue {
        background: #fde8e8;
        color: #c0392b;
        font-weight: 700;
    }

    /* ---------- 紧急标记 ---------- */
    .urgent-tag {
        display: inline-block;
        font-size: 12px;
        font-weight: 700;
        color: #fff;
        background: #e74c3c;
        border-radius: 6px;
        padding: 3px 8px;
        margin-left: 8px;
        animation: pulse 1.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%      { opacity: 0.6; }
    }

    /* ---------- 删除按钮 ---------- */
    .delete-btn button {
        background: transparent !important;
        border: 1.5px solid #e74c3c !important;
        color: #e74c3c !important;
        border-radius: 10px !important;
        padding: 6px 16px !important;
        font-size: 13px !important;
        transition: all 0.2s ease !important;
    }
    .delete-btn button:hover {
        background: #e74c3c !important;
        color: white !important;
    }

    /* ---------- 空状态提示 ---------- */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #b0b0b0;
        font-size: 16px;
    }
    .empty-state .icon { font-size: 48px; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 页面主体内容
# ============================================================

# ---- 标题 & 当前日期 ----
st.markdown('<p class="app-title">✅ 我的待办清单</p>', unsafe_allow_html=True)

# 显示当前日期（中文格式，居中灰色）
today = datetime.date.today()
# 将日期格式化为中文风格：2026年6月22日 星期一
weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
weekday_str = weekday_names[today.weekday()]
date_str = f"{today.year}年{today.month}月{today.day}日 {weekday_str}"
st.markdown(f'<p class="current-date">📅 {date_str}</p>', unsafe_allow_html=True)

st.markdown('<p class="app-subtitle">好记性不如烂笔头，把要做的事情记下来吧</p>', unsafe_allow_html=True)

# ---- 统计数据 ----
# 计算未完成和已完成的数量
pending_count = sum(1 for t in st.session_state.tasks if not t["done"])
done_count   = sum(1 for t in st.session_state.tasks if t["done"])

st.markdown(f"""
<div class="stats-container">
    <div class="stat-card">
        <p class="stat-number pending">{pending_count}</p>
        <p class="stat-label">📋 待完成</p>
    </div>
    <div class="stat-card">
        <p class="stat-number done">{done_count}</p>
        <p class="stat-label">🎉 已完成</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- 输入区域 ----
st.markdown('<div class="input-container">', unsafe_allow_html=True)

# 任务内容输入框
# key="input_box" 将输入值绑定到 session_state.input_box
st.text_input(
    label="输入新的任务",
    placeholder="例如：买牛奶、写作业、回复邮件……",
    key="input_box",
    label_visibility="collapsed",
    on_change=add_task,  # 按回车时自动添加
)

# 截止日期选择器 + 添加按钮（并排两列）
col_date, col_btn = st.columns([1.5, 1])
with col_date:
    # date_input 的值通过 key="deadline_input" 绑定到 session_state
    # 默认值设为今天，用户可自行修改
    st.date_input(
        label="📅 截止日期",
        value=datetime.date.today(),
        key="deadline_input",
        min_value=datetime.date(2020, 1, 1),   # 最早可选日期
        max_value=datetime.date(2099, 12, 31), # 最晚可选日期
        format="YYYY-MM-DD",                    # 日期显示格式
    )
with col_btn:
    # 按钮放在日期选择器旁边，视觉上更紧凑
    st.button(
        "➕ 添加任务",
        on_click=add_task,
        use_container_width=True,
        type="primary",
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---- 任务列表 ----
st.markdown("### 📝 任务列表")

# 获取所有任务，并按紧急程度排序
tasks = st.session_state.tasks
sorted_tasks = sorted(tasks, key=sort_key)  # 排序：越紧急越靠前

if len(sorted_tasks) == 0:
    # 空列表时显示友好的提示
    st.markdown("""
    <div class="empty-state">
        <div class="icon">📭</div>
        <p>还没有任务呢，在上方添加一条吧～</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # 遍历排序后的每条任务，渲染为卡片
    for task in sorted_tasks:
        task_id = task["id"]
        content = task["content"]
        is_done = task["done"]
        deadline = task["deadline"]

        # ---- 计算倒计时 ----
        days = calc_days_remaining(deadline)
        countdown_text, countdown_css = get_countdown_text(days)

        # ---- 判断是否为今天到期（需要标红 + 紧急标记）----
        is_urgent = (not is_done) and (days == 0)

        # ---- 根据完成状态和紧急状态决定卡片 CSS 类名 ----
        if is_done:
            card_class = "task-card done-card"
        elif is_urgent:
            card_class = "task-card urgent-card"
        else:
            card_class = "task-card"

        text_class = "task-content done-text" if is_done else "task-content"

        # ---- 渲染任务卡片 ----
        # 用 st.container 配合自定义 HTML 实现灵活布局
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

        col_check, col_main, col_del = st.columns([0.06, 0.79, 0.15])

        with col_check:
            # 复选框 —— checked 属性绑定到 task["done"]
            st.checkbox(
                label="",
                value=is_done,
                key=f"check_{task_id}",              # 用唯一 ID 而非索引，排序后 key 不乱
                on_change=toggle_task,
                args=(task_id,),
                label_visibility="collapsed",
            )

        with col_main:
            # 任务文字 + 倒计时 + 紧急标记
            urgent_html = ""
            if is_urgent:
                # 今天到期且未完成：显示红色"紧急"标记
                urgent_html = '<span class="urgent-tag">⚠️ 紧急</span>'

            # 倒计时显示（已完成的任务也显示，但颜色变淡）
            if is_done:
                # 已完成的任务显示灰色倒计时
                badge_html = f'<span class="countdown-badge" style="background:#f0f0f0;color:#bbb;">{countdown_text}</span>'
            else:
                badge_html = f'<span class="countdown-badge {countdown_css}">{countdown_text}</span>'

            st.markdown(
                f'<span class="{text_class}">{content}</span>'
                f'{badge_html}'
                f'{urgent_html}',
                unsafe_allow_html=True,
            )

        with col_del:
            # 删除按钮
            st.button(
                "🗑 删除",
                key=f"del_{task_id}",                 # 用唯一 ID 而非索引
                on_click=delete_task,
                args=(task_id,),
                use_container_width=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 页脚提示
# ============================================================
st.markdown("---")
st.caption("💡 提示：输入任务内容、选择截止日期后，按 **回车** 或点击 **添加任务** 即可。"
           "任务按紧急程度自动排序，今天到期的会标红提醒。")
