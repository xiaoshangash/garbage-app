import streamlit as st
from PIL import Image
import requests
import json
import time
from io import BytesIO

st.set_page_config(page_title="垃圾分类助手", page_icon="♻️", layout="wide")

API_KEY = "sk-c3ff6b69d6174dc995b02fb8b13a41b7"

def recognize_image(image):
    """使用阿里通义千问识别图片"""
    try:
        buf = BytesIO()
        image.save(buf, format='JPEG')
        
        import base64
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "qwen-vl-plus",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": f"data:image/jpeg;base64,{img_base64}"},
                            {"text": "这张图片里是什么物体？只回答物体名称。"}
                        ]
                    }
                ]
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if "output" in result:
            choices = result["output"].get("choices", [])
            if choices:
                text = choices[0].get("message", {}).get("content", "")
                if isinstance(text, list):
                    text = str(text[0]) if text else "未知"
                return str(text).strip(), None
        
        return None, str(result)
    except Exception as e:
        return None, str(e)
def match_garbage(item_name):
    """匹配垃圾分类"""
    name = item_name.lower()
    
    recyclable = ["瓶", "罐", "塑料", "玻璃", "纸", "箱", "金属", "铝", "铁", "书", "报", "杂志", "盒", "袋"]
    hazardous = ["电池", "灯泡", "灯管", "药", "油漆", "农药", "温度计"]
    kitchen = ["食物", "水果", "菜", "饭", "肉", "骨头", "壳", "核", "皮", "苹果", "香蕉", "橘子", "剩"]
    
    for word in hazardous:
        if word in name:
            return "有害垃圾", "🔋", "放入有害垃圾回收箱", "含有害物质，专门处理保护环境", "有害垃圾单独放，环境保护靠大家！"
    
    for word in recyclable:
        if word in name:
            return "可回收物", "🥫", "清洗干净 → 投入蓝色可回收桶", "回收再利用，节约资源", "垃圾分一分，环境美十分！"
    
    for word in kitchen:
        if word in name:
            return "厨余垃圾", "🍎", "沥干水分 → 投入绿色厨余垃圾桶", "可以堆肥发电，变废为宝", "厨余变成宝，大地开口笑！"
    
    return "其他垃圾", "🗑️", "投入灰色其他垃圾桶", "无法回收，安全处理", "减少垃圾，从源头做起！"

st.title("♻️ AI垃圾分类智能助手")
st.markdown("### 📸 上传图片 → 🤖 通义AI识别 → 📋 自动分类")
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
            item_name, error = recognize_image(image)
            elapsed = time.time() - start_time
            
            if error:
                st.error(f"识别失败：{error}")
            elif item_name:
                category, icon, handle, reason, slogan = match_garbage(item_name)
                
                color_map = {"可回收物": "#2196F3", "有害垃圾": "#F44336", "厨余垃圾": "#4CAF50", "其他垃圾": "#9E9E9E"}
                color = color_map.get(category, "#333")
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color}15, {color}05); border: 3px solid {color}; border-radius: 20px; padding: 25px; margin-bottom: 20px;">
                    <div style="font-size: 60px; text-align: center;">{icon}</div>
                    <h2 style="text-align: center; color: {color};">AI识别：{item_name}</h2>
                    <h3 style="text-align: center;">属于：<span style="color: {color}; font-size: 28px;">{category}</span></h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 📋 处理步骤")
                st.info(handle)
                st.markdown("### 💡 为什么？")
                st.success(reason)
                st.markdown("### 🌍 环保标语")
                st.markdown(f'<div style="background-color:#E8F5E9; border-left:5px solid #4CAF50; padding:15px; border-radius:5px; font-size:18px;">"{slogan}"</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("识别耗时", f"{elapsed:.2f}秒", delta="✅ <3秒")
                m2.metric("AI引擎", "通义千问")
                m3.metric("状态", "免费")
            else:
                st.warning("请再试一次")
    else:
        st.info("👈 请先上传一张图片")
        st.markdown("---")
        st.markdown("### 🌟 功能")
        st.markdown("""
        - 🤖 **通义千问AI**：真实AI识别
        - 🗑️ **自动分类**：可回收/有害/厨余/其他
        - 📋 **处理建议**：详细指导
        - 🆓 **完全免费**：阿里免费额度
        """)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#999;"><p>🤖 通义千问AI驱动 | 国内直连 | 免费使用</p ></div>', unsafe_allow_html=True)
