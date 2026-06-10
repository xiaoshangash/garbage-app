import streamlit as st
from PIL import Image
import requests
import base64
import json
import time
from io import BytesIO

st.set_page_config(page_title="垃圾分类助手", page_icon="♻️", layout="wide")

API_KEY = "uSagY45hN0kwCQL1nI9IK9ti"
SECRET_KEY = "Nogp6CdDtFp6Kl349vE7GAHBzjurYZ2O"

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    response = requests.get(url, params=params)
    return response.json().get("access_token")

def recognize_image(image):
    token = get_access_token()
    if not token:
        return None, "API获取失败"
    buf = BytesIO()
    image.save(buf, format='JPEG')
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    url = f"https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general?access_token={token}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"image": img_base64}
    response = requests.post(url, headers=headers, data=data)
    return response.json(), None

GARBAGE_DB = {
    "塑料瓶": {"类别": "可回收物", "图标": "🥤", "处理": "清空液体 → 压扁 → 投入蓝色可回收桶", "原因": "塑料可以回收重新制成新的塑料制品", "标语": "塑料回收一小步，绿色地球一大步！"},
    "易拉罐": {"类别": "可回收物", "图标": "🥫", "处理": "清空内容物 → 压扁 → 投入蓝色可回收桶", "原因": "铝罐可以无限次回收利用", "标语": "回收一个铝罐，节省一台电视看3小时的电！"},
    "玻璃瓶": {"类别": "可回收物", "图标": "🍾", "处理": "清洗干净 → 去掉瓶盖 → 投入蓝色可回收桶", "原因": "玻璃可以100%回收再利用", "标语": "玻璃新生，循环不息！"},
    "纸板箱": {"类别": "可回收物", "图标": "📦", "处理": "拆开压平 → 保持干燥 → 投入蓝色可回收桶", "原因": "回收1吨纸板可以少砍17棵树", "标语": "回收一张纸，拯救一棵树！"},
    "报纸": {"类别": "可回收物", "图标": "📰", "处理": "保持干燥 → 叠放整齐 → 投入蓝色可回收桶", "原因": "废纸回收可以制成再生纸", "标语": "今天的报纸，明天的课本！"},
    "电池": {"类别": "有害垃圾", "图标": "🔋", "处理": "放入有害垃圾回收箱 → 不要扔普通垃圾桶", "原因": "电池含重金属，会污染土壤和水源", "标语": "一节电池污一亩地，回收处理要牢记！"},
    "灯泡": {"类别": "有害垃圾", "图标": "💡", "处理": "用原包装包好 → 投入有害垃圾回收箱", "原因": "灯泡含水银，对人体和环境有害", "标语": "小小灯泡危害大，正确回收靠大家！"},
    "苹果核": {"类别": "厨余垃圾", "图标": "🍎", "处理": "沥干水分 → 投入绿色厨余垃圾桶", "原因": "可以堆肥变成有机肥料", "标语": "厨余变成宝，大地开口笑！"},
    "剩饭": {"类别": "厨余垃圾", "图标": "🍚", "处理": "沥干汤汁 → 投入绿色厨余垃圾桶", "原因": "可以发酵产生沼气发电", "标语": "光盘行动要记牢，剩饭回收也是宝！"},
    "纸巾": {"类别": "其他垃圾", "图标": "🧻", "处理": "投入灰色其他垃圾桶", "原因": "纸巾遇水即化，无法回收再造", "标语": "纸巾虽小，分类要好！"},
}

CATEGORY_KEYWORDS = {
    "可回收物": ["塑料", "瓶", "罐", "铝", "纸", "板", "箱", "玻璃", "金属", "铁", "钢", "铜", "报纸", "书", "杂志"],
    "有害垃圾": ["电池", "灯", "药", "油漆", "农药", "化学品", "汞", "水银"],
    "厨余垃圾": ["食物", "水果", "蔬菜", "饭", "菜", "肉", "骨头", "壳", "核", "剩", "苹果", "香蕉", "橘子"],
    "其他垃圾": ["纸巾", "卫生纸", "尿布", "灰", "土", "陶瓷", "砖", "瓦"]
}

