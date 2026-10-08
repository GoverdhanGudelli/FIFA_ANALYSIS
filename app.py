import os
import subprocess
import streamlit as st
import pandas as pd
import plotly.express as px


def ensure_lfs_data():
    sample_file = "data/male_teams_dashboard.csv"
    if os.path.exists(sample_file):
        try:
            with open(sample_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(100)
                if "version https://git-lfs" in content:
                    subprocess.run(["git", "lfs", "install"], check=True)
                    subprocess.run(["git", "lfs", "pull"], check=True)
        except Exception:
            pass


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FIFA Football Analytics",
    page_icon="⚽",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("⚽ FIFA Football Analytics")
st.caption(
    "Comparative Data Science Analysis of FIFA Players and Teams"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    ensure_lfs_data()

    male_players = pd.read_csv(
        "data/male_players_dashboard.csv",
        low_memory=False
    )

    female_players = pd.read_csv(
        "data/female_players_dashboard.csv",
        low_memory=False
    )

    male_teams = pd.read_csv(
        "data/male_teams_dashboard.csv",
        low_memory=False
    )

    female_teams = pd.read_csv(
        "data/female_teams_dashboard.csv",
        low_memory=False
    )

    return (
        male_players,
        female_players,
        male_teams,
        female_teams
    )


male_players, female_players, male_teams, female_teams = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Overview",
        "👤 Player Analytics",
        "🏟️ Team Analytics",
        "🔗 Player–Team Analytics",
        "🧠 Advanced Analytics",
        "⚥ Male vs Female",
        "📚 Research & Findings"
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "🏠 Overview":

    st.header("Project Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Male Player Records",
        f"{len(male_players):,}"
    )

    col2.metric(
        "Female Player Records",
        f"{len(female_players):,}"
    )

    col3.metric(
        "Male Teams",
        f"{len(male_teams):,}"
    )

    col4.metric(
        "Female Teams",
        f"{len(female_teams):,}"
    )

    st.divider()

    st.subheader("Overall Rating Distribution")

    male_plot = male_players[
        ["overall"]
    ].assign(Gender="Male")

    female_plot = female_players[
        ["overall"]
    ].assign(Gender="Female")

    distribution = pd.concat(
        [male_plot, female_plot]
    )

    fig = px.histogram(
        distribution,
        x="overall",
        color="Gender",
        barmode="overlay",
        nbins=40,
        title="FIFA Overall Rating Distribution"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.subheader("Average Player Ratings")

    comparison = pd.DataFrame({
        "Gender": ["Male", "Female"],
        "Average Overall": [
            male_players["overall"].mean(),
            female_players["overall"].mean()
        ],
        "Average Potential": [
            male_players["potential"].mean(),
            female_players["potential"].mean()
        ]
    })

    fig = px.bar(
        comparison,
        x="Gender",
        y=["Average Overall", "Average Potential"],
        barmode="group",
        title="Average Overall vs Potential"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# PLAYER ANALYTICS
# ============================================================

elif page == "👤 Player Analytics":

    st.header("Player Analytics")

    gender = st.sidebar.selectbox(
        "Player Dataset",
        ["Male", "Female"]
    )

    df = (
        male_players
        if gender == "Male"
        else female_players
    ).copy()

    # -------------------------------
    # Filters
    # -------------------------------

    if "fifa_version" in df.columns:

        versions = sorted(
            df["fifa_version"].dropna().unique()
        )

        selected_version = st.sidebar.selectbox(
            "FIFA Version",
            ["All"] + list(versions)
        )

        if selected_version != "All":
            df = df[
                df["fifa_version"] == selected_version
            ]

    if "main_position" in df.columns:

        positions = sorted(
            df["main_position"]
            .dropna()
            .unique()
        )

        selected_position = st.sidebar.selectbox(
            "Position",
            ["All"] + positions
        )

        if selected_position != "All":
            df = df[
                df["main_position"] == selected_position
            ]

    overall_min = int(df["overall"].min())
    overall_max = int(df["overall"].max())

    overall_range = st.sidebar.slider(
        "Overall Range",
        overall_min,
        overall_max,
        (overall_min, overall_max)
    )

    df = df[
        df["overall"].between(
            overall_range[0],
            overall_range[1]
        )
    ]

    # -------------------------------
    # KPI
    # -------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Players",
        f"{len(df):,}"
    )

    c2.metric(
        "Avg Overall",
        f"{df['overall'].mean():.2f}"
    )

    c3.metric(
        "Avg Potential",
        f"{df['potential'].mean():.2f}"
    )

    c4.metric(
        "Avg Age",
        f"{df['age'].mean():.1f}"
    )

    # -------------------------------
    # Overall vs Potential
    # -------------------------------

    st.subheader("Overall vs Potential")

    scatter_df = df.sample(
        min(5000, len(df)),
        random_state=42
    )

    fig = px.scatter(
        scatter_df,
        x="overall",
        y="potential",
        color="age",
        hover_name="short_name",
        hover_data=[
            c for c in [
                "club_name",
                "main_position",
                "nationality_name",
                "value_eur"
            ]
            if c in df.columns
        ],
        title="Overall vs Potential"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # -------------------------------
    # Position analysis
    # -------------------------------

    if "main_position" in df.columns:

        st.subheader("Average Overall by Position")

        position_df = (
            df
            .groupby("main_position")
            ["overall"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig = px.bar(
            position_df,
            x="main_position",
            y="overall",
            title="Average Overall by Position"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # -------------------------------
    # Player table
    # -------------------------------

    st.subheader("Top Players")

    display_cols = [
        c for c in [
            "short_name",
            "club_name",
            "main_position",
            "overall",
            "potential",
            "age",
            "value_eur"
        ]
        if c in df.columns
    ]

    st.dataframe(
        df
        .sort_values("overall", ascending=False)
        [display_cols]
        .head(50),
        width="stretch"
    )


# ============================================================
# TEAM ANALYTICS
# ============================================================

elif page == "🏟️ Team Analytics":

    st.header("Team Analytics")

    gender = st.sidebar.selectbox(
        "Team Dataset",
        ["Male", "Female"]
    )

    df = (
        male_teams
        if gender == "Male"
        else female_teams
    ).copy()

    if "league_name" in df.columns:

        leagues = sorted(
            df["league_name"]
            .dropna()
            .unique()
        )

        selected_league = st.sidebar.selectbox(
            "League",
            ["All"] + list(leagues)
        )

        if selected_league != "All":
            df = df[
                df["league_name"] == selected_league
            ]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Teams",
        f"{len(df):,}"
    )

    if "overall" in df.columns:
        c2.metric(
            "Avg Overall",
            f"{df['overall'].mean():.2f}"
        )

    if "attack" in df.columns:
        c3.metric(
            "Avg Attack",
            f"{df['attack'].mean():.2f}"
        )

    if "defence" in df.columns:
        c4.metric(
            "Avg Defence",
            f"{df['defence'].mean():.2f}"
        )

    # Top teams

    if "overall" in df.columns:

        st.subheader("Top Teams")

        top_teams = (
            df
            .sort_values("overall", ascending=False)
            .head(20)
            .sort_values("overall")
        )

        fig = px.bar(
            top_teams,
            x="overall",
            y="team_name",
            orientation="h",
            title="Top Teams by Overall"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # Attack / Midfield / Defence

    attributes = [
        c for c in [
            "attack",
            "midfield",
            "defence"
        ]
        if c in df.columns
    ]

    if attributes and "overall" in df.columns:

        st.subheader(
            "Team Attributes vs Overall"
        )

        for attribute in attributes:

            fig = px.scatter(
                df,
                x=attribute,
                y="overall",
                hover_name="team_name",
                title=f"{attribute.title()} vs Overall"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


# ============================================================
# PLAYER–TEAM ANALYTICS
# ============================================================

elif page == "🔗 Player–Team Analytics":

    st.header("Player → Team Analytics")

    st.info(
        "This page connects player-level squad features "
        "with team-level FIFA ratings."
    )

    try:

        squad = pd.read_csv(
            "data/male_squad_features.csv"
        )

        teams = male_teams.copy()

        if "team_id" in teams.columns:

            team_options = (
                teams["team_name"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_team = st.selectbox(
                "Select Team",
                sorted(team_options)
            )

            team_row = teams[
                teams["team_name"] == selected_team
            ].sort_values(
                "fifa_version"
                if "fifa_version" in teams.columns
                else "team_id"
            ).tail(1)

            if not team_row.empty:

                team_id = team_row.iloc[0]["team_id"]

                squad_row = squad[
                    squad["club_team_id"] == team_id
                ]

                if not squad_row.empty:

                    row = squad_row.iloc[0]

                    c1, c2, c3, c4 = st.columns(4)

                    c1.metric(
                        "Squad Size",
                        int(row["squad_size"])
                    )

                    c2.metric(
                        "Avg Player Overall",
                        f"{row['avg_player_overall']:.1f}"
                    )

                    c3.metric(
                        "Avg Potential",
                        f"{row['avg_player_potential']:.1f}"
                    )

                    c4.metric(
                        "Top Player",
                        f"{row['max_player_overall']:.0f}"
                    )

                    st.subheader(
                        "Team Rating"
                    )

                    if "overall" in team_row.columns:
                        st.metric(
                            "Team Overall",
                            f"{team_row.iloc[0]['overall']:.1f}"
                        )

                    st.dataframe(
                        team_row,
                        width="stretch"
                    )

                else:
                    st.warning(
                        "No squad-level record was found for this team."
                    )

    except FileNotFoundError:

        st.warning(
            "Player-team feature file is not available. "
            "Run the dashboard export section in the notebook first."
        )


# ============================================================
# ADVANCED ANALYTICS
# ============================================================

elif page == "🧠 Advanced Analytics":

    st.header("Advanced Analytics")

    tab1, tab2, tab3 = st.tabs(
        [
            "PCA",
            "Regression",
            "Clustering"
        ]
    )

    with tab1:

        st.subheader(
            "Principal Component Analysis"
        )

        st.info(
            "PCA results should be exported from the notebook "
            "and displayed here as an interactive visualization."
        )

        st.write(
            "Use this section to show explained variance, "
            "component loadings and the 2D PCA projection."
        )

    with tab2:

        st.subheader(
            "Regression Model Evaluation"
        )

        st.info(
            "Display Linear, Ridge and Lasso model metrics here."
        )

    with tab3:

        st.subheader(
            "K-Means Player Profiles"
        )

        st.info(
            "Display cluster profiles, elbow analysis "
            "and PCA-based cluster visualization here."
        )


# ============================================================
# MALE VS FEMALE
# ============================================================

elif page == "⚥ Male vs Female":

    st.header(
        "Male vs Female FIFA Dataset Comparison"
    )

    metrics = [
        "overall",
        "potential",
        "age",
        "pace",
        "shooting",
        "passing",
        "dribbling",
        "defending",
        "physic"
    ]

    metrics = [
        c for c in metrics
        if c in male_players.columns
        and c in female_players.columns
    ]

    comparison = pd.DataFrame({
        "Metric": metrics,
        "Male": [
            male_players[c].mean()
            for c in metrics
        ],
        "Female": [
            female_players[c].mean()
            for c in metrics
        ]
    })

    comparison["Male"] = comparison["Male"].round(2)
    comparison["Female"] = comparison["Female"].round(2)

    st.dataframe(
        comparison,
        width="stretch"
    )

    fig = px.bar(
        comparison,
        x="Metric",
        y=["Male", "Female"],
        barmode="group",
        title="Male vs Female FIFA Player Ratings"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.warning(
        "This is a descriptive comparison of FIFA datasets "
        "and should not be interpreted as a direct measure "
        "of real-world male/female football performance."
    )


# ============================================================
# RESEARCH
# ============================================================

elif page == "📚 Research & Findings":

    st.header(
        "Research Questions & Literature"
    )

    st.subheader(
        "RQ1 — Player Attributes"
    )

    st.write(
        "Which player attributes are most strongly "
        "associated with FIFA Overall?"
    )

    st.subheader(
        "RQ2 — Player Potential"
    )

    st.write(
        "Which young players have the largest "
        "Potential − Overall gap?"
    )

    st.subheader(
        "RQ3 — Player Value"
    )

    st.write(
        "Which player characteristics are associated "
        "with FIFA Player Value?"
    )

    st.subheader(
        "RQ4 — Team Strength"
    )

    st.write(
        "Which team characteristics are associated "
        "with FIFA Team Overall?"
    )

    st.subheader(
        "RQ5 — Player–Team Relationship"
    )

    st.write(
        "Does aggregate squad composition correspond "
        "to team-level FIFA ratings?"
    )

    st.subheader(
        "Research References"
    )

    st.markdown("""
    **1. Wakelam et al. (2022)**  
    Footballer attributes and sports analytics.

    **2. Vroonen et al. (2017)**  
    Predicting professional soccer player potential.

    **3. Al-Asadi & Taşdemir (2022)**  
    FIFA video-game data and player value prediction.

    **4. Felipe et al. (2020)**  
    Team variables, player positions, age and footballer value.
    """)
   

    st.markdown("---")

    st.header("Final Numerical Findings")

    # --- Key Metrics ---
    st.subheader("Dataset Scope & Key Averages")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Male Players", value="161,583")
        st.caption("Unique Players: 49,699")

    with col2:
        st.metric(label="Female Players", value="3,196")
        st.caption("Unique Players: 1,266")

    with col3:
        st.metric(label="Male Mean Overall", value="65.70")
        st.caption("Mean Potential: 70.74")

    with col4:
        st.metric(label="Female Mean Overall", value="75.95")
        st.caption("Mean Potential: 79.57")

    st.markdown("---")

    # --- Correlations ---
    st.subheader("Key Correlations")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(label="Overall ↔ Potential", value="0.695")

    with c2:
        st.metric(label="Overall ↔ Player Value", value="0.567")

    with c3:
        st.metric(label="Potential ↔ Player Value", value="0.534")

    # Top Major Attribute Correlations Table
    st.markdown("**Top Major Attribute Correlations with Overall Rating:**")
    major_corr_data = pd.DataFrame(
        {
            "Attribute": [
                "Passing",
                "Dribbling",
                "Physic",
                "Shooting",
                "Defending",
            ],
            "Correlation": [0.681, 0.607, 0.513, 0.482, 0.325],
        }
    )
    st.dataframe(major_corr_data, width="stretch", hide_index=True)

    st.markdown("---")

    # --- Best Regression Model ---
    st.subheader("Best Performing Regression Model")
    st.markdown("**Linear Regression (Overall Prediction)**")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MAE", "2.0426")
    m2.metric("MSE", "6.7444")
    m3.metric("RMSE", "2.5970")
    m4.metric("R² Score", "0.8596")

    st.markdown("---")

    # --- Top Future Star Candidates ---
    st.subheader("Top Future Star Candidates (Highest Potential Gap)")
    future_stars_df = pd.DataFrame(
        [
            {
                "Name": "C. Burton",
                "Age": 17,
                "Overall": 50,
                "Potential": 78,
                "Gap": 28,
                "Club": "Shrewsbury Town",
                "Position": "GK",
            },
            {
                "Name": "A. Gomes",
                "Age": 16,
                "Overall": 63,
                "Potential": 89,
                "Gap": 26,
                "Club": "Manchester United",
                "Position": "CAM",
            },
            {
                "Name": "B. Arrey-Mbi",
                "Age": 17,
                "Overall": 60,
                "Potential": 86,
                "Gap": 26,
                "Club": "FC Bayern München II",
                "Position": "CB",
            },
            {
                "Name": "M. Edwards",
                "Age": 17,
                "Overall": 58,
                "Potential": 84,
                "Gap": 26,
                "Club": "Tottenham Hotspur",
                "Position": "CAM",
            },
            {
                "Name": "C. Gregory",
                "Age": 17,
                "Overall": 54,
                "Potential": 80,
                "Gap": 26,
                "Club": "Shrewsbury Town",
                "Position": "GK",
            },
        ]
    )

    st.dataframe(future_stars_df, width="stretch", hide_index=True)