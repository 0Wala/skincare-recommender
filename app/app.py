import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Glow Guide", layout="wide")

st.markdown("""
    <style>
    /* Start centered, then nudge slightly left */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        margin-left: -160px;  
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 2.2rem;
        font-weight: 700;
        padding: 18px 40px;
    }
    /* GLOBAL FONT STYLING */
    </style>
    """ , unsafe_allow_html=True)


st.markdown("""
    <style>
    
    html, body, [class*="css"] {
        font-size: 1.05rem !important;  /* ~30% bigger than default */
        font-family: 'Segoe UI', sans-serif;
    }

    /* Form labels like "Select your skin type" */
    .stSelectbox label, .stRadio label, .stMultiSelect label {
        font-size: 1.2rem !important;
    }

    /* Buttons like "Get My Recommendations" */
    button[kind="primary"] {
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# dataset path
df = pd.read_csv("data/skincare.csv")


# App title
st.title("Glow Guide – Your Personalized Skincare Companion ")


# my tabs
tabs = st.tabs(["🌸 Glow Guide", "✨ Get Recommendation", "📘 Skin Care 101"])

# --------------------
# 🌸 TAB 1: Glow Guide
# --------------------
with tabs[0]:

    st.markdown("""
    Welcome to **Glow Guide**, your personal space to navigate skincare with ease ; helping you understand your skin, explore product matches, and care for your skin with clarity and confidence. <br>
    We're here to help you explore what works best for your skin — and walk with you on a journey of care, nourishment, and gentleness 💛
    """, unsafe_allow_html=True)
 
    
    st.image ("app/images/glow_intro.png", use_container_width=True)



    st.markdown(""""
   ⚠️ *Disclaimer: While we offer personalized suggestions based on your skin needs, this guide is not a substitute for professional advice.
    Kindly consult a dermatologist or licensed skincare professional for ongoing skin concerns and tailored treatment plans.*
    """)
    
    st.markdown("---")


    st.info(" Ready to start your journey? Head over to **Get Recommendation** to find your perfect skincare match. Have fun exploring! 🌸")

    
# -------------------------------
# ✨ TAB 2: Get Recommendation
# -------------------------------
with tabs[1]:
    st.subheader("✨ Get Your Personalized Skincare Picks")
    st.write("Select your preferences below to discover products that match your skin needs.")

    # Skin Type 
    skin_types = sorted(set([stype.strip() for sublist in df['skin_type'].dropna() for stype in sublist.split(",")]))
    selected_skin_type = st.radio("🌿 What's your skin type?", options=skin_types, horizontal=True)

    # Skin Concerns
    all_concerns = sorted(set([c.strip() for sublist in df['concerns'].dropna() for c in sublist.split(",") if c.strip().lower() != "anti-bacterial"]))
    selected_concerns = st.multiselect("💬 What skin concerns do you have?", options=all_concerns)

    # Desired Outcomes – below concerns
    desired_outcomes = sorted([
        'hydration', 'moisturizing', 'radiance', 'anti-aging', 'smoother skin', 'exfoliating', 'soothing',
        'oil control', 'deep cleansing', 'brightening', 'even skin tone', 'skin barrier repair',
        'de-puffing', 'firm skin', 'acne treatment', 'UV protection', 'pore minimizing'
    ])
    selected_outcomes = st.multiselect("What are your desired results?", options=desired_outcomes)

    # Reverse mapping outcomes → concerns
    from collections import defaultdict
    outcome_to_concerns = defaultdict(list)
    for concern, outcomes in {
        'dryness': ['hydration', 'moisturizing'],
        'dullness': ['radiance'],
        'fine lines and wrinkles': ['anti-aging'],
        'uneven skin texture': ['smoother skin', 'exfoliating'],
        'irritation': ['soothing'],
        'excess oil': ['oil control'],
        'clogged pores': ['deep cleansing'],
        'hyperpigmentation': ['brightening', 'even skin tone'],
        'damaged skin barrier': ['skin barrier repair'],
        'puffiness': ['de-puffing'],
        'sagging': ['firm skin'],
        'dark circles': ['brightening'],
        'acne': ['acne treatment'],
        'redness': ['soothing'],
        'sun damage': ['UV protection'],
        'enlarged pores': ['pore minimizing'],
        'stretch marks': ['exfoliating'],
        
    }.items():
        for outcome in outcomes:
            outcome_to_concerns[outcome].append(concern)

    # Convert selected outcomes to additional concerns
    matched_concerns = []
    for outcome in selected_outcomes:
        matched_concerns.extend(outcome_to_concerns.get(outcome, []))
    matched_concerns = list(set(matched_concerns))

    final_concerns = list(set(matched_concerns + selected_concerns))

    # Product Type 
    product_types = sorted(df['product_type'].dropna().unique())
    selected_type = st.selectbox("🧴 Pick a product type :", options=list(product_types))

    # Price Range 
    price_ranges = ["0–2500 Ksh", "2500–5000 Ksh", "5000–10000 Ksh", "Above 10000 Ksh", "All"]
    selected_price_range = st.radio("💵  Choose your price range:", options=price_ranges, horizontal=True)

    # generating recommendations button
    if st.button("Get My Recommendations"):
        # Preprocess data
        df['skin_type_list'] = df['skin_type'].apply(lambda x: [s.lower().strip() for s in x.split(",")])
        df['concerns_list'] = df['concerns'].apply(lambda x: [c.lower().strip() for c in x.split(",") if c])

        # Filter skin type and concerns
        filtered = df[
            df['skin_type_list'].apply(lambda x: selected_skin_type.lower() in x) &
            df['concerns_list'].apply(lambda x: any(c.lower() in x for c in final_concerns))
        ]

        # Filter product type if selected
        if selected_type != "(None)":
            filtered = filtered[filtered['product_type'] == selected_type]

        # Price range
        if selected_price_range != "All":
            if selected_price_range == "Above 10000 Ksh":
                filtered = filtered[filtered['price_ksh'] > 10000]
            else:
                min_price, max_price = map(int, selected_price_range.replace("Ksh", "").split("–"))
                filtered = filtered[
                    (filtered['price_ksh'] >= min_price) & (filtered['price_ksh'] <= max_price)
                ]

        # Show results
        if not filtered.empty:
            st.success(f"🎉 Found {len(filtered)} matching product(s):")
            st.dataframe(filtered[['product_name', 'product_type', 'price_ksh']].reset_index(drop=True))
            
             # 💾 Download button 
            csv = filtered[['product_name', 'product_type', 'price_ksh']].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download My Picks",
                data=csv,
                file_name='glow_guide_recommendations.csv',
                mime='text/csv'
    )
    
        else:
            st.warning("Sorry, no matching products found. Try adjusting your preferences.")
                         

# -------------------------------
# 📘 TAB 3: Skin Care 101 – Product Usage + Tips
# -------------------------------
with tabs[2]:
    st.subheader("📘 Skin Care 101 – Know What You Use")
    st.write("Let’s walk through how to use each skincare product effectively, and how to build consistency with grace.")

    st.markdown("---")

    st.markdown("### 🧴 How to Use Each Product")

    st.markdown("**1. Facial Cleanser:**")
    st.markdown("""
        - Wash your face (max 2x daily);morning and night.
        - Use your fingertips in soft, circular motions for **30–60 seconds**.
        - For dry skin, it’s okay to use only water in the morning.
        - Avoid over-cleansing as it may strip your skin of natural oils.
        """)

    st.markdown("**2. Toner:**")
    st.markdown("""
        - Apply after cleansing. A toner rebalances your skin's pH and prepares it for better absorption of follow-up products.
        - Apply a few drops of toner to a cotton pad or your palms, and gently pat it over your face and neck. Allow it absorb before moving onto the next step.
        - Avoid toners with **fragrance** if you have sensitive skin.
        """)

    st.markdown("**3. Serum:**")
    st.markdown("""
        - Use after toner or on clean skin (AM + PM).
        -**AM serums** protects and hydrates your skin during the day while**PM serums** repair and rejuvenate your skin overnight.
        - Gently pat into your face and let it absorb fully before layering.
        - Choose a serum that targets your concern (e.g., dark spots, acne scars).
        """)

    st.markdown("**4. Moisturizer:**")
    st.markdown("""
        - Locks in hydration and seals in previous steps.
        - AM moisturizers often contain SPF and vitamins.
        - PM moisturizers may have rich ingredients for overnight repair.
        - Wait 2–3 mins after serum before applying.
        """)

    st.markdown("**5. Sunscreen:**")
    st.markdown("""
        - Apply Every morning as the final step of your routine (and reapply during the day as needed)
        - Use a broad-spectrum sunscreen with at least SPF 30. Apply a generous amount(two fingers' worth of product) to your face and neck.
        - Reapply every 2–3 hours, even indoors, especially if you’re in front of a window or using screens.
        - If you wear makeup, consider a setting spray with SPF for easy reapplication.
        """)

    st.markdown("### 💡 Glowing Habits to Keep In Mind")
    st.markdown("""
- **Don’t switch products too often.** Your skin needs time to adapt.  
- **Consistency is key.** Real results take time.  
- **Listen to your skin.** If a product irritates or breaks you out, stop using it.  
- **Patch test new products.** Apply a small amount on your wrist or behind your ear to check for reactions before using it on your face.  
- **If you wear makeup**, consider a setting spray with SPF for easy reapplication.
""")

    with st.expander("🔍 Not sure about your skin type? Click here for a quick self-check."):
        st.markdown("""
         " Wash your face with a gentle cleanser and wait for about an hour without applying anything."
        - **If Normal**: skin feels comfortable and balanced, not oily or dry.
        - **If Oily**: skin becomes shiny or oily and large pores are visible.
        - **If Dry**: skin feels tight or looks flaky/rough.Especially on the cheeks and forehead.
        - **If Combination**: skin is oily in the T-zone (forehead, nose, chin) and dry/normal around the cheeks.
        - **If Sensitive**: skin easily reacts with redness, stinging, or breakouts,especially after using new products. 
        """)
        
    
    st.markdown(
    '''
    <style>
    [data-testid="stExpander"] {
        background-color: #e6f0fa;        /*  Soft blue */
        border: 1px solid #bcd4ec;        /* Gentle blue edge */
        border-radius: 8px;
        color: #4a4a4a;                   /* deep gray for text */
    }

    [data-testid="stExpander"] > div:first-child {
        font-weight: bold;
    }

    [data-testid="stExpander"] svg {
        color: #5f80aa;                  
    }
    </style>
    ''',
    unsafe_allow_html=True
)


    st.markdown(
    """
    <p style='text-align: right; font-size: 0.8rem; font-style: italic; color: #4a4a4a; margin-top: 30px;'>
     A reminder to be gentle with your skin — it’s already carrying your beauty.<br>
    Products are just the polish 🌸.
    </p>
    """,
    unsafe_allow_html=True
)