def find_garbage_info(name):
    for key in GARBAGE_DB:
        if key in name:
            return GARBAGE_DB[key], key
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name:
                for k, v in GARBAGE_DB.items():
                    if v["类别"] == category:
                        return v, k
                return {"类别": category, "图标": "🗑️", "处理": "请查看当地分类指南", "原因": "AI识别结果，建议确认", "标语": "垃圾分类，人人有责！"}, name
    return {"类别": "其他垃圾", "图标": "🗑️", "处理": "无法精确识别，建议投入灰色其他垃圾桶", "原因": "建议进一步确认该物品的分类", "标语": "爱护环境，从垃圾分类开始！"}, name

st.title("♻️ AI垃圾分类智能助手")
st.markdown("### 📸 拍照/上传 → 🤖 百度AI识别 → 📋 自动分类建议")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 上传图片")
    uploaded_file = st.file_uploader("选择图片", type=['jpg', 'jpeg', 'png'])
    camera_file = st.camera_input("拍照")
    image_file = uploaded_file or camera_file

    if image_file:
        image = Image.open(image_file).convert('RGB')
        st.image(image, caption="你的图片", use_column_width=True)

with col2:
    st.subheader("🤖 AI识别结果")
    
    if image_file:
        with st.spinner("🧠 AI正在分析中..."):
            start_time = time.time()
            result, error = recognize_image(image)
            elapsed = time.time() - start_time
            
            if error:
                st.error(f"识别失败：{error}")
            elif result and "result" in result and len(result["result"]) > 0:
                top_item = result["result"][0]
                item_name = top_item["keyword"]
                confidence = top_item["score"]
                info, matched_name = find_garbage_info(item_name)
                color_map = {"可回收物": "#2196F3", "有害垃圾": "#F44336", "厨余垃圾": "#4CAF50", "其他垃圾": "#9E9E9E"}
                color = color_map.get(info['类别'], "#333")
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color}15, {color}05); border: 3px solid {color}; border-radius: 20px; padding: 25px; margin-bottom: 20px;">
                    <div style="font-size: 60px; text-align: center;">{info['图标']}</div>
                    <h2 style="text-align: center; color: {color};">百度AI识别：{item_name}</h2>
                    <h3 style="text-align: center;">属于：<span style="color: {color}; font-size: 28px;">{info['类别']}</span></h3>
                    <p style="text-align: center;">置信度：{confidence:.1%}</p >
                </div>
                """, unsafe_allow_html=True)
                
                if len(result["result"]) > 1:
                    st.markdown("**其他可能的物体：**")
                    for item in result["result"][1:4]:
                        st.markdown(f"- {item['keyword']} ({item['score']:.1%})")
                
                st.markdown("---")
                st.markdown("### 📋 处理步骤")
                st.info(info['处理'])
                st.markdown("### 💡 为什么要这样处理？")
                st.success(info['原因'])
                st.markdown("### 🌍 环保标语")
                st.markdown(f'<div style="background-color:#E8F5E9; border-left:5px solid #4CAF50; padding:15px; border-radius:5px; font-size:18px;">"{info["标语"]}"</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### ⚡ 系统性能")
                m1, m2, m3 = st.columns(3)
                m1.metric("AI识别耗时", f"{elapsed:.2f}秒", delta="✅ 达标")
                m2.metric("识别置信度", f"{confidence:.1%}")
                m3.metric("支持物体数", "10万+")
            else:
                st.warning("未识别到物体，请换个角度再拍一张！")
    else:
        st.info("👈 请先上传或拍摄一张垃圾图片")
        st.markdown("---")
        st.markdown("### 🌟 功能介绍")
        st.markdown("""
        - ✅ **真实AI识别**：基于百度AI，可识别10万+物体
        - ✅ **自动分类**：可回收物/有害垃圾/厨余垃圾/其他垃圾
        - ✅ **处理建议**：详细告诉你怎么扔
        - ✅ **环保标语**：每次都有不一样的环保知识
        """)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#999;"><p>🤖 基于百度AI图像识别 | 垃圾分类智能助手 | 可识别10万+物体</p ></div>', unsafe_allow_html=True)
