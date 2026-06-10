import streamlit as st
from PIL import Image
import requests
import json
import time
from io import BytesIO

st.set_page_config(page_title="垃圾分类助手", page_icon="♻️", layout="wide")

# ========== 免费模型API ==========
def recognize_image(image):
    """使用Hugging Face免费模型识别图片"""
    try:
        buf = BytesIO()
        image.save(buf, format='JPEG')
        
        # 用免费模型
        API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
        response = requests.post(API_URL, data=buf.getvalue(), timeout=10)
        result = response.json()
        return result, None
    except Exception as e:
        return None, str(e)

def match_garbage_type(label):
    """根据识别标签匹配垃圾类型"""
    label = label.lower()
    
    # 可回收物
    recyclable = ["bottle", "can", "plastic", "glass", "paper", "cardboard", "metal", "aluminum", 
                  "tin", "newspaper", "magazine", "book", "box", "carton", "jar", "container",
                  "water bottle", "soda", "beer", "wine", "drink"]
    for word in recyclable:
        if word in label:
            return "可回收物", "🥫"
    
    # 有害垃圾
    hazardous = ["battery", "light bulb", "lamp", "medicine", "paint", "chemical"]
    for word in hazardous:
        if word in label:
            return "有害垃圾", "🔋"
    
    # 厨余垃圾
    kitchen = ["food", "fruit", "apple", "banana", "orange", "vegetable", "meat", "bone",
               "egg", "bread", "rice", "noodle", "peel", "leftover", "meal"]
    for word in kitchen:
        if word in label:
            return "厨余垃圾", "🍎"
    
    # 其他垃圾
    return "其他垃圾", "🗑️"

# ========== 界面 ==========
st.title("♻️ AI垃圾分类智能助手")
st.markdown("### 📸 拍照/上传 → 🤖 免费AI识别 → 📋 自动分类")
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
                st.info("💡 提示：可能是模型正在加载，等10秒再试一次")
            elif result and isinstance(result, list) and len(result) > 0:
                top = result[0]
                item_name = top.get("label", "未知物体")
                confidence = top.get("score", 0)
                category, icon = match_garbage_type(item_name)
                
                color_map = {"可回收物": "#2196F3", "有害垃圾": "#F44336", "厨余垃圾": "#4CAF50", "其他垃圾": "#9E9E9E"}
                color = color_map.get(category, "#333")
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color}15, {color}05); border: 3px solid {color}; border-radius: 20px; padding: 25px; margin-bottom: 20px;">
                    <div style="font-size: 60px; text-align: center;">{icon}</div>
                    <h2 style="text-align: center; color: {color};">AI识别：{item_name}</h2>
                    <h3 style="text-align: center;">分类：<span style="color: {color}; font-size: 28px;">{category}</span></h3>
                    <p style="text-align: center;">置信度：{confidence:.1%}</p >
                </div>
                """, unsafe_allow_html=True)
                
                if len(result) > 1:
                    st.markdown("**其他可能：**")
                    for item in result[1:4]:
                        st.markdown(f"- {item.get('label', '未知')} ({item.get('score', 0):.1%})")
                
                st.markdown("---")
                st.markdown("### 📋 处理建议")
                advice_map = {
                    "可回收物": "清空内容物 → 清洗干净 → 投入蓝色可回收桶",
                    "有害垃圾": "投入红色有害垃圾回收箱 → 小心轻放",
                    "厨余垃圾": "沥干水分 → 投入绿色厨余垃圾桶",
                    "其他垃圾": "投入灰色其他垃圾桶"
                }
                st.info(advice_map.get(category, "请确认后投放"))
                
                st.markdown("### 🌍 环保标语")
                slogans = {
                    "可回收物": "垃圾分一分，环境美十分！",
                    "有害垃圾": "有害垃圾单独放，环境保护靠大家！",
                    "厨余垃圾": "厨余变成宝，大地开口笑！",
                    "其他垃圾": "减少垃圾，从源头做起！"
                }
                st.success(slogans.get(category, "垃圾分类，人人有责！"))
                
                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("识别耗时", f"{elapsed:.2f}秒")
                m2.metric("置信度", f"{confidence:.1%}")
                m3.metric("API", "免费")
            else:
                st.warning("模型加载中，请等10秒后再试！")
                st.info("💡 首次使用模型需要预热，再上传一次就好")
    else:
        st.info("👈 请先上传一张图片")
        st.markdown("---")
        st.markdown("### 🌟 特性")
        st.markdown("""
        - 🆓 **完全免费**：使用开源模型，无限制使用
        - 🤖 **AI识别**：自动识别图片中的物体
        - 🗑️ **自动分类**：可回收/有害/厨余/其他
        """)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#999;"><p>🤖 基于开源AI模型 | 完全免费 | 不限次数</p ></div>', unsafe_allow_html=True)
